"""OpenActive opportunity data-model field catalog for field-usage analysis.

This is a trimmed, self-contained copy of the data that ``field_usage`` needs
from ``quality.version_compliance`` — only the spec tables and the
alternative-field helper, none of the version-detection/scoring logic. Keeping
it local lets the analysis evolve its own catalog (more entity types, V2.0
focus) without touching the quality job.

Field statuses (``required`` / ``recommended`` / ``optional``) follow the
OpenActive Modelling Opportunity Data spec, primarily V2.0:
https://openactive.io/modelling-opportunity-data/

Scope notes:
  * ``RouteGuide`` (a separate Route Guide spec) is intentionally excluded.
  * The Event family (Event, SessionSeries, ScheduledSession, HeadlineEvent,
    CourseInstance, EventSeries, OnDemandEvent, Course) is folded into a single
    ``Event`` category, as in the original catalog.
  * Referenced / nested model types (Organization, Person, Place, Offer,
    Concept, …) are first-class categories here so their field usage is scored
    against the model rather than only "discovered".
"""

from __future__ import annotations

# Canonical ordering of versions for comparisons (higher = newer).
VERSION_ORDER: dict[str, int] = {"V0.x": 0, "V1.0": 1, "V1.1": 2, "V2.0": 3, "V2.1": 4}

# ---------------------------------------------------------------------------
# Version specifications per spec category
# ---------------------------------------------------------------------------

VERSION_SPECS: dict[str, dict[str, dict[str, str]]] = {
    # --- Event family (Event, SessionSeries, ScheduledSession, ...) ---
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
            "potentialAction": "optional",
        },
    },
    # --- FacilityUse (oa:FacilityUse) — V2.0+ ---
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
    # --- IndividualFacilityUse (oa:IndividualFacilityUse) — subtype of FacilityUse ---
    "IndividualFacilityUse": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "recommended",
            "identifier": "optional", "name": "required", "description": "recommended",
            "provider": "recommended", "image": "optional",
            "activity": "required", "location": "recommended",
            "accessibilitySupport": "optional", "accessibilityInformation": "optional",
            "attendeeInstructions": "optional", "category": "optional",
            "event": "recommended", "offers": "recommended",
            "hoursAvailable": "optional", "aggregateFacilityUse": "optional",
            "potentialAction": "optional",
        },
    },
    # --- Slot (oa:Slot) — V2.0+ ---
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
    # --- Organization (schema:Organization) ---
    "Organization": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "recommended",
            "identifier": "optional", "name": "required", "description": "optional",
            "image": "optional", "logo": "optional", "address": "optional",
            "contactPoint": "optional", "telephone": "optional", "email": "optional",
            "sameAs": "optional", "legalName": "optional", "taxID": "optional",
            "vatID": "optional",
        },
    },
    # --- Person (schema:Person) ---
    "Person": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "recommended",
            "identifier": "optional", "name": "required", "description": "optional",
            "image": "optional", "contactPoint": "optional", "telephone": "optional",
            "email": "optional", "jobTitle": "optional", "gender": "optional",
            "sameAs": "optional",
        },
    },
    # --- Place (schema:Place) ---
    "Place": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "recommended",
            "identifier": "optional", "name": "required", "description": "recommended",
            "image": "optional", "address": "optional", "geo": "optional",
            "telephone": "optional", "openingHoursSpecification": "optional",
            "amenityFeature": "optional", "containedInPlace": "optional",
            "containsPlace": "optional",
        },
    },
    # --- SportsActivityLocation (schema:SportsActivityLocation) — subtype of Place ---
    "SportsActivityLocation": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "recommended",
            "identifier": "optional", "name": "required", "description": "recommended",
            "image": "optional", "address": "optional", "geo": "optional",
            "telephone": "optional", "openingHoursSpecification": "optional",
            "amenityFeature": "optional", "containedInPlace": "optional",
            "containsPlace": "optional",
        },
    },
    # --- GeoCoordinates (schema:GeoCoordinates) ---
    "GeoCoordinates": {
        "V2.0": {
            "@type": "required", "latitude": "required", "longitude": "required",
        },
    },
    # --- PostalAddress (schema:PostalAddress) ---
    "PostalAddress": {
        "V2.0": {
            "@type": "required", "streetAddress": "recommended",
            "addressLocality": "recommended", "addressRegion": "recommended",
            "postalCode": "recommended", "addressCountry": "recommended",
        },
    },
    # --- Offer (schema:Offer) ---
    "Offer": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "identifier": "optional",
            "name": "recommended", "description": "optional",
            "price": "required", "priceCurrency": "required",
            "availability": "optional", "availableChannel": "optional",
            "acceptedPaymentMethod": "optional", "ageRestriction": "optional",
            "validFromBeforeStartDate": "optional", "openBookingFlowRequirement": "optional",
            "prepayment": "optional", "allowCustomerCancellationFullRefund": "optional",
            "latestCancellationBeforeStartDate": "optional", "url": "optional",
        },
    },
    # --- PriceSpecification (schema:PriceSpecification) ---
    "PriceSpecification": {
        "V2.0": {
            "@type": "required", "price": "required", "priceCurrency": "required",
            "name": "optional", "minPrice": "optional", "maxPrice": "optional",
            "valueAddedTaxIncluded": "optional",
        },
    },
    # --- Schedule (oa:Schedule) ---
    "Schedule": {
        "V2.0": {
            "@type": "required", "repeatFrequency": "required",
            "startDate": "recommended", "endDate": "recommended",
            "startTime": "required", "endTime": "required", "duration": "recommended",
            "byDay": "optional", "byMonth": "optional", "byMonthDay": "optional",
            "repeatCount": "optional", "exceptDate": "optional",
            "scheduledEventType": "required", "urlTemplate": "recommended",
            "idTemplate": "recommended",
        },
    },
    # --- Concept (skos:Concept) — Physical Activity / activity-list concepts ---
    "Concept": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "prefLabel": "required",
            "altLabel": "optional", "inScheme": "optional", "notation": "optional",
            "broader": "optional", "narrower": "optional",
        },
    },
    # --- Brand (oa:Brand) — the range of Event.programme ---
    "Brand": {
        "V2.0": {
            "@type": "required", "@id": "recommended", "url": "required",
            "identifier": "optional", "name": "required", "description": "recommended",
            "logo": "recommended", "video": "optional",
        },
    },
    # --- ImageObject (schema:ImageObject) ---
    "ImageObject": {
        "V2.0": {
            "@type": "required", "url": "required", "name": "optional",
            "description": "optional", "width": "optional", "height": "optional",
            "thumbnail": "optional",
        },
    },
    # --- ContactPoint (schema:ContactPoint) ---
    "ContactPoint": {
        "V2.0": {
            "@type": "required", "name": "optional", "telephone": "optional",
            "email": "optional", "url": "optional", "contactType": "optional",
            "availableLanguage": "optional",
        },
    },
    # --- OpeningHoursSpecification (schema:OpeningHoursSpecification) ---
    "OpeningHoursSpecification": {
        "V2.0": {
            "@type": "required", "dayOfWeek": "required", "opens": "optional",
            "closes": "optional", "validFrom": "optional", "validThrough": "optional",
        },
    },
}

