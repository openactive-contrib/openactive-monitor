"""Adapter over ``field_usage.model_spec`` for field-usage analysis.

``model_spec`` owns the canonical OpenActive data-model field catalog
(``VERSION_SPECS``) keyed by spec category (``Event``, ``FacilityUse``,
``Slot``, ``Organization``, ``Place``, ``Offer``, …) and spec version. This
adapter resolves, per category, the ``{field: status}`` catalog for a chosen
version, maps an observed ``@type`` / feed ``kind`` to a spec category, and
tells which observed types are model entities versus discovered-only nested
sub-entities.
"""

from __future__ import annotations

from field_usage.model_spec import (
    FEED_TYPE_TO_SPEC_CATEGORY,
    VERSION_ORDER,
    VERSION_SPECS,
    get_alternatives,
)

# The four top-level spec categories that have a model field catalog.
SPEC_CATEGORIES: list[str] = list(VERSION_SPECS.keys())

# Spec versions that actually have a field catalog (across all categories),
# ordered oldest → newest. Excludes the synthetic ``V0.x`` detection bucket.
AVAILABLE_VERSIONS: list[str] = sorted(
    {v for spec in VERSION_SPECS.values() for v in spec},
    key=lambda v: VERSION_ORDER.get(v, -1),
)

# Default data-model version used for the analysis.
DEFAULT_MODEL_VERSION: str = "V2.0"


def resolve_version_for_category(category: str, version: str) -> str:
    """Return the version spec to use for ``category``.

    Not every category defines every version (e.g. ``RouteGuide`` only has
    ``V1.0``, ``FacilityUse``/``Slot`` start at ``V2.0``). When the requested
    ``version`` is absent for a category we fall back to the newest available
    version that does not exceed it; if none qualifies, the oldest available.
    """
    specs = VERSION_SPECS.get(category, {})
    if version in specs:
        return version
    req_rank = VERSION_ORDER.get(version, -1)
    ranked = sorted((VERSION_ORDER.get(v, -1), v) for v in specs)
    at_or_below = [pair for pair in ranked if pair[0] <= req_rank]
    if at_or_below:
        return at_or_below[-1][1]
    return ranked[0][1] if ranked else version


def model_fields_for_category(
    category: str, version: str = DEFAULT_MODEL_VERSION
) -> dict[str, str]:
    """Return the ``{field: status}`` catalog for ``category`` at ``version``.

    Status (``required`` / ``recommended`` / ``optional``) is taken directly
    from the resolved version's spec — not collapsed across versions — so the
    analysis reflects a single chosen edition of the OpenActive model.
    """
    resolved = resolve_version_for_category(category, version)
    return dict(VERSION_SPECS.get(category, {}).get(resolved, {}))


def spec_category_for_kind(kind: str | None) -> str:
    """Map a feed ``kind`` / observed ``@type`` to its spec category.

    Defaults to ``Event`` (the largest family) when unknown.
    """
    if not kind:
        return "Event"
    return FEED_TYPE_TO_SPEC_CATEGORY.get(kind.strip(), "Event")


def is_model_type(type_str: str | None) -> bool:
    """True if ``type_str`` maps to one of the four model spec categories.

    A type is a *model* entity when ``FEED_TYPE_TO_SPEC_CATEGORY`` knows it
    explicitly. Nested sub-entities (Place, Organization, Offer, ...) are not in
    that mapping and are therefore *discovered-only*.
    """
    if not type_str:
        return False
    return type_str.strip() in FEED_TYPE_TO_SPEC_CATEGORY


def field_is_present(
    category: str,
    field: str,
    observed_fields: set[str],
) -> bool:
    """True if ``field`` (or one of its alternatives) appears in ``observed_fields``.

    Mirrors the alternative-field handling in
    ``version_compliance.score_item_against_version`` so a bare ``type`` / ``id``
    satisfies ``@type`` / ``@id`` and ``facilityType`` satisfies
    ``FacilityUse.activity``.
    """
    if field in observed_fields:
        return True
    return any(alt in observed_fields for alt in get_alternatives(category, field))


__all__ = [
    "SPEC_CATEGORIES",
    "AVAILABLE_VERSIONS",
    "DEFAULT_MODEL_VERSION",
    "resolve_version_for_category",
    "model_fields_for_category",
    "spec_category_for_kind",
    "is_model_type",
    "field_is_present",
]
