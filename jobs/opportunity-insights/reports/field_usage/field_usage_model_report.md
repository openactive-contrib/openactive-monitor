# OpenActive Data-Model Field-Usage Report

- Generated: 2026-06-23T14:10:59+00:00
- Opportunities table: `openactive-monitor.openactive_analytics.opportunities`
- Model spec version: V2.0
- Sampling window: all-time
- Samples per (dataset, feed, kind): 500
- Thresholds: RARE < 1.0%, LOW < 10.0%

> **Sampled %** is the share of *object instances* of a type whose `json_data` contains the field key (value may be null), measured over the random sample (up to 500 rows per dataset/feed/kind). Entities referenced by URI string are counted where they are themselves published (their own rows), not at the reference site; in-place nested entities are counted wherever they appear. Because the sample is capped per group, rare fields can wobble run to run.

## Contents

- Model categories: Event, FacilityUse, IndividualFacilityUse, Slot, Organization, Person, Place, SportsActivityLocation, GeoCoordinates, PostalAddress, Offer, PriceSpecification, Schedule, Concept, Brand, ImageObject, ContactPoint, OpeningHoursSpecification
- Discovered-only nested types: AggregateRating, BabyChanging, ChangingFacilities, CourseFeatureSpecification, Creche, LocationFeatureSpecification, Lockers, Parking, PrivacyPolicy, QuantifiedValue, QuantitativeValue, Showers, TermsOfUse, Toilets, Towels, VideoObject, VirtualLocation, beta:Bar, beta:Cafe, beta:IndicativeOffer, btf:EventComponent

## Event

