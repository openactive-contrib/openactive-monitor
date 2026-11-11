"""Fetch helpers for official OpenActive JSON-LD documents.

Shared by the taxonomy adherence report (``main.py`` in this folder) and the
custom-property analysis (``custom_properties.py``) that runs as part of the
``opportunity-insights`` job.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)

ACTIVITY_LIST_URL = "https://openactive.io/activity-list/activity-list.jsonld"
FACILITY_LIST_URL = "https://openactive.io/facility-types/facility-types.jsonld"
ACTIVITY_LIST_NAMESPACE = "https://openactive.io/activity-list"
FACILITY_LIST_NAMESPACE = "https://openactive.io/facility-types"
OA_CONTEXT_URL = "https://openactive.io/ns/oa.jsonld"
BETA_CONTEXT_URL = "https://openactive.io/ns-beta/beta.jsonld"


def fetch_jsonld(url: str, timeout: int = 30) -> dict[str, Any] | None:
    """Fetch and parse a JSON-LD document, returning ``None`` on any failure."""
    try:
        logger.info("Fetching JSON-LD from %s", url)
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error("Failed to fetch JSON-LD from %s: %s", url, e)
        return None
    if not isinstance(data, dict):
        logger.error("Unexpected JSON-LD shape from %s: %s", url, type(data).__name__)
        return None
    return data


def fetch_taxonomy(url: str) -> set[str]:
    """Fetch and extract taxonomy terms from a JSON-LD file (case-insensitive)."""
    data = fetch_jsonld(url)
    if data is None:
        return set()

    terms = set()

    # Try "concept" array (OpenActive format)
    if "concept" in data and isinstance(data["concept"], list):
        for item in data["concept"]:
            if "prefLabel" in item:
                label = item["prefLabel"]
                if isinstance(label, str):
                    terms.add(label.lower())

    # Fallback to @graph format
    elif "@graph" in data and isinstance(data["@graph"], list):
        for item in data["@graph"]:
            if "prefLabel" in item:
                label = item["prefLabel"]
                if isinstance(label, str):
                    terms.add(label.lower())
                elif isinstance(label, dict):
                    for lang, value in label.items():
                        if isinstance(value, str):
                            terms.add(value.lower())
            elif "name" in item:
                name = item["name"]
                if isinstance(name, str):
                    terms.add(name.lower())

    logger.info("Fetched %d terms from taxonomy", len(terms))
    return terms


def fetch_vocabulary_terms(url: str) -> set[str]:
    """Return the property/class terms defined by a JSON-LD vocabulary (case-sensitive).

    Collects the keys of ``@context`` (a dict, or a list whose dict entries are
    merged) plus the ``@id`` of every ``@graph`` item — e.g. ``facilityType``
    from ``oa.jsonld`` or ``beta:formattedDescription`` from ``beta.jsonld``.
    """
    data = fetch_jsonld(url)
    if data is None:
        return set()

    terms: set[str] = set()

    context = data.get("@context")
    contexts = context if isinstance(context, list) else [context]
    for ctx in contexts:
        if isinstance(ctx, dict):
            terms.update(k for k in ctx if isinstance(k, str))

    graph = data.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            if isinstance(item, dict) and isinstance(item.get("@id"), str):
                terms.add(item["@id"])

    logger.info("Fetched %d vocabulary terms from %s", len(terms), url)
    return terms


# ---------------------------------------------------------------------------
# SKOS concept schemes (activity list / facility types)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConceptScheme:
    """Lookup sets for one OpenActive SKOS concept scheme.

    ``ids`` are normalised with :func:`normalise_concept_id`; ``labels`` are the
    lower-cased ``prefLabel`` and ``altLabel`` values of every concept.
    """

    scheme_url: str
    namespace: str
    ids: frozenset[str]
    labels: frozenset[str]


_SCHEME_SLASH_HASH = re.compile(r"/#")


def normalise_concept_id(raw: str) -> str:
    """Canonicalise a concept URI so publisher variants compare equal.

    Handles the variants seen in the wild: surrounding whitespace, ``http://``
    instead of ``https://``, a ``www.`` host prefix, ``/activity-list/#uuid``
    instead of ``/activity-list#uuid``, trailing slashes, and upper-case UUID
    fragments.
    """
    value = raw.strip()
    lowered = value.lower()
    if lowered.startswith("http://"):
        value = "https://" + value[len("http://"):]
    elif lowered.startswith("https://"):
        value = "https://" + value[len("https://"):]
    if value.lower().startswith("https://www."):
        value = "https://" + value[len("https://www."):]
    value = _SCHEME_SLASH_HASH.sub("#", value, count=1)
    base, sep, fragment = value.partition("#")
    base = base.rstrip("/")
    return f"{base.lower()}{sep}{fragment.strip().lower()}" if sep else base.lower()


def _iter_labels(value: Any) -> list[str]:
    """Flatten a SKOS label value (str, list of str, or language map) to strings."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    if isinstance(value, dict):
        return [v for v in value.values() if isinstance(v, str)]
    return []


def build_concept_scheme(data: dict[str, Any], scheme_url: str, namespace: str) -> ConceptScheme:
    """Build a :class:`ConceptScheme` from a parsed SKOS JSON-LD document."""
    concepts = data.get("concept")
    if not isinstance(concepts, list):
        concepts = data.get("@graph") if isinstance(data.get("@graph"), list) else []

    ids: set[str] = set()
    labels: set[str] = set()
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        concept_id = concept.get("id") or concept.get("@id")
        if isinstance(concept_id, str) and concept_id.strip():
            ids.add(normalise_concept_id(concept_id))
        for key in ("prefLabel", "altLabel"):
            for label in _iter_labels(concept.get(key)):
                if label.strip():
                    labels.add(label.strip().lower())

    return ConceptScheme(
        scheme_url=scheme_url,
        namespace=normalise_concept_id(namespace),
        ids=frozenset(ids),
        labels=frozenset(labels),
    )


def fetch_concept_scheme(url: str, namespace: str) -> ConceptScheme | None:
    """Fetch a SKOS concept scheme; ``None`` if the fetch fails or it has no concepts."""
    data = fetch_jsonld(url)
    if data is None:
        return None
    scheme = build_concept_scheme(data, url, namespace)
    if not scheme.ids:
        logger.error("No concepts found in concept scheme %s", url)
        return None
    logger.info(
        "Loaded concept scheme %s: %d concept ids, %d labels",
        url, len(scheme.ids), len(scheme.labels),
    )
    return scheme


__all__ = [
    "ACTIVITY_LIST_URL",
    "ACTIVITY_LIST_NAMESPACE",
    "FACILITY_LIST_URL",
    "FACILITY_LIST_NAMESPACE",
    "ConceptScheme",
    "build_concept_scheme",
    "fetch_concept_scheme",
    "normalise_concept_id",
    "OA_CONTEXT_URL",
    "BETA_CONTEXT_URL",
    "fetch_jsonld",
    "fetch_taxonomy",
    "fetch_vocabulary_terms",
]
