"""Required-property lists per OpenActive opportunity ``kind``.

Sourced from the OpenActive Modelling Opportunity Data spec:
https://openactive.io/modelling-opportunity-data/
https://developer.openactive.io/data-model/types

Property names are the unprefixed JSON keys actually present in ``json_data``
(e.g. ``name``, not ``schema:name``). Where the spec defines an "either A or B"
requirement (e.g. ``startDate`` OR ``eventSchedule``), the more commonly
populated option is listed here so the per-kind check stays simple.
"""

from __future__ import annotations

REQUIRED_FIELDS_BY_KIND: dict[str, list[str]] = {
    "SessionSeries":         ["@type", "name", "url", "activity", "location", "organizer"],
    "ScheduledSession":      ["@type", "name", "startDate"],
    "Event":                 ["@type", "name", "url", "activity", "location", "organizer"],
    "HeadlineEvent":         ["@type", "name", "url", "activity", "location", "organizer"],
    "OnDemandEvent":         ["@type", "name", "url", "activity", "organizer"],
    "CourseInstance":        ["@type", "name", "url", "activity", "location", "organizer"],
    "Course":                ["@type"],
    "FacilityUse":           ["@type", "@id", "name", "url", "provider", "activity", "location"],
    "IndividualFacilityUse": ["@type", "name", "url", "provider", "location"],
    "Slot":                  ["@type", "facilityUse", "startDate", "duration", "remainingUses"],
}

SAMPLES_PER_KIND = 10
QUALITY_WINDOW_DAYS = 5