- Observed `@type`s: `Course`, `CourseInstance`, `Event`, `EventSeries`, `HeadlineEvent`, `OnDemandEvent`, `ScheduledSession`, `SessionSeries`
- Total instances sampled: **115,178**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `potentialAction` | optional | 0.0% | 0 | 115,178 | UNUSED |
| `schedulingNote` | optional | 0.0% | 0 | 115,178 | UNUSED |
| `contributor` | recommended | 0.1% | 160 | 115,178 | RARE |
| `accessibilitySupport` | optional | 0.6% | 696 | 115,178 | RARE |
| `accessibilityInformation` | optional | 0.7% | 800 | 115,178 | RARE |
| `meetingPoint` | optional | 1.5% | 1,729 | 115,178 | LOW |
| `programme` | optional | 2.3% | 2,706 | 115,178 | LOW |
| `subEvent` | optional | 3.1% | 3,515 | 115,178 | LOW |
| `leader` | optional | 6.1% | 7,052 | 115,178 | LOW |
| `isAccessibleForFree` | optional | 6.3% | 7,267 | 115,178 | LOW |
| `image` | optional | 7.1% | 8,124 | 115,178 | LOW |
| `isCoached` | optional | 9.3% | 10,738 | 115,178 | LOW |
| `level` | recommended | 10.6% | 12,168 | 115,178 | COMMON |
| `attendeeInstructions` | optional | 12.1% | 13,902 | 115,178 | COMMON |
| `ageRange` | recommended | 18.6% | 21,435 | 115,178 | COMMON |
| `category` | optional | 21.0% | 24,171 | 115,178 | COMMON |
| `eventStatus` | recommended | 23.4% | 26,908 | 115,178 | COMMON |
| `eventSchedule` | optional | 25.8% | 29,724 | 115,178 | COMMON |
| `description` | recommended | 28.5% | 32,826 | 115,178 | COMMON |
| `remainingAttendeeCapacity` | recommended | 29.2% | 33,652 | 115,178 | COMMON |
| `activity` | required | 29.5% | 33,923 | 115,178 | COMMON |
| `maximumAttendeeCapacity` | recommended | 30.6% | 35,263 | 115,178 | COMMON |
| `genderRestriction` | optional | 30.7% | 35,315 | 115,178 | COMMON |
| `location` | required | 34.6% | 39,852 | 115,178 | COMMON |
| `organizer` | required | 36.8% | 42,385 | 115,178 | COMMON |
| `offers` | recommended | 37.0% | 42,611 | 115,178 | COMMON |
| `url` | required | 42.9% | 49,388 | 115,178 | COMMON |
| `superEvent` | optional | 46.4% | 53,411 | 115,178 | COMMON |
| `@id` | recommended | 53.8% | 62,014 | 115,178 | COMMON |
| `duration` | recommended | 58.3% | 67,199 | 115,178 | COMMON |
| `name` | required | 60.4% | 69,541 | 115,178 | COMMON |
| `identifier` | optional | 78.0% | 89,830 | 115,178 | COMMON |
| `endDate` | recommended | 82.9% | 95,485 | 115,178 | COMMON |
| `startDate` | recommended | 86.7% | 99,854 | 115,178 | COMMON |
| `@type` | required | 100.0% | 115,178 | 115,178 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `potentialAction` (optional) — UNUSED, 0.0% (0/115,178)
- `schedulingNote` (optional) — UNUSED, 0.0% (0/115,178)
- `contributor` (recommended) — RARE, 0.1% (160/115,178)
- `accessibilitySupport` (optional) — RARE, 0.6% (696/115,178)
- `accessibilityInformation` (optional) — RARE, 0.7% (800/115,178)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `beta:sportsActivityLocation` | 13.4% | 15,411 | 115,178 |
| `beta:formattedDescription` | 12.7% | 14,593 | 115,178 |
| `eventAttendanceMode` | 4.9% | 5,642 | 115,178 |
| `beta:estimatedDuration` | 3.8% | 4,330 | 115,178 |
| `beta:participantSuppliedEquipment` | 1.6% | 1,803 | 115,178 |
| `author` | 1.3% | 1,544 | 115,178 |
| `instanceOfCourse` | 1.3% | 1,511 | 115,178 |
| `btf:componentEvent` | 1.2% | 1,435 | 115,178 |
| `beta:attendeeCount` | 1.1% | 1,316 | 115,178 |
| `participation_type` | 0.9% | 1,033 | 115,178 |
| `beta:distance` | 0.9% | 1,001 | 115,178 |
| `disambiguatingDescription` | 0.9% | 1,001 | 115,178 |
| `additionalAdmissionRestriction` | 0.8% | 968 | 115,178 |
| `beta:isWheelchairAccessible` | 0.7% | 858 | 115,178 |
| `beta:facilitySetting` | 0.7% | 791 | 115,178 |
| `beta:isVirtuallyCoached` | 0.6% | 706 | 115,178 |
| `beta:isScheduledAsSlots` | 0.6% | 679 | 115,178 |
| `beta:FacilitySettingType` | 0.6% | 641 | 115,178 |
| `beta:virtualLocation` | 0.5% | 624 | 115,178 |
| `beta:donationPaymentUrl` | 0.4% | 517 | 115,178 |
| `btf:raceTypes` | 0.4% | 500 | 115,178 |
| `btf:eventFeatures` | 0.4% | 467 | 115,178 |
| `activities` | 0.4% | 458 | 115,178 |
| `courseFeatures` | 0.3% | 383 | 115,178 |
| `btf:expectedCompetitors` | 0.3% | 365 | 115,178 |
| `subEventUrl` | 0.3% | 360 | 115,178 |
| `beta:contactPoint` | 0.2% | 244 | 115,178 |
| `beta:isFirstSessionAccessibleForFree` | 0.2% | 244 | 115,178 |
| `beta:video` | 0.1% | 76 | 115,178 |
| `specialRequirements` | 0.1% | 62 | 115,178 |
| `beta:isInteractivityPreferred` | 0.0% | 52 | 115,178 |
| `beta:course` | 0.0% | 33 | 115,178 |
| `logo` | 0.0% | 33 | 115,178 |
| `btf:draftLegal` | 0.0% | 26 | 115,178 |
| `britishcycling:gpxFile` | 0.0% | 18 | 115,178 |
| `britishcycling:terrain` | 0.0% | 17 | 115,178 |
| `britishcycling:topography` | 0.0% | 17 | 115,178 |
| `britishcycling:publicTransport` | 0.0% | 12 | 115,178 |
| `britishcycling:publicTransportDetails` | 0.0% | 12 | 115,178 |
| `britishcycling:stoppingPoints` | 0.0% | 12 | 115,178 |
| `btf:qualifier` | 0.0% | 7 | 115,178 |
| `sameAs` | 0.0% | 5 | 115,178 |
| `beta:activityDuration` | 0.0% | 1 | 115,178 |
| `beta:hasCoaching` | 0.0% | 1 | 115,178 |
| `beta:level` | 0.0% | 1 | 115,178 |
| `beta:orderPostUrl` | 0.0% | 1 | 115,178 |
| `beta:registrationCount` | 0.0% | 1 | 115,178 |
| `publicAccess` | 0.0% | 1 | 115,178 |
| `toLocation` | 0.0% | 1 | 115,178 |

## FacilityUse