# ---------------------------------------------------------------------------
# Mapping from observed feed_type / @type strings to spec categories
# ---------------------------------------------------------------------------

FEED_TYPE_TO_SPEC_CATEGORY: dict[str, str] = {
    # Event family → "Event"
    "Event": "Event",
    "SessionSeries": "Event",
    "ScheduledSession": "Event",
    "ScheduledSessions": "Event",
    "CourseInstance": "Event",
    "Course": "Event",
    "EventSeries": "Event",
    "HeadlineEvent": "Event",
    "OnDemandEvent": "Event",
    # Facility / slot
    "FacilityUse": "FacilityUse",
    "IndividualFacilityUse": "IndividualFacilityUse",
    "FacilityUse/Slot": "Slot",
    "Slot for FacilityUse": "Slot",
    "Slot": "Slot",
    # Referenced / nested model types (identity, plus a few aliases)
    "Organization": "Organization",
    "Person": "Person",
    "Place": "Place",
    "SportsActivityLocation": "SportsActivityLocation",
    "GeoCoordinates": "GeoCoordinates",
    "PostalAddress": "PostalAddress",
    "Offer": "Offer",
    "PriceSpecification": "PriceSpecification",
    "Schedule": "Schedule",
    "PartialSchedule": "Schedule",
    "Concept": "Concept",
    "PhysicalActivity": "Concept",
    "Brand": "Brand",
    "Programme": "Brand",
    "ImageObject": "ImageObject",
    "ContactPoint": "ContactPoint",
    "OpeningHoursSpecification": "OpeningHoursSpecification",
}

# ---------------------------------------------------------------------------
# Alternative fields
# ---------------------------------------------------------------------------

# Category-specific: a required property satisfied by an alternative key.
ALTERNATIVE_FIELDS: dict[tuple[str, str], list[str]] = {
    ("FacilityUse", "activity"): ["facilityType"],
    ("IndividualFacilityUse", "activity"): ["facilityType"],
}

# Universal aliases: feeds may use the unprefixed schema.org keys (``type``,
# ``id``) instead of the JSON-LD keys (``@type``, ``@id``); either satisfies the
# requirement.
GLOBAL_ALTERNATIVE_FIELDS: dict[str, list[str]] = {
    "@type": ["type"],
    "@id": ["id"],
}


def get_alternatives(spec_category: str, prop: str) -> list[str]:
    """Alternative field names that satisfy ``prop`` for ``spec_category``.

    Combines category-specific alternatives with the universal JSON-LD aliases.
    """
    return (
        ALTERNATIVE_FIELDS.get((spec_category, prop), [])
        + GLOBAL_ALTERNATIVE_FIELDS.get(prop, [])
    )


__all__ = [
    "VERSION_ORDER",
    "VERSION_SPECS",
    "FEED_TYPE_TO_SPEC_CATEGORY",
    "ALTERNATIVE_FIELDS",
    "GLOBAL_ALTERNATIVE_FIELDS",
    "get_alternatives",
]
