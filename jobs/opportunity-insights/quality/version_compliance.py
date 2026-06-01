"""Feed version detection and compliance scoring.

Detects which OpenActive spec version a feed conforms to (V0.x, V1.1, V2.0, V2.1)
and computes a numeric quality score based on the presence/absence of required,
recommended, and optional properties.

Scoring weights:
  - Required property present:      +3
  - Required property missing:      -3
  - Recommended property present:   +2
  - Recommended property missing:   -1
  - Optional property present:      +1
  - Optional property missing:       0

Version specifications derived from the OpenActive specs:
  V2.0: https://openactive.io/modelling-opportunity-data/
  V2.1: https://openactive.io/modelling-opportunity-data/EditorsDraft/
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Version specifications per feed type
# ---------------------------------------------------------------------------

VERSION_SPECS: dict[str, dict[str, dict[str, str]]] = {
    # --- Event ---
    "Event": {
        "V1.0": {
            "@id": "required", "url": "required", "identifier": "optional",
            "name": "required", "description": "recommended", "image": "optional",
            "startDate": "optional", "endDate": "optional", "duration": "recommended",
            "location": "required", "organizer": "recommended", "contributor": "recommended",
            "maximumAttendeeCapacity": "optional", "remainingAttendeeCapacity": "optional",
            "eventStatus": "recommended", "subEvent": "optional", "superEvent": "optional",
            "schedule": "optional", "activity": "required", "category": "recommended",
            "ageRange": "optional", "genderRestriction": "optional", "programme": "optional",
            "attendeeInstructions": "optional", "leader": "optional",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "isCoached": "optional", "level": "optional", "meetingPoint": "optional",
        },
        "V1.1": {
            "@id": "required", "url": "required", "identifier": "optional",
            "name": "required", "description": "recommended", "image": "optional",
            "startDate": "optional", "endDate": "optional", "duration": "recommended",
            "location": "required", "organizer": "recommended", "contributor": "recommended",
            "maximumAttendeeCapacity": "optional", "remainingAttendeeCapacity": "optional",
            "eventStatus": "recommended", "subEvent": "optional", "superEvent": "optional",
            "schedule": "optional", "activity": "required", "category": "recommended",
            "ageRange": "optional", "genderRestriction": "optional", "programme": "optional",
            "attendeeInstructions": "optional", "leader": "optional",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "isCoached": "optional", "level": "optional", "meetingPoint": "optional",
        },
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "required",
            "identifier": "optional", "name": "required", "description": "recommended",
            "image": "optional", "startDate": "recommended", "endDate": "recommended",
            "duration": "recommended", "location": "required", "organizer": "required",
            "contributor": "recommended", "maximumAttendeeCapacity": "recommended",
            "remainingAttendeeCapacity": "recommended", "eventStatus": "recommended",
            "subEvent": "optional", "superEvent": "optional", "eventSchedule": "optional",
            "schedulingNote": "optional", "activity": "required", "category": "optional",
            "ageRange": "recommended", "genderRestriction": "optional", "programme": "optional",
            "attendeeInstructions": "optional", "leader": "optional",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "isCoached": "optional", "level": "recommended", "meetingPoint": "optional",
            "isAccessibleForFree": "optional", "offers": "recommended",
            "potentialAction": "optional",
        },
        "V2.1": {
            "@type": "required", "@id": "recommended", "url": "required",
            "identifier": "optional", "name": "required", "description": "recommended",
            "image": "optional", "startDate": "recommended", "endDate": "recommended",
            "duration": "recommended", "location": "required", "organizer": "required",
            "contributor": "recommended", "maximumAttendeeCapacity": "recommended",
            "remainingAttendeeCapacity": "recommended", "eventStatus": "recommended",
            "subEvent": "optional", "superEvent": "optional", "eventSchedule": "optional",
            "schedulingNote": "optional", "activity": "required", "category": "optional",
            "ageRange": "recommended", "genderRestriction": "optional", "programme": "optional",
            "attendeeInstructions": "optional", "leader": "optional",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "isCoached": "optional", "level": "recommended", "meetingPoint": "optional",
            "isAccessibleForFree": "optional", "offers": "recommended",
            "potentialAction": "optional", "routeGuide": "optional",
        },
    },
    # --- FacilityUse (oa:FacilityUse / oa:IndividualFacilityUse) — V2.0+ only ---
    "FacilityUse": {
        "V2.0": {
            "@type": "required", "@id": "required", "url": "required",
            "identifier": "optional", "name": "required", "description": "recommended",
            "provider": "required", "image": "recommended",
            "activity": "required", "location": "required",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "attendeeInstructions": "optional", "category": "optional",
            "event": "recommended", "offers": "optional",
            "hoursAvailable": "optional", "individualFacilityUse": "optional",
            "aggregateFacilityUse": "optional", "potentialAction": "optional",
        },
        "V2.1": {
            "@type": "required", "@id": "required", "url": "required",
            "identifier": "optional", "name": "required", "description": "recommended",
            "provider": "required", "image": "recommended",
            "activity": "required", "location": "required",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "attendeeInstructions": "optional", "category": "optional",
            "event": "recommended", "offers": "optional",
            "hoursAvailable": "optional", "individualFacilityUse": "optional",
            "aggregateFacilityUse": "optional", "potentialAction": "optional",
        },
    },
    # --- Slot (oa:Slot) — V2.0+ only ---
    "Slot": {
        "V2.0": {
            "@type": "required", "@id": "recommended",
            "identifier": "optional", "facilityUse": "required",
            "startDate": "required", "endDate": "optional",
            "duration": "required", "offers": "recommended",
            "remainingUses": "required", "maximumUses": "recommended",
        },
        "V2.1": {
            "@type": "required", "@id": "recommended",
            "identifier": "optional", "facilityUse": "required",
            "startDate": "required", "endDate": "optional",
            "duration": "required", "offers": "recommended",
            "remainingUses": "required", "maximumUses": "recommended",
        },
    },
    # --- RouteGuide (rt:RouteGuide) — Route Guide Specification 1.0 ---
    "RouteGuide": {
        "V1.0": {
            "@type": "required", "@id": "required",
            "name": "required", "description": "required",
            "url": "optional", "author": "optional",
            "datePublished": "recommended", "dateModified": "recommended",
            "activity": "required", "distance": "required",
            "startPoint": "required", "endPoint": "optional",
            "headline": "optional",
            "indicativeDuration": "recommended",
            "accessibilityDescription": "recommended",
            "gradient": "recommended", "surface": "recommended",
            "geoPath": "recommended", "mapImage": "optional",
            "routeDifficulty": "optional", "category": "optional",
            "amenityFeature": "recommended",
            "isLoop": "optional", "isMaintained": "optional",
            "riskInformation": "recommended", "legalAdvisory": "recommended",
            "contactPoint": "recommended",
            "isBasedOn": "recommended",
            "image": "optional", "review": "optional",
            "suggestedEquipment": "optional",
            "segments": "optional", "segmentGroups": "optional",
        },
    },
}

# Mapping from feed_type strings to spec categories.
FEED_TYPE_TO_SPEC_CATEGORY: dict[str, str] = {
    "Event": "Event",
    "SessionSeries": "Event",
    "ScheduledSession": "Event",
    "ScheduledSessions": "Event",
    "CourseInstance": "Event",
    "EventSeries": "Event",
    "HeadlineEvent": "Event",
    "OnDemandEvent": "Event",
    "FacilityUse": "FacilityUse",
    "IndividualFacilityUse": "FacilityUse",
    "FacilityUse/Slot": "Slot",
    "Slot for FacilityUse": "Slot",
    "Slot": "Slot",
    "RouteGuide": "RouteGuide",
}

# Properties that exist ONLY in V2.0+ (for Event feeds):
V2_ONLY_PROPERTIES = {"eventSchedule", "schedulingNote", "isAccessibleForFree", "offers", "potentialAction"}

# Property that exists ONLY in V2.1 (for Event feeds):
V21_ONLY_PROPERTIES = {"routeGuide"}

# Minimum % of required properties that must be present to award V1.1 (rather than V0.x)
V1_REQUIRED_THRESHOLD = 50.0

# For strict version: each required property must be present in at least this % of sampled items
STRICT_REQUIRED_THRESHOLD = 95.0

# Alternative fields: for some spec categories a required property can be satisfied by an alternative.
ALTERNATIVE_FIELDS: dict[tuple[str, str], list[str]] = {
    ("FacilityUse", "activity"): ["facilityType"],
}

# Global alternative fields applied across all spec categories. Some feeds use
# the unprefixed schema.org keys (``type``, ``id``) instead of the JSON-LD
# keys (``@type``, ``@id``); both should be treated as satisfying the requirement.
GLOBAL_ALTERNATIVE_FIELDS: dict[str, list[str]] = {
    "@type": ["type"],
    "@id": ["id"],
}


def get_alternatives(spec_category: str, prop: str) -> list[str]:
    """Return the list of alternative field names that satisfy ``prop`` for ``spec_category``.

    Combines category-specific alternatives from ``ALTERNATIVE_FIELDS`` with
    universal aliases from ``GLOBAL_ALTERNATIVE_FIELDS``.
    """
    return (
        ALTERNATIVE_FIELDS.get((spec_category, prop), [])
        + GLOBAL_ALTERNATIVE_FIELDS.get(prop, [])
    )

# Canonical ordering of versions for comparisons (higher = newer)
VERSION_ORDER: dict[str, int] = {"V0.x": 0, "V1.0": 1, "V1.1": 2, "V2.0": 3, "V2.1": 4}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_item_against_version(
    item_data: dict[str, Any],
    version_spec: dict[str, str],
    spec_category: str = "Event",
) -> dict[str, int]:
    """Score how well a single item's properties match a version spec.

    Returns dict with: score, required_present, required_total,
    recommended_present, recommended_total.
    """
    score = 0
    required_present = 0
    required_total = 0
    recommended_present = 0
    recommended_total = 0

    item_keys = set(item_data.keys()) - {"@context"}

    for prop, status in version_spec.items():
        present = prop in item_keys
        if not present:
            alts = get_alternatives(spec_category, prop)
            present = any(alt in item_keys for alt in alts)
        if status == "required":
            required_total += 1
            if present:
                score += 3
                required_present += 1
            else:
                score -= 3
        elif status == "recommended":
            recommended_total += 1
            if present:
                score += 2
                recommended_present += 1
            else:
                score -= 1
        elif status == "optional":
            if present:
                score += 1

    return {
        "score": score,
        "required_present": required_present,
        "required_total": required_total,
        "recommended_present": recommended_present,
        "recommended_total": recommended_total,
    }


# ---------------------------------------------------------------------------
# Version detection
# ---------------------------------------------------------------------------

def _get_spec_category(feed_type_str: str) -> str:
    """Map a feed_type string to the spec category."""
    if not feed_type_str:
        return "Event"
    return FEED_TYPE_TO_SPEC_CATEGORY.get(feed_type_str.strip(), "Event")


def _detect_item_type(items_data_list: list[dict[str, Any]]) -> str:
    """Infer spec category from the @type field of sampled items."""
    type_counts: Counter[str] = Counter()
    for item in items_data_list:
        t = item.get("@type") or item.get("type") or ""
        if isinstance(t, list):
            t = t[0] if t else ""
        type_counts[t] += 1
    if not type_counts:
        return "Event"
    most_common = type_counts.most_common(1)[0][0]
    return FEED_TYPE_TO_SPEC_CATEGORY.get(most_common, "Event")


def _get_versions_for_category(spec_category: str) -> dict[str, dict[str, str]]:
    """Return the dict of {version: spec} for a given spec category."""
    return VERSION_SPECS.get(spec_category, VERSION_SPECS["Event"])


def detect_feed_version(
    items_data_list: list[dict[str, Any]],
    feed_type_str: str = "",
) -> dict[str, Any]:
    """Detect the best-matching spec version for a list of item data dicts.

    Returns a dict with:
      - 'version': str, e.g. 'V2.0'
      - 'spec_category': str, e.g. 'FacilityUse'
      - 'scores': {version: avg_score}
      - 'required_pct': {version: % of required props present}
      - 'recommended_pct': {version: % of recommended props present}
      - 'has_v2_only_properties': bool
      - 'has_v21_only_properties': bool
    """
    if not items_data_list:
        return {
            "version": "Unknown",
            "spec_category": "Event",
            "scores": {},
            "required_pct": {},
            "recommended_pct": {},
            "has_v2_only_properties": False,
            "has_v21_only_properties": False,
        }

    # Determine spec category from feed type string and item data
    spec_category = _get_spec_category(feed_type_str)
    if spec_category == "Event":
        detected_cat = _detect_item_type(items_data_list)
        if detected_cat != "Event":
            spec_category = detected_cat

    version_specs = _get_versions_for_category(spec_category)

    version_totals = {v: {"score": 0, "req_p": 0, "req_t": 0, "rec_p": 0, "rec_t": 0} for v in version_specs}
    n = len(items_data_list)

    # Check presence of version-distinguishing properties across all sampled items
    all_keys: set[str] = set()
    for item_data in items_data_list:
        all_keys.update(item_data.keys())

    has_v2_only = bool(all_keys & V2_ONLY_PROPERTIES)
    has_v21_only = bool(all_keys & V21_ONLY_PROPERTIES)

    for item_data in items_data_list:
        for version, spec in version_specs.items():
            result = score_item_against_version(item_data, spec, spec_category=spec_category)
            version_totals[version]["score"] += result["score"]
            version_totals[version]["req_p"] += result["required_present"]
            version_totals[version]["req_t"] += result["required_total"]
            version_totals[version]["rec_p"] += result["recommended_present"]
            version_totals[version]["rec_t"] += result["recommended_total"]

    scores: dict[str, float] = {}
    required_pct: dict[str, float] = {}
    recommended_pct: dict[str, float] = {}
    for v, totals in version_totals.items():
        scores[v] = totals["score"] / n
        required_pct[v] = (totals["req_p"] / totals["req_t"] * 100) if totals["req_t"] > 0 else 0
        recommended_pct[v] = (totals["rec_p"] / totals["rec_t"] * 100) if totals["rec_t"] > 0 else 0

    # Primary: pick the version with the highest average score
    best_version = max(scores, key=scores.get)  # type: ignore[arg-type]

    # For Event feeds only: apply structural disambiguation
    if spec_category == "Event":
        if has_v2_only and best_version.startswith("V1"):
            v2_scores = {v: s for v, s in scores.items() if v.startswith("V2")}
            if v2_scores:
                best_version = max(v2_scores, key=lambda v: scores[v])

        if has_v21_only:
            best_version = "V2.1"

        # V1.0 and V1.1 are structurally identical; default to V1.1
        if best_version == "V1.0":
            best_version = "V1.1"

        # If V1.x and below required threshold, downgrade to V0.x
        if best_version in ("V1.0", "V1.1") and required_pct.get(best_version, 0) < V1_REQUIRED_THRESHOLD:
            best_version = "V0.x"

    return {
        "version": best_version,
        "spec_category": spec_category,
        "scores": scores,
        "required_pct": required_pct,
        "recommended_pct": recommended_pct,
        "has_v2_only_properties": has_v2_only,
        "has_v21_only_properties": has_v21_only,
    }


def compute_feed_score(
    items_data_list: list[dict[str, Any]],
    feed_type_str: str = "",
) -> dict[str, Any]:
    """Compute a normalised quality score (0–100) and detect the feed version.

    The score is derived from the best-matching version spec:
      score = (average_item_score - min_possible) / (max_possible - min_possible) * 100

    Returns dict with:
      - 'version': detected version string
      - 'spec_category': spec category
      - 'score': float 0–100 (normalised quality score)
      - 'required_pct': % of required fields present for detected version
      - 'recommended_pct': % of recommended fields present for detected version
    """
    detection = detect_feed_version(items_data_list, feed_type_str=feed_type_str)

    if detection["version"] == "Unknown" or not detection["scores"]:
        return {
            "version": "Unknown",
            "spec_category": detection["spec_category"],
            "score": None,
            "required_pct": None,
            "recommended_pct": None,
        }

    best_version = detection["version"]
    spec_category = detection["spec_category"]
    version_specs = _get_versions_for_category(spec_category)
    spec = version_specs.get(best_version)

    if not spec:
        return {
            "version": best_version,
            "spec_category": spec_category,
            "score": None,
            "required_pct": detection["required_pct"].get(best_version),
            "recommended_pct": detection["recommended_pct"].get(best_version),
        }

    # Compute min/max possible scores for the detected version spec
    max_score = 0
    min_score = 0
    for status in spec.values():
        if status == "required":
            max_score += 3
            min_score -= 3
        elif status == "recommended":
            max_score += 2
            min_score -= 1
        elif status == "optional":
            max_score += 1
            # min for optional is 0 (missing optional doesn't penalise)

    avg_score = detection["scores"].get(best_version, 0)

    # Normalise to 0–100
    score_range = max_score - min_score
    if score_range > 0:
        normalised = (avg_score - min_score) / score_range * 100
        normalised = max(0.0, min(100.0, normalised))
    else:
        normalised = 0.0

    return {
        "version": best_version,
        "spec_category": spec_category,
        "score": round(normalised, 1),
        "required_pct": round(detection["required_pct"].get(best_version, 0), 1),
        "recommended_pct": round(detection["recommended_pct"].get(best_version, 0), 1),
    }