- Observed `@type`s: `FacilityUse`
- Total instances sampled: **5,004**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `accessibilitySupport` | optional | 0.0% | 0 | 5,004 | UNUSED |
| `aggregateFacilityUse` | optional | 0.0% | 0 | 5,004 | UNUSED |
| `event` | recommended | 0.0% | 0 | 5,004 | UNUSED |
| `potentialAction` | optional | 0.0% | 0 | 5,004 | UNUSED |
| `accessibilityInformation` | optional | 5.5% | 276 | 5,004 | LOW |
| `individualFacilityUse` | optional | 10.6% | 532 | 5,004 | COMMON |
| `image` | recommended | 23.9% | 1,198 | 5,004 | COMMON |
| `attendeeInstructions` | optional | 36.4% | 1,823 | 5,004 | COMMON |
| `description` | recommended | 45.8% | 2,293 | 5,004 | COMMON |
| `offers` | optional | 53.0% | 2,654 | 5,004 | COMMON |
| `category` | optional | 56.7% | 2,836 | 5,004 | COMMON |
| `hoursAvailable` | optional | 57.5% | 2,879 | 5,004 | COMMON |
| `activity` | required | 75.2% | 3,764 | 5,004 | COMMON |
| `url` | required | 81.3% | 4,067 | 5,004 | COMMON |
| `identifier` | optional | 82.7% | 4,139 | 5,004 | COMMON |
| `@id` | required | 94.5% | 4,730 | 5,004 | COMMON |
| `@type` | required | 94.5% | 4,730 | 5,004 | COMMON |
| `location` | required | 94.5% | 4,730 | 5,004 | COMMON |
| `name` | required | 94.5% | 4,730 | 5,004 | COMMON |
| `provider` | required | 94.5% | 4,730 | 5,004 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `accessibilitySupport` (optional) — UNUSED, 0.0% (0/5,004)
- `aggregateFacilityUse` (optional) — UNUSED, 0.0% (0/5,004)
- `event` (recommended) — UNUSED, 0.0% (0/5,004)
- `potentialAction` (optional) — UNUSED, 0.0% (0/5,004)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `endDate` | 100.0% | 5,004 | 5,004 |
| `startDate` | 100.0% | 5,004 | 5,004 |
| `beta:offerValidityPeriod` | 56.7% | 2,836 | 5,004 |
| `beta:formattedDescription` | 46.4% | 2,321 | 5,004 |
| `beta:facilitySetting` | 41.7% | 2,086 | 5,004 |
| `alternateName` | 37.4% | 1,871 | 5,004 |
| `beta:facilityType` | 16.9% | 844 | 5,004 |
| `beta:isWheelchairAccessible` | 8.6% | 432 | 5,004 |
| `beta:video` | 0.0% | 2 | 5,004 |

## IndividualFacilityUse

- Observed `@type`s: `IndividualFacilityUse`
- Total instances sampled: **5,033**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `accessibilityInformation` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `accessibilitySupport` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `aggregateFacilityUse` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `attendeeInstructions` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `category` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `description` | recommended | 0.0% | 0 | 5,033 | UNUSED |
| `event` | recommended | 0.0% | 0 | 5,033 | UNUSED |
| `image` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `offers` | recommended | 0.0% | 0 | 5,033 | UNUSED |
| `potentialAction` | optional | 0.0% | 0 | 5,033 | UNUSED |
| `activity` | required | 68.4% | 3,445 | 5,033 | COMMON |
| `identifier` | optional | 68.4% | 3,445 | 5,033 | COMMON |
| `location` | recommended | 68.4% | 3,445 | 5,033 | COMMON |
| `provider` | recommended | 68.4% | 3,445 | 5,033 | COMMON |
| `hoursAvailable` | optional | 82.1% | 4,130 | 5,033 | COMMON |
| `url` | recommended | 97.1% | 4,888 | 5,033 | COMMON |
| `@id` | recommended | 100.0% | 5,033 | 5,033 | COMMON |
| `@type` | required | 100.0% | 5,033 | 5,033 | COMMON |
| `name` | required | 100.0% | 5,033 | 5,033 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `accessibilityInformation` (optional) — UNUSED, 0.0% (0/5,033)
- `accessibilitySupport` (optional) — UNUSED, 0.0% (0/5,033)
- `aggregateFacilityUse` (optional) — UNUSED, 0.0% (0/5,033)
- `attendeeInstructions` (optional) — UNUSED, 0.0% (0/5,033)
- `category` (optional) — UNUSED, 0.0% (0/5,033)
- `description` (recommended) — UNUSED, 0.0% (0/5,033)
- `event` (recommended) — UNUSED, 0.0% (0/5,033)
- `image` (optional) — UNUSED, 0.0% (0/5,033)
- `offers` (recommended) — UNUSED, 0.0% (0/5,033)
- `potentialAction` (optional) — UNUSED, 0.0% (0/5,033)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `endDate` | 68.4% | 3,445 | 5,033 |
| `startDate` | 68.4% | 3,445 | 5,033 |
| `beta:facilitySetting` | 1.7% | 84 | 5,033 |
| `beta:isWheelchairAccessible` | 0.1% | 3 | 5,033 |

## Slot

- Observed `@type`s: `Slot`
- Total instances sampled: **71,001**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `maximumUses` | recommended | 40.9% | 29,007 | 71,001 | COMMON |
| `identifier` | optional | 99.3% | 70,501 | 71,001 | COMMON |
| `offers` | recommended | 100.0% | 70,990 | 71,001 | COMMON |
| `@id` | recommended | 100.0% | 71,001 | 71,001 | COMMON |
| `@type` | required | 100.0% | 71,001 | 71,001 | COMMON |
| `duration` | required | 100.0% | 71,001 | 71,001 | COMMON |
| `endDate` | optional | 100.0% | 71,001 | 71,001 | COMMON |
| `facilityUse` | required | 100.0% | 71,001 | 71,001 | COMMON |
| `remainingUses` | required | 100.0% | 71,001 | 71,001 | COMMON |
| `startDate` | required | 100.0% | 71,001 | 71,001 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

