"""Fetch helpers for official OpenActive JSON-LD documents.

Shared by the taxonomy adherence report (``main.py`` in this folder) and the
custom-property analysis (``custom_properties.py``) that runs as part of the
``opportunity-insights`` job.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

ACTIVITY_LIST_URL = "https://openactive.io/activity-list/activity-list.jsonld"
FACILITY_LIST_URL = "https://openactive.io/facility-types/facility-types.jsonld"
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


__all__ = [
    "ACTIVITY_LIST_URL",
    "FACILITY_LIST_URL",
    "OA_CONTEXT_URL",
    "BETA_CONTEXT_URL",
    "fetch_jsonld",
    "fetch_taxonomy",
    "fetch_vocabulary_terms",
]