_None — every model field is used above the RARE threshold._

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `beta:sportsActivityLocation` | 21.1% | 15,007 | 71,001 |
| `url` | 1.4% | 1,000 | 71,001 |
| `isOpenBookingWithCustomerAccountAllowed` | 0.7% | 500 | 71,001 |
| `additionalAdmissionRestriction` | 0.2% | 139 | 71,001 |

## Organization

- Observed `@type`s: `Organization`
- Total instances sampled: **49,797**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `contactPoint` | optional | 0.0% | 0 | 49,797 | UNUSED |
| `taxID` | optional | 0.0% | 0 | 49,797 | UNUSED |
| `vatID` | optional | 0.0% | 0 | 49,797 | UNUSED |
| `address` | optional | 1.2% | 576 | 49,797 | LOW |
| `image` | optional | 3.7% | 1,820 | 49,797 | LOW |
| `identifier` | optional | 5.2% | 2,612 | 49,797 | LOW |
| `sameAs` | optional | 26.9% | 13,391 | 49,797 | COMMON |
| `description` | optional | 27.0% | 13,451 | 49,797 | COMMON |
| `logo` | optional | 31.6% | 15,724 | 49,797 | COMMON |
| `legalName` | optional | 38.2% | 19,034 | 49,797 | COMMON |
| `telephone` | optional | 39.2% | 19,541 | 49,797 | COMMON |
| `url` | recommended | 56.1% | 27,942 | 49,797 | COMMON |
| `email` | optional | 57.0% | 28,385 | 49,797 | COMMON |
| `@id` | recommended | 70.7% | 35,182 | 49,797 | COMMON |
| `@type` | required | 100.0% | 49,797 | 49,797 | COMMON |
| `name` | required | 100.0% | 49,797 | 49,797 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `contactPoint` (optional) — UNUSED, 0.0% (0/49,797)
- `taxID` (optional) — UNUSED, 0.0% (0/49,797)
- `vatID` (optional) — UNUSED, 0.0% (0/49,797)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `beta:formattedDescription` | 28.5% | 14,203 | 49,797 |
| `taxMode` | 13.9% | 6,920 | 49,797 |
| `beta:video` | 12.6% | 6,297 | 49,797 |
| `isOpenBookingAllowed` | 7.4% | 3,671 | 49,797 |
| `beta:formalCriteriaMet` | 4.3% | 2,150 | 49,797 |
| `termsOfService` | 0.5% | 226 | 49,797 |
| `aggregateRating` | 0.0% | 6 | 49,797 |
| `beta:numberOfMembers` | 0.0% | 6 | 49,797 |
| `foundingDate` | 0.0% | 6 | 49,797 |

## Person

- Observed `@type`s: `Person`
- Total instances sampled: **8,025**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `contactPoint` | optional | 0.0% | 0 | 8,025 | UNUSED |
| `image` | optional | 0.0% | 0 | 8,025 | UNUSED |
| `sameAs` | optional | 0.0% | 0 | 8,025 | UNUSED |
| `telephone` | optional | 2.7% | 217 | 8,025 | LOW |
| `identifier` | optional | 4.3% | 343 | 8,025 | LOW |
| `description` | optional | 5.6% | 448 | 8,025 | LOW |
| `gender` | optional | 6.2% | 500 | 8,025 | LOW |
| `jobTitle` | optional | 7.4% | 596 | 8,025 | LOW |
| `email` | optional | 12.9% | 1,033 | 8,025 | COMMON |
| `url` | recommended | 15.9% | 1,279 | 8,025 | COMMON |
| `@id` | recommended | 20.2% | 1,619 | 8,025 | COMMON |
| `name` | required | 87.3% | 7,002 | 8,025 | COMMON |
| `@type` | required | 100.0% | 8,025 | 8,025 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `contactPoint` (optional) — UNUSED, 0.0% (0/8,025)
- `image` (optional) — UNUSED, 0.0% (0/8,025)
- `sameAs` (optional) — UNUSED, 0.0% (0/8,025)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `givenName` | 12.7% | 1,022 | 8,025 |
| `taxMode` | 9.9% | 796 | 8,025 |
| `familyName` | 8.8% | 706 | 8,025 |
| `beta:formalCriteriaMet` | 1.0% | 77 | 8,025 |
| `address` | 0.9% | 72 | 8,025 |

## Place

- Observed `@type`s: `Place`
- Total instances sampled: **48,028**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `containedInPlace` | optional | 0.0% | 0 | 48,028 | UNUSED |
| `containsPlace` | optional | 0.0% | 0 | 48,028 | UNUSED |
| `image` | optional | 13.4% | 6,439 | 48,028 | COMMON |
| `@id` | recommended | 16.1% | 7,753 | 48,028 | COMMON |
| `description` | recommended | 25.7% | 12,330 | 48,028 | COMMON |
| `openingHoursSpecification` | optional | 28.6% | 13,757 | 48,028 | COMMON |
| `amenityFeature` | optional | 37.5% | 18,024 | 48,028 | COMMON |
| `telephone` | optional | 60.2% | 28,909 | 48,028 | COMMON |
| `url` | recommended | 60.5% | 29,071 | 48,028 | COMMON |
| `identifier` | optional | 70.0% | 33,622 | 48,028 | COMMON |
| `geo` | optional | 86.2% | 41,404 | 48,028 | COMMON |
| `address` | optional | 95.7% | 45,978 | 48,028 | COMMON |
| `name` | required | 99.0% | 47,525 | 48,028 | COMMON |
| `@type` | required | 100.0% | 48,028 | 48,028 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `containedInPlace` (optional) — UNUSED, 0.0% (0/48,028)
- `containsPlace` (optional) — UNUSED, 0.0% (0/48,028)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `beta:formattedDescription` | 33.2% | 15,942 | 48,028 |
| `beta:placeType` | 2.0% | 947 | 48,028 |
| `email` | 1.8% | 877 | 48,028 |
| `areaServed` | 0.0% | 1 | 48,028 |
| `beta:meetingPoint` | 0.0% | 1 | 48,028 |

## SportsActivityLocation

- Observed `@type`s: `SportsActivityLocation`
- Total instances sampled: **57,234**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `@id` | recommended | 0.0% | 0 | 57,234 | UNUSED |
| `address` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `amenityFeature` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `containedInPlace` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `containsPlace` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `description` | recommended | 0.0% | 0 | 57,234 | UNUSED |
| `geo` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `image` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `openingHoursSpecification` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `telephone` | optional | 0.0% | 0 | 57,234 | UNUSED |
| `url` | recommended | 0.0% | 0 | 57,234 | UNUSED |
| `identifier` | optional | 70.2% | 40,158 | 57,234 | COMMON |
| `name` | required | 97.1% | 55,569 | 57,234 | COMMON |
| `@type` | required | 100.0% | 57,234 | 57,234 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `@id` (recommended) — UNUSED, 0.0% (0/57,234)
- `address` (optional) — UNUSED, 0.0% (0/57,234)
- `amenityFeature` (optional) — UNUSED, 0.0% (0/57,234)
- `containedInPlace` (optional) — UNUSED, 0.0% (0/57,234)
- `containsPlace` (optional) — UNUSED, 0.0% (0/57,234)
- `description` (recommended) — UNUSED, 0.0% (0/57,234)
- `geo` (optional) — UNUSED, 0.0% (0/57,234)
- `image` (optional) — UNUSED, 0.0% (0/57,234)
- `openingHoursSpecification` (optional) — UNUSED, 0.0% (0/57,234)
- `telephone` (optional) — UNUSED, 0.0% (0/57,234)
- `url` (recommended) — UNUSED, 0.0% (0/57,234)

### Provider-extension fields (not in the model)

_None observed._

## GeoCoordinates

- Observed `@type`s: `GeoCoordinates`
- Total instances sampled: **41,404**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `@type` | required | 100.0% | 41,404 | 41,404 | COMMON |
| `latitude` | required | 100.0% | 41,404 | 41,404 | COMMON |
| `longitude` | required | 100.0% | 41,404 | 41,404 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

_None — every model field is used above the RARE threshold._

### Provider-extension fields (not in the model)

_None observed._

## PostalAddress

- Observed `@type`s: `PostalAddress`
- Total instances sampled: **43,608**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `addressRegion` | recommended | 87.3% | 38,089 | 43,608 | COMMON |
| `addressLocality` | recommended | 87.4% | 38,115 | 43,608 | COMMON |
| `streetAddress` | recommended | 88.8% | 38,705 | 43,608 | COMMON |
| `postalCode` | recommended | 90.6% | 39,492 | 43,608 | COMMON |
| `addressCountry` | recommended | 90.9% | 39,660 | 43,608 | COMMON |
| `@type` | required | 100.0% | 43,608 | 43,608 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

_None — every model field is used above the RARE threshold._

### Provider-extension fields (not in the model)

_None observed._

## Offer

- Observed `@type`s: `Offer`
- Total instances sampled: **152,019**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `availability` | optional | 0.0% | 0 | 152,019 | UNUSED |
| `availableChannel` | optional | 0.0% | 0 | 152,019 | UNUSED |
| `openBookingFlowRequirement` | optional | 0.0% | 0 | 152,019 | UNUSED |
| `prepayment` | optional | 0.0% | 0 | 152,019 | UNUSED |
| `ageRestriction` | optional | 17.1% | 25,933 | 152,019 | COMMON |
| `acceptedPaymentMethod` | optional | 26.3% | 40,013 | 152,019 | COMMON |
| `latestCancellationBeforeStartDate` | optional | 27.6% | 41,991 | 152,019 | COMMON |
| `allowCustomerCancellationFullRefund` | optional | 27.6% | 41,994 | 152,019 | COMMON |
| `validFromBeforeStartDate` | optional | 28.0% | 42,565 | 152,019 | COMMON |
| `url` | optional | 29.7% | 45,155 | 152,019 | COMMON |
| `description` | optional | 30.3% | 46,053 | 152,019 | COMMON |
| `@id` | recommended | 31.6% | 48,052 | 152,019 | COMMON |
| `identifier` | optional | 80.7% | 122,726 | 152,019 | COMMON |
| `name` | recommended | 85.7% | 130,282 | 152,019 | COMMON |
| `priceCurrency` | required | 98.9% | 150,380 | 152,019 | COMMON |
| `@type` | required | 100.0% | 152,019 | 152,019 | COMMON |
| `price` | required | 100.0% | 152,019 | 152,019 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `availability` (optional) — UNUSED, 0.0% (0/152,019)
- `availableChannel` (optional) — UNUSED, 0.0% (0/152,019)
- `openBookingFlowRequirement` (optional) — UNUSED, 0.0% (0/152,019)
- `prepayment` (optional) — UNUSED, 0.0% (0/152,019)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `openBookingInAdvance` | 27.3% | 41,494 | 152,019 |
| `validThroughBeforeStartDate` | 27.3% | 41,494 | 152,019 |
| `beta:partySize` | 4.2% | 6,334 | 152,019 |
| `ageRange` | 3.5% | 5,263 | 152,019 |
| `eligibleCustomerType` | 1.0% | 1,542 | 152,019 |
| `validFrom` | 0.5% | 761 | 152,019 |
| `openBookingPrepayment` | 0.3% | 500 | 152,019 |
| `validThrough` | 0.2% | 356 | 152,019 |

## PriceSpecification

- Observed `@type`s: _(none observed)_
- Total instances sampled: **0**

_No sampled instances for this category._

## Schedule

- Observed `@type`s: `PartialSchedule`, `Schedule`
- Total instances sampled: **55,261**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `byMonth` | optional | 0.0% | 0 | 55,261 | UNUSED |
| `byMonthDay` | optional | 0.0% | 6 | 55,261 | RARE |
| `exceptDate` | optional | 0.7% | 362 | 55,261 | RARE |
| `repeatCount` | optional | 1.5% | 809 | 55,261 | LOW |
| `idTemplate` | recommended | 2.6% | 1,458 | 55,261 | LOW |
| `urlTemplate` | recommended | 2.6% | 1,458 | 55,261 | LOW |
| `scheduledEventType` | required | 5.5% | 3,054 | 55,261 | LOW |
| `endDate` | recommended | 68.9% | 38,085 | 55,261 | COMMON |
| `repeatFrequency` | required | 71.5% | 39,495 | 55,261 | COMMON |
| `duration` | recommended | 77.7% | 42,926 | 55,261 | COMMON |
| `endTime` | required | 79.6% | 43,981 | 55,261 | COMMON |
| `byDay` | optional | 92.1% | 50,916 | 55,261 | COMMON |
| `startDate` | recommended | 97.3% | 53,761 | 55,261 | COMMON |
| `startTime` | required | 98.8% | 54,582 | 55,261 | COMMON |
| `@type` | required | 100.0% | 55,261 | 55,261 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `byMonth` (optional) — UNUSED, 0.0% (0/55,261)
- `byMonthDay` (optional) — RARE, 0.0% (6/55,261)
- `exceptDate` (optional) — RARE, 0.7% (362/55,261)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `scheduleTimezone` | 73.8% | 40,757 | 55,261 |

## Concept

- Observed `@type`s: `Concept`
- Total instances sampled: **57,220**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `altLabel` | optional | 0.0% | 0 | 57,220 | UNUSED |
| `broader` | optional | 0.0% | 0 | 57,220 | UNUSED |
| `narrower` | optional | 0.0% | 0 | 57,220 | UNUSED |
| `notation` | optional | 1.7% | 958 | 57,220 | LOW |
| `@id` | recommended | 98.3% | 56,231 | 57,220 | COMMON |
| `prefLabel` | required | 100.0% | 57,203 | 57,220 | COMMON |
| `@type` | required | 100.0% | 57,220 | 57,220 | COMMON |
| `inScheme` | optional | 100.0% | 57,220 | 57,220 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `altLabel` (optional) — UNUSED, 0.0% (0/57,220)
- `broader` (optional) — UNUSED, 0.0% (0/57,220)
- `narrower` (optional) — UNUSED, 0.0% (0/57,220)

### Provider-extension fields (not in the model)

_None observed._

## Brand

- Observed `@type`s: `Brand`
- Total instances sampled: **2,705**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `video` | optional | 0.0% | 0 | 2,705 | UNUSED |
| `@id` | recommended | 3.3% | 88 | 2,705 | LOW |
| `identifier` | optional | 37.0% | 1,000 | 2,705 | COMMON |
| `description` | recommended | 58.2% | 1,575 | 2,705 | COMMON |
| `logo` | recommended | 61.9% | 1,675 | 2,705 | COMMON |
| `url` | required | 99.9% | 2,703 | 2,705 | COMMON |
| `@type` | required | 100.0% | 2,705 | 2,705 | COMMON |
| `name` | required | 100.0% | 2,705 | 2,705 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `video` (optional) — UNUSED, 0.0% (0/2,705)

### Provider-extension fields (not in the model)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `beta:video` | 26.0% | 703 | 2,705 |

## ImageObject

- Observed `@type`s: `ImageObject`
- Total instances sampled: **67,786**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `description` | optional | 0.0% | 0 | 67,786 | UNUSED |
| `height` | optional | 0.0% | 0 | 67,786 | UNUSED |
| `name` | optional | 0.0% | 0 | 67,786 | UNUSED |
| `thumbnail` | optional | 0.0% | 0 | 67,786 | UNUSED |
| `width` | optional | 0.0% | 0 | 67,786 | UNUSED |
| `@type` | required | 100.0% | 67,786 | 67,786 | COMMON |
| `url` | required | 100.0% | 67,786 | 67,786 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `description` (optional) — UNUSED, 0.0% (0/67,786)
- `height` (optional) — UNUSED, 0.0% (0/67,786)
- `name` (optional) — UNUSED, 0.0% (0/67,786)
- `thumbnail` (optional) — UNUSED, 0.0% (0/67,786)
- `width` (optional) — UNUSED, 0.0% (0/67,786)

### Provider-extension fields (not in the model)

_None observed._

## ContactPoint

- Observed `@type`s: `ContactPoint`
- Total instances sampled: **244**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `availableLanguage` | optional | 0.0% | 0 | 244 | UNUSED |
| `contactType` | optional | 0.0% | 0 | 244 | UNUSED |
| `url` | optional | 0.0% | 0 | 244 | UNUSED |
| `telephone` | optional | 91.4% | 223 | 244 | COMMON |
| `@type` | required | 100.0% | 244 | 244 | COMMON |
| `email` | optional | 100.0% | 244 | 244 | COMMON |
| `name` | optional | 100.0% | 244 | 244 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `availableLanguage` (optional) — UNUSED, 0.0% (0/244)
- `contactType` (optional) — UNUSED, 0.0% (0/244)
- `url` (optional) — UNUSED, 0.0% (0/244)

### Provider-extension fields (not in the model)

_None observed._

## OpeningHoursSpecification

- Observed `@type`s: `OpeningHoursSpecification`
- Total instances sampled: **130,318**

### Model fields

| Field | Model status | Sampled % | Instances with | Total | Classification |
|---|---|---:|---:|---:|---|
| `validFrom` | optional | 0.0% | 0 | 130,318 | UNUSED |
| `validThrough` | optional | 0.0% | 0 | 130,318 | UNUSED |
| `dayOfWeek` | required | 99.9% | 130,249 | 130,318 | COMMON |
| `@type` | required | 100.0% | 130,318 | 130,318 | COMMON |
| `closes` | optional | 100.0% | 130,318 | 130,318 | COMMON |
| `opens` | optional | 100.0% | 130,318 | 130,318 | COMMON |

### ⚠️ Deletion candidates (UNUSED / RARE)

- `validFrom` (optional) — UNUSED, 0.0% (0/130,318)
- `validThrough` (optional) — UNUSED, 0.0% (0/130,318)

### Provider-extension fields (not in the model)

_None observed._

## Discovered-only nested entity types

_These `@type`s are not part of the OpenActive opportunity model catalog (e.g. Place, Organization, Offer). Reported as discovered from in-place nested objects; sampling-only coverage._

### `AggregateRating` (instances sampled: 6)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `bestRating` | 100.0% | 6 | 6 |
| `ratingValue` | 100.0% | 6 | 6 |
| `reviewCount` | 100.0% | 6 | 6 |
| `type` | 100.0% | 6 | 6 |
| `worstRating` | 100.0% | 6 | 6 |

### `BabyChanging` (instances sampled: 15,812)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 15,812 | 15,812 |
| `name` | 100.0% | 15,812 | 15,812 |
| `value` | 100.0% | 15,812 | 15,812 |

### `ChangingFacilities` (instances sampled: 17,110)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `name` | 100.0% | 17,110 | 17,110 |
| `value` | 100.0% | 17,110 | 17,110 |
| `@type` | 96.9% | 16,585 | 17,110 |
| `type` | 3.1% | 525 | 17,110 |

### `CourseFeatureSpecification` (instances sampled: 766)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `name` | 100.0% | 766 | 766 |
| `type` | 100.0% | 766 | 766 |
| `value` | 100.0% | 766 | 766 |

### `Creche` (instances sampled: 16,197)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 16,197 | 16,197 |
| `name` | 100.0% | 16,197 | 16,197 |
| `value` | 100.0% | 16,197 | 16,197 |

### `LocationFeatureSpecification` (instances sampled: 8,637)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 8,637 | 8,637 |
| `name` | 100.0% | 8,637 | 8,637 |
| `value` | 100.0% | 8,637 | 8,637 |

### `Lockers` (instances sampled: 16,578)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 16,578 | 16,578 |
| `name` | 100.0% | 16,578 | 16,578 |
| `value` | 100.0% | 16,578 | 16,578 |

### `Parking` (instances sampled: 16,951)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `name` | 100.0% | 16,951 | 16,951 |
| `value` | 100.0% | 16,951 | 16,951 |
| `@type` | 98.9% | 16,768 | 16,951 |
| `type` | 1.1% | 183 | 16,951 |
| `description` | 0.0% | 4 | 16,951 |

### `PrivacyPolicy` (instances sampled: 226)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 226 | 226 |
| `name` | 100.0% | 226 | 226 |
| `requiresExplicitConsent` | 100.0% | 226 | 226 |
| `url` | 100.0% | 226 | 226 |
| `dateModified` | 6.6% | 15 | 226 |

### `QuantifiedValue` (instances sampled: 4,299)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `type` | 100.0% | 4,299 | 4,299 |
| `unitCode` | 100.0% | 4,299 | 4,299 |
| `value` | 100.0% | 4,299 | 4,299 |

### `QuantitativeValue` (instances sampled: 72,903)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `minValue` | 78.9% | 57,493 | 72,903 |
| `@type` | 72.5% | 52,829 | 72,903 |
| `maxValue` | 59.3% | 43,236 | 72,903 |
| `type` | 27.5% | 20,074 | 72,903 |
| `unitCode` | 8.0% | 5,830 | 72,903 |
| `value` | 7.3% | 5,330 | 72,903 |

### `Showers` (instances sampled: 17,387)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `name` | 100.0% | 17,387 | 17,387 |
| `value` | 100.0% | 17,387 | 17,387 |
| `@type` | 95.3% | 16,576 | 17,387 |
| `type` | 4.7% | 811 | 17,387 |

### `TermsOfUse` (instances sampled: 226)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 226 | 226 |
| `name` | 100.0% | 226 | 226 |
| `requiresExplicitConsent` | 100.0% | 226 | 226 |
| `url` | 100.0% | 226 | 226 |
| `dateModified` | 6.6% | 15 | 226 |

### `Toilets` (instances sampled: 17,295)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `name` | 100.0% | 17,295 | 17,295 |
| `value` | 100.0% | 17,295 | 17,295 |
| `@type` | 97.1% | 16,791 | 17,295 |
| `type` | 2.9% | 504 | 17,295 |
| `description` | 0.0% | 1 | 17,295 |

### `Towels` (instances sampled: 16,182)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 16,182 | 16,182 |
| `name` | 100.0% | 16,182 | 16,182 |
| `value` | 100.0% | 16,182 | 16,182 |

### `VideoObject` (instances sampled: 6,408)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `url` | 100.0% | 6,408 | 6,408 |
| `@type` | 99.7% | 6,391 | 6,408 |
| `type` | 0.3% | 17 | 6,408 |

### `VirtualLocation` (instances sampled: 624)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 624 | 624 |
| `name` | 99.8% | 623 | 624 |
| `url` | 56.2% | 351 | 624 |
| `@id` | 36.5% | 228 | 624 |
| `description` | 2.4% | 15 | 624 |

### `beta:Bar` (instances sampled: 14,897)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 14,897 | 14,897 |
| `name` | 100.0% | 14,897 | 14,897 |
| `value` | 100.0% | 14,897 | 14,897 |

### `beta:Cafe` (instances sampled: 15,008)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 15,008 | 15,008 |
| `name` | 100.0% | 15,008 | 15,008 |
| `value` | 100.0% | 15,008 | 15,008 |

### `beta:IndicativeOffer` (instances sampled: 14,873)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `@type` | 100.0% | 14,873 | 14,873 |
| `identifier` | 100.0% | 14,873 | 14,873 |
| `name` | 100.0% | 14,873 | 14,873 |
| `price` | 100.0% | 14,873 | 14,873 |
| `priceCurrency` | 100.0% | 14,873 | 14,873 |
| `description` | 82.1% | 12,204 | 14,873 |
| `ageRestriction` | 57.9% | 8,609 | 14,873 |
| `@id` | 0.2% | 29 | 14,873 |

### `btf:EventComponent` (instances sampled: 4,299)

| Field | Presence % | Instances with | Total |
|---|---:|---:|---:|
| `activity` | 100.0% | 4,299 | 4,299 |
| `beta:distance` | 100.0% | 4,299 | 4,299 |
| `btf:order` | 100.0% | 4,299 | 4,299 |
| `identifier` | 100.0% | 4,299 | 4,299 |
| `name` | 100.0% | 4,299 | 4,299 |
| `type` | 100.0% | 4,299 | 4,299 |
| `btf:swimType` | 27.9% | 1,201 | 4,299 |
