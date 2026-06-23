# Per-Dataset Field Usage

For each dataset, the fields actually present in sampled `json_data`, grouped by entity `@type`. `absent (model)` lists model fields that never appeared in this dataset for that type.

Datasets: **174**

## http://data.better.org.uk/
_publisher: GLL_

- feeds sampled: `better-org-uk-odi-sessions-json` (Event, n=500)

### Concept  (instances sampled: 958)

- present: inScheme, notation, prefLabel, type
- absent (model): @id, altLabel, broader, narrower

### Event  (instances sampled: 500)

- present: ageRange, beta:sportsActivityLocation, duration, endDate, eventStatus, location, name, organizer, startDate, type, url, activities, description, level, contributor, activity
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, eventSchedule, genderRestriction, identifier, image, isAccessibleForFree, isCoached, leader, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 500)

- present: latitude, longitude, type
- absent (model): —

### Organization  (instances sampled: 500)

- present: name, type
- absent (model): @id, address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Person  (instances sampled: 160)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 500)

- present: address, geo, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification

### PostalAddress  (instances sampled: 500)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 500)

- present: maxValue, minValue, type

### SportsActivityLocation  (instances sampled: 500)

- present: name, type
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, identifier, image, openingHoursSpecification, telephone, url

## http://data.britishtriathlon.org/
_publisher: British Triathlon_

- feeds sampled: `api-britishtriathlon-org-openactive-v1-events` (HeadlineEvent, n=500)

### Brand  (instances sampled: 117)

- present: beta:video, description, logo, name, type, url
- absent (model): @id, identifier, video

### Concept  (instances sampled: 6,307)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 1,435)

- present: activity, btf:componentEvent, genderRestriction, identifier, name, type, url, ageRange, level, offers, btf:draftLegal, accessibilitySupport
- absent (model): @id, accessibilityInformation, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent

### GeoCoordinates  (instances sampled: 488)

- present: latitude, longitude, type
- absent (model): —

### HeadlineEvent  (instances sampled: 500)

- present: activity, btf:raceTypes, duration, endDate, eventStatus, identifier, location, name, organizer, startDate, subEvent, type, url, description, btf:eventFeatures, btf:expectedCompetitors, image, programme, btf:qualifier
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, eventSchedule, genderRestriction, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, remainingAttendeeCapacity, schedulingNote, superEvent

### ImageObject  (instances sampled: 391)

- present: type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 90)

- present: name, price, priceCurrency, type, validFrom, validThrough
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: name, type
- absent (model): @id, address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Parking (nested)  (instances sampled: 153)

- present: name, type, value

### Place  (instances sampled: 500)

- present: address, name, type, geo, amenityFeature
- absent (model): @id, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 500)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### QuantifiedValue (nested)  (instances sampled: 4,299)

- present: type, unitCode, value

### QuantitativeValue (nested)  (instances sampled: 1,104)

- present: minValue, type

### Showers (nested)  (instances sampled: 316)

- present: name, type, value

### Toilets (nested)  (instances sampled: 474)

- present: name, type, value

### btf:EventComponent (nested)  (instances sampled: 4,299)

- present: activity, beta:distance, btf:order, identifier, name, type, btf:swimType

## http://data.goodgym.org/

- feeds sampled: `goodgym-org-api-happenings` (Event, n=1)

### Event  (instances sampled: 1)

- present: activity, ageRange, beta:distance, beta:formattedDescription, beta:hasCoaching, beta:level, beta:orderPostUrl, beta:registrationCount, description, disambiguatingDescription, duration, endDate, genderRestriction, id, identifier, image, isAccessibleForFree, leader, location, name, offers, organizer, programme, publicAccess, startDate, toLocation, type, url
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, eventStatus, isCoached, level, maximumAttendeeCapacity, meetingPoint, potentialAction, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 1)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1)

- present: id, price, type
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, priceCurrency, url, validFromBeforeStartDate

### Organization  (instances sampled: 1)

- present: email, logo, name, telephone, type, url
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, sameAs, taxID, vatID

### Place  (instances sampled: 2)

- present: description, type, address, areaServed, beta:meetingPoint, geo, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 1)

- present: addressLocality, postalCode, streetAddress, type
- absent (model): addressCountry, addressRegion

## http://data.letsride.co.uk/
_publisher: British Cycling_

- feeds sampled: `api-letsride-co-uk-public-v1-rides` (Event, n=500)

### AggregateRating (nested)  (instances sampled: 6)

- present: bestRating, ratingValue, reviewCount, type, worstRating

### Brand  (instances sampled: 500)

- present: description, identifier, logo, name, type, url
- absent (model): @id, video

### ChangingFacilities (nested)  (instances sampled: 30)

- present: name, type, value

### Concept  (instances sampled: 500)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: activity, ageRange, beta:attendeeCount, beta:distance, endDate, genderRestriction, identifier, isAccessibleForFree, location, name, offers, organizer, programme, startDate, type, url, meetingPoint, remainingAttendeeCapacity, description, maximumAttendeeCapacity, level, britishcycling:gpxFile, britishcycling:terrain, britishcycling:topography, attendeeInstructions, britishcycling:publicTransport, britishcycling:publicTransportDetails, britishcycling:stoppingPoints, image, accessibilityInformation, beta:activityDuration, duration
- absent (model): @id, accessibilitySupport, category, contributor, eventSchedule, eventStatus, isCoached, leader, potentialAction, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 500)

- present: latitude, longitude, type
- absent (model): —

### ImageObject  (instances sampled: 518)

- present: type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 500)

- present: price, type, url
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, priceCurrency, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: name, type, url, aggregateRating, beta:numberOfMembers, description, foundingDate, identifier, image, sameAs
- absent (model): @id, address, contactPoint, email, legalName, logo, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 30)

- present: name, type, value, description

### Place  (instances sampled: 500)

- present: address, geo, type, amenityFeature, description
- absent (model): @id, containedInPlace, containsPlace, identifier, image, name, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 500)

- present: addressCountry, postalCode, type, streetAddress, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,000)

- present: type, minValue, unitCode, value

### Toilets (nested)  (instances sampled: 30)

- present: name, type, value, description

## http://www.schools-plus.co.uk/OpenActive.php
_publisher: Schools Plus Ltd_

- feeds sampled: `api-schools-plus-co-uk-api-oa-facility-uses` (FacilityUse, n=500), `api-schools-plus-co-uk-api-oa-slots` (Slot, n=500)

### Concept  (instances sampled: 1,533)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### FacilityUse  (instances sampled: 500)

- present: @id, @type, activity, endDate, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 500)

- present: @type, latitude, longitude
- absent (model): —

### Offer  (instances sampled: 500)

- present: @id, @type, openBookingPrepayment, price, priceCurrency
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: @type, name, taxMode, telephone, url
- absent (model): @id, address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, vatID

### Place  (instances sampled: 500)

- present: @type, address, geo, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, offers, remainingUses, startDate
- absent (model): identifier, maximumUses

## https://actihire.bookteq.com/api/open-active
_publisher: Actihire_

- feeds sampled: `actihire-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=500), `actihire-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 500)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 500)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 500)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 2,777)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 500)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 500)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 500)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://activehartlepool.gs-signature.cloud/OpenActive/
_publisher: Active Hartlepool_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-HartlepoolBoroughCouncil-live-facility-uses` (FacilityUse, n=31), `opendata-leisurecloud-live-api-feeds-HartlepoolBoroughCouncil-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-HartlepoolBoroughCouncil-live-session-series` (SessionSeries, n=500)

### BabyChanging (nested)  (instances sampled: 531)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 531)

- present: @type, name, value

### Concept  (instances sampled: 100)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 531)

- present: @type, name, value

### EventSeries  (instances sampled: 77)

- present: @type, activity, ageRange, beta:formattedDescription, description, endDate, genderRestriction, identifier, level, name, organizer, startDate, isCoached, attendeeInstructions, beta:isVirtuallyCoached, accessibilitySupport
- absent (model): @id, accessibilityInformation, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 31)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 531)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 531)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 531)

- present: @type, name, value

### Offer  (instances sampled: 984)

- present: @type, acceptedPaymentMethod, description, identifier, name, price, priceCurrency, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,856)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 531)

- present: @id, @type, beta:formattedDescription, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, description, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 531)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, byDay, duration, endTime, scheduleTimezone, startDate, startTime, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 531)

- present: @type, address, amenityFeature, beta:formattedDescription, geo, identifier, name, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace, description, image

### PostalAddress  (instances sampled: 531)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 600)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, organizer, genderRestriction, attendeeInstructions, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 531)

- present: @type, name, value

### SportsActivityLocation  (instances sampled: 500)

- present: @type, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, identifier, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 531)

- present: @type, name, value

### Towels (nested)  (instances sampled: 531)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 531)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 531)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 60)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://activeleeds-oa.leisurecloud.net/OpenActive/
_publisher: Active Leeds_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-ActiveLeeds-live-facility-uses` (FacilityUse, n=79), `opendata-leisurecloud-live-api-feeds-ActiveLeeds-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-ActiveLeeds-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-ActiveLeeds-live-slots` (Slot, n=500)

### FacilityUse  (instances sampled: 79)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### ImageObject  (instances sampled: 579)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 1,483)

- present: @type, price, priceCurrency, description, identifier, name, ageRestriction
- absent (model): @id, acceptedPaymentMethod, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 553)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 579)

- present: @id, @type, beta:formattedDescription, legalName, logo, name, url
- absent (model): address, contactPoint, description, email, identifier, image, sameAs, taxID, telephone, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 579)

- present: @type, address, identifier, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 579)

- present: @type
- absent (model): addressCountry, addressLocality, addressRegion, postalCode, streetAddress

### QuantitativeValue (nested)  (instances sampled: 638)

- present: @type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, organizer, startDate, url, genderRestriction, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,625)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### beta:IndicativeOffer (nested)  (instances sampled: 309)

- present: @type, identifier, name, price, priceCurrency, description, ageRestriction

## https://activeluton-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Active Luton_

- feeds sampled: `activeluton-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=9), `activeluton-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `activeluton-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 507)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 9)

- present: endDate, startDate, activity, description, id, identifier, location, name, provider, type, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 507)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 507)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 491)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 418)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 507)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 507)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 430)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://activenottingham-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `activenottingham-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=10), `activenottingham-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `activenottingham-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 509)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 10)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 117)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,023)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 509)

- present: name, type, email
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 478)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Place  (instances sampled: 509)

- present: address, identifier, name, type, telephone, url, geo
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 509)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 546)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://ajnstadium.bookteq.com/api/open-active
_publisher: Brea Avalon LLP_

- feeds sampled: `ajnstadium-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=13), `ajnstadium-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 13)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 13)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 13)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 63)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 13)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 13)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 13)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://aliveleisure-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `aliveleisure-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=62), `aliveleisure-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `aliveleisure-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 559)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 62)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 559)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 559)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 487)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 81)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 559)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 559)

- present: addressCountry, addressRegion, postalCode, streetAddress, type, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 448)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://anemoslimited.bookteq.com/api/open-active

- feeds sampled: `anemoslimited-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=6), `anemoslimited-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 6)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 6)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 6)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 42)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 6)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 6)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 6)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://angusalive-openactive.legendonlineservices.co.uk/OpenActive
_publisher: ANGUSalive_

- feeds sampled: `angusalive-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 500)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### GeoCoordinates  (instances sampled: 500)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 735)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 400)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 110)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 500)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 500)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,133)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

## https://api.premiertennis.co.uk/openactive

- feeds sampled: `api-premiertennis-co-uk-openactive-feed-facility-uses` (FacilityUse, n=32), `api-premiertennis-co-uk-openactive-feed-scheduled-sessions` (ScheduledSession, n=454), `api-premiertennis-co-uk-openactive-feed-session-series` (SessionSeries, n=179)

### Concept  (instances sampled: 211)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### FacilityUse  (instances sampled: 32)

- present: @id, @type, endDate, facilityType, identifier, individualFacilityUse, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### GeoCoordinates  (instances sampled: 203)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 211)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### IndividualFacilityUse  (instances sampled: 145)

- present: @id, @type, name
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, identifier, image, location, offers, potentialAction, provider, url

### LocationFeatureSpecification (nested)  (instances sampled: 812)

- present: @type, name, value

### Offer  (instances sampled: 1,428)

- present: @id, @type, identifier, name, price, priceCurrency
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 196)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 211)

- present: @id, @type, address, email, isOpenBookingAllowed, legalName, logo, name, taxMode, telephone, termsOfService, url
- absent (model): contactPoint, description, identifier, image, sameAs, taxID, vatID

### Parking (nested)  (instances sampled: 203)

- present: @type, name, value

### PartialSchedule  (instances sampled: 179)

- present: @type, endDate, scheduleTimezone, startDate
- absent (model): byDay, byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, startTime, urlTemplate

### Place  (instances sampled: 211)

- present: @id, @type, address, name, amenityFeature, geo
- absent (model): containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 422)

- present: @type, addressCountry, addressRegion, postalCode, streetAddress, addressLocality
- absent (model): —

### PrivacyPolicy (nested)  (instances sampled: 211)

- present: @type, name, requiresExplicitConsent, url

### QuantitativeValue (nested)  (instances sampled: 179)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 454)

- present: @id, @type, duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, offers, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 179)

- present: @id, @type, activity, ageRange, beta:facilitySetting, beta:isScheduledAsSlots, endDate, eventSchedule, genderRestriction, identifier, location, name, offers, organizer, startDate, url, description
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### TermsOfUse (nested)  (instances sampled: 211)

- present: @type, name, requiresExplicitConsent, url

### Toilets (nested)  (instances sampled: 203)

- present: @type, name, value

## https://appleby.bookteq.com/api/open-active
_publisher: Appleby Frodingham Sports Club_

- feeds sampled: `appleby-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=21), `appleby-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 21)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 21)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 21)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 119)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 21)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 21)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 21)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://ashmoletrust.bookteq.com/api/open-active
_publisher: Ashmole Trust_

- feeds sampled: `ashmoletrust-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=94), `ashmoletrust-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 94)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 94)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 94)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 643)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 94)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 94)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 94)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://awesomecic.bookteq.com/api/open-active
_publisher: Awesome CIC_

- feeds sampled: `awesomecic-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=2), `awesomecic-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 2)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 2)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 2)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 24)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 2)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 2)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 2)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://bangorcitystadium.bookteq.com/api/open-active
_publisher: Bangor City Stadium_

- feeds sampled: `bangorcitystadium-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=3), `bangorcitystadium-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 3)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 3)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 3)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 21)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 3)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 3)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 3)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://barrowcouncil-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Barrow Park Leisure Centre_

- feeds sampled: `barrowcouncil-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=16), `barrowcouncil-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `barrowcouncil-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 1,249)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 16)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 507)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,645)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 507)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 424)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 250)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 507)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 507)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,982)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://basingstokewellbeing.bookteq.com/api/open-active
_publisher: Basingstoke Wellbeing_

- feeds sampled: `basingstokewellbeing-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=5)

### Concept  (instances sampled: 5)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 5)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 5)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, offers, potentialAction

### Organization  (instances sampled: 5)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 5)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 5)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

## https://bccleisure.gs-signature.cloud/OpenActive/
_publisher: Birmingham City Council_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-BirminghamCityCouncil-live-facility-uses` (FacilityUse, n=10), `opendata-leisurecloud-live-api-feeds-BirminghamCityCouncil-live-scheduled-sessions` (ScheduledSession, n=274), `opendata-leisurecloud-live-api-feeds-BirminghamCityCouncil-live-session-series` (SessionSeries, n=124), `opendata-leisurecloud-live-api-feeds-BirminghamCityCouncil-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 134)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 134)

- present: @type, name, value

### Concept  (instances sampled: 100)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 134)

- present: @type, name, value

### EventSeries  (instances sampled: 45)

- present: @type, activity, beta:formattedDescription, description, endDate, genderRestriction, identifier, name, organizer, startDate, level, isCoached, ageRange, attendeeInstructions, accessibilitySupport, image
- absent (model): @id, accessibilityInformation, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 10)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions, activity, alternateName, beta:formattedDescription
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 134)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 797)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 134)

- present: @type, name, value

### Offer  (instances sampled: 955)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 1,008)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 134)

- present: @id, @type, beta:formattedDescription, description, legalName, name, url
- absent (model): address, contactPoint, email, identifier, image, logo, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 134)

- present: @type, name, value

### PartialSchedule  (instances sampled: 124)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 134)

- present: @type, address, amenityFeature, beta:formattedDescription, description, geo, identifier, name, openingHoursSpecification, telephone, url, image
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 134)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 25)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 274)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 124)

- present: @id, @type, attendeeInstructions, category, duration, endDate, eventSchedule, identifier, location, name, offers, startDate, url, genderRestriction, organizer, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 134)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,021)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 134)

- present: @type, name, value

### Towels (nested)  (instances sampled: 134)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 134)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 134)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 45)

- present: @type, identifier, name, price, priceCurrency, description, ageRestriction

## https://beaconsfieldtownfc.bookteq.com/api/open-active
_publisher: Beaconsfield Town FC_

- feeds sampled: `beaconsfieldtownfc-bookteq-com-api-open-active-slots` (Slot, n=500)

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://bedfordtownfootballclub.bookteq.com/api/open-active
_publisher: Bedford Town Football Club_

- feeds sampled: `bedfordtownfootballclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=14), `bedfordtownfootballclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 14)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 14)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 14)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 84)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 14)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 14)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 14)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://berkscountyfc.bookteq.com/api/open-active

- feeds sampled: `berkscountyfc-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=9), `berkscountyfc-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 9)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 9)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 9)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 15)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 9)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 9)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 9)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://better-admin.org.uk/api/openactive/better
_publisher: Better_

- feeds sampled: `better-admin-org-uk-api-openactive-better-facility-uses` (FacilityUse, n=500), `better-admin-org-uk-api-openactive-better-scheduled-sessions` (ScheduledSession, n=500), `better-admin-org-uk-api-openactive-better-session-series` (SessionSeries, n=500), `better-admin-org-uk-api-openactive-better-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 192)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 955)

- present: @type, name, value

### Concept  (instances sampled: 2,632)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 570)

- present: @type, name, value

### FacilityUse  (instances sampled: 500)

- present: @id, @type, endDate, facilityType, individualFacilityUse, location, name, provider, startDate, url, beta:facilitySetting, beta:formattedDescription, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, identifier, image, offers, potentialAction

### GeoCoordinates  (instances sampled: 1,000)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 78)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### IndividualFacilityUse  (instances sampled: 1,443)

- present: @id, @type, hoursAvailable, name, url, beta:facilitySetting, beta:isWheelchairAccessible
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, attendeeInstructions, category, description, event, identifier, image, location, offers, potentialAction, provider

### LocationFeatureSpecification (nested)  (instances sampled: 6,880)

- present: @type, name, value

### Lockers (nested)  (instances sampled: 951)

- present: @type, name, value

### Offer  (instances sampled: 3,179)

- present: @type, acceptedPaymentMethod, name, price, priceCurrency, ageRestriction, beta:partySize
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 6,046)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1,000)

- present: @id, @type, email, identifier, name, taxMode, url
- absent (model): address, contactPoint, description, image, legalName, logo, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 938)

- present: @type, name, value

### PartialSchedule  (instances sampled: 25,898)

- present: @type, byDay, duration, endTime, repeatFrequency, scheduleTimezone, startDate, startTime, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 363)

- present: @type, givenName, familyName
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, name, sameAs, telephone, url

### Place  (instances sampled: 1,000)

- present: @id, @type, address, beta:formattedDescription, geo, name, openingHoursSpecification, description, amenityFeature, beta:placeType, email, telephone, url, image
- absent (model): containedInPlace, containsPlace, identifier

### PostalAddress  (instances sampled: 1,000)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,438)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent, url, offers, beta:isWheelchairAccessible, leader
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, name, organizer, potentialAction, programme, schedulingNote, subEvent

### SessionSeries  (instances sampled: 500)

- present: @id, @type, activity, beta:isScheduledAsSlots, endDate, eventSchedule, genderRestriction, identifier, isCoached, location, name, organizer, startDate, url, offers, beta:formattedDescription, beta:facilitySetting, description, leader, beta:isVirtuallyCoached, ageRange, level, accessibilitySupport
- absent (model): accessibilityInformation, attendeeInstructions, category, contributor, duration, eventStatus, image, isAccessibleForFree, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 949)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, isOpenBookingWithCustomerAccountAllowed, maximumUses, remainingUses, startDate, url, offers
- absent (model): —

### Toilets (nested)  (instances sampled: 968)

- present: @type, name, value

### Towels (nested)  (instances sampled: 555)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 626)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 737)

- present: @type, name, value

## https://betterflow.coursepro.co.uk/odi/feed
_publisher: Better_

- feeds sampled: `betterflow-coursepro-co-uk-odi-scheduled-sessions` (ScheduledSession, n=500), `betterflow-coursepro-co-uk-odi-session-series` (SessionSeries, n=500)

### Concept  (instances sampled: 1,000)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 1,000)

- present: @id, @type, activity, identifier, location, name, organizer, description, endDate, startDate
- absent (model): accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### GeoCoordinates  (instances sampled: 2,000)

- present: @type, latitude, longitude
- absent (model): —

### Offer  (instances sampled: 1,055)

- present: @type, price, priceCurrency, description
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 1,000)

- present: @id, @type, name, url
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, vatID

### Place  (instances sampled: 2,000)

- present: @type, geo, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### QuantitativeValue (nested)  (instances sampled: 1,000)

- present: @type, maxValue, minValue

### Schedule  (instances sampled: 1,000)

- present: @type, byDay, endTime, scheduleTimezone, scheduledEventType, startTime
- absent (model): byMonth, byMonthDay, duration, endDate, exceptDate, idTemplate, repeatCount, repeatFrequency, startDate, urlTemplate

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, duration, endDate, identifier, remainingAttendeeCapacity, startDate, superEvent, url
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent

### SessionSeries  (instances sampled: 1,000)

- present: @id, @type, ageRange, endDate, eventSchedule, eventStatus, identifier, location, maximumAttendeeCapacity, name, offers, startDate, superEvent, url
- absent (model): accessibilityInformation, accessibilitySupport, activity, attendeeInstructions, category, contributor, description, duration, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, meetingPoint, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

## https://bewellwigan.gs-signature.cloud/OpenActive/
_publisher: Wigan Leisure and Culture Trust_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-WiganLeisureandCultureTrust-live-facility-uses` (FacilityUse, n=58), `opendata-leisurecloud-live-api-feeds-WiganLeisureandCultureTrust-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-WiganLeisureandCultureTrust-live-slots` (Slot, n=500)

### FacilityUse  (instances sampled: 58)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction, url

### Offer  (instances sampled: 2,801)

- present: @type, price, priceCurrency, description, identifier, name, ageRestriction
- absent (model): @id, acceptedPaymentMethod, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 406)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 558)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 558)

- present: @type, address, identifier, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 558)

- present: @type
- absent (model): addressCountry, addressLocality, addressRegion, postalCode, streetAddress

### QuantitativeValue (nested)  (instances sampled: 1,424)

- present: @type, minValue, maxValue

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, genderRestriction, identifier, location, name, offers, organizer, startDate, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 952)

- present: @type, identifier, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### beta:IndicativeOffer (nested)  (instances sampled: 206)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://bishopchallonersportscentre.bookteq.com/api/open-active
_publisher: Bishop Challoner Sports Centre_

- feeds sampled: `bishopchallonersportscentre-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=22), `bishopchallonersportscentre-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 22)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 22)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 22)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 142)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 22)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 22)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 22)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://blackburnwithdarwen-openactive.legendonlineservices.co.uk/OpenActive
_publisher: BwD Leisure_

- feeds sampled: `blackburnwithdarwen-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=15), `blackburnwithdarwen-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `blackburnwithdarwen-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 515)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 15)

- present: activity, endDate, id, identifier, location, name, provider, startDate, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 515)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,180)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 515)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 458)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 262)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 515)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 515)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 850)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://blueflamessportingclublimited.bookteq.com/api/open-active
_publisher: Blue Flames Sporting Club Limited_

- feeds sampled: `blueflamessportingclublimited-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=20), `blueflamessportingclublimited-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 20)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 20)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 20)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 140)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 20)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 20)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 20)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://bolderacademy.bookteq.com/api/open-active
_publisher: Bolder Academy_

- feeds sampled: `bolderacademy-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=36), `bolderacademy-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 36)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 36)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 36)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 210)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 36)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 36)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 36)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://boltonarena-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `boltonarena-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=12), `boltonarena-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `boltonarena-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 512)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 12)

- present: activity, endDate, id, identifier, location, name, provider, startDate, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 512)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 512)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 469)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 482)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 512)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 512)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 17)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://bridportleisure-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `bridportleisure-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=1)

### FacilityUse  (instances sampled: 1)

- present: endDate, startDate
- absent (model): @id, @type, accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, identifier, image, individualFacilityUse, location, name, offers, potentialAction, provider, url

## https://brimhamsactive.gs-signature.cloud/OpenActive/
_publisher: Brimhams Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-BrimhamsActive-live-facility-uses` (FacilityUse, n=9), `opendata-leisurecloud-live-api-feeds-BrimhamsActive-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-BrimhamsActive-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-BrimhamsActive-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 509)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 509)

- present: @type, name, value

### Creche (nested)  (instances sampled: 509)

- present: @type, name, value

### FacilityUse  (instances sampled: 9)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 509)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 509)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 509)

- present: @type, name, value

### Offer  (instances sampled: 2,329)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 2,357)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 509)

- present: @id, @type, beta:formattedDescription, email, legalName, logo, name, sameAs, url
- absent (model): address, contactPoint, description, identifier, image, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 509)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 509)

- present: @type, address, amenityFeature, beta:formattedDescription, geo, identifier, name, telephone, url, openingHoursSpecification
- absent (model): @id, containedInPlace, containsPlace, description, image

### PostalAddress  (instances sampled: 509)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,363)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, organizer, startDate, url, genderRestriction, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 509)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,737)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 509)

- present: @type, name, value

### Towels (nested)  (instances sampled: 509)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 509)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 509)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 33)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://broughtontowncouncil.bookteq.com/api/open-active
_publisher: Broughton Town Council _

- feeds sampled: `broughtontowncouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=39), `broughtontowncouncil-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 39)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 39)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 39)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 224)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 39)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 39)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 39)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://bryntegschool.bookteq.com/api/open-active
_publisher: Brynteg School_

- feeds sampled: `bryntegschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=38), `bryntegschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 38)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 38)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 38)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 240)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 38)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 38)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 38)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://castlepoint.gs-signature.cloud/OpenActive/
_publisher: Castlepoint_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-Castlepoint-live-facility-uses` (FacilityUse, n=6), `opendata-leisurecloud-live-api-feeds-Castlepoint-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-Castlepoint-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-Castlepoint-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 496)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 496)

- present: @type, name, value

### Concept  (instances sampled: 521)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 496)

- present: @type, name, value

### EventSeries  (instances sampled: 453)

- present: @type, activity, beta:formattedDescription, endDate, identifier, level, name, organizer, startDate, description, ageRange, genderRestriction, isCoached, attendeeInstructions, image, beta:isVirtuallyCoached, accessibilitySupport, beta:isWheelchairAccessible
- absent (model): @id, accessibilityInformation, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 6)

- present: @id, @type, activity, alternateName, beta:formattedDescription, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, beta:facilityType, description, beta:facilitySetting, beta:isWheelchairAccessible
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, event, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 496)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 8,128)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 496)

- present: @type, name, value

### Offer  (instances sampled: 510)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,514)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 506)

- present: @id, @type, beta:formattedDescription, description, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 496)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, scheduleTimezone, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 506)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, description, geo, image, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 506)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 453)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, superEvent, attendeeInstructions, organizer, genderRestriction, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 496)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,201)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 496)

- present: @type, name, value

### Towels (nested)  (instances sampled: 496)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 496)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 496)

- present: @type, name, value

## https://chauncyschool.bookteq.com/api/open-active
_publisher: Chauncy School_

- feeds sampled: `chauncyschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=25), `chauncyschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 25)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 25)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 25)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 140)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 25)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 25)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 25)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://chelmsfordcitysports.gs-signature.cloud/OpenActive/
_publisher: Chelmsford City Sports_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-ChelmsfordCitySports-live-facility-uses` (FacilityUse, n=54), `opendata-leisurecloud-live-api-feeds-ChelmsfordCitySports-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-ChelmsfordCitySports-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-ChelmsfordCitySports-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 554)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 554)

- present: @type, name, value

### Concept  (instances sampled: 340)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 554)

- present: @type, name, value

### EventSeries  (instances sampled: 284)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, name, organizer, startDate, description, ageRange, isCoached, level, beta:isVirtuallyCoached, attendeeInstructions, beta:isWheelchairAccessible
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 54)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions, activity, alternateName, beta:formattedDescription, beta:facilityType, beta:isWheelchairAccessible, beta:facilitySetting
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 554)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 952)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 554)

- present: @type, name, value

### Offer  (instances sampled: 2,562)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 2,044)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 554)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### Parking (nested)  (instances sampled: 554)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 554)

- present: @type, address, amenityFeature, beta:formattedDescription, description, geo, identifier, name, telephone, url, image, openingHoursSpecification
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 554)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 2,100)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, offers, startDate, url, attendeeInstructions, superEvent, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 554)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,532)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 554)

- present: @type, name, value

### Towels (nested)  (instances sampled: 554)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 554)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 554)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 277)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://connect.pembrokeshire.gov.uk/OpenActive/
_publisher: Pembrokeshire Leisure_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-Pembrokeshire-live-course-instance` (CourseInstance, n=2), `opendata-leisurecloud-live-api-feeds-Pembrokeshire-live-facility-uses` (FacilityUse, n=65), `opendata-leisurecloud-live-api-feeds-Pembrokeshire-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-Pembrokeshire-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-Pembrokeshire-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 515)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 515)

- present: @type, name, value

### Concept  (instances sampled: 410)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 2)

- present: @id, @type, author, category, genderRestriction, name
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, contributor, description, duration, endDate, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 2)

- present: @id, @type, attendeeInstructions, category, duration, endDate, eventStatus, identifier, instanceOfCourse, location, maximumAttendeeCapacity, name, organizer, remainingAttendeeCapacity, startDate, subEvent, url, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 515)

- present: @type, name, value

### Event  (instances sampled: 3)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 374)

- present: @type, activity, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, ageRange, description, beta:isWheelchairAccessible, isCoached, level, beta:isVirtuallyCoached
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 65)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, activity, alternateName, beta:facilityType, beta:formattedDescription, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 515)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 567)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 515)

- present: @type, name, value

### Offer  (instances sampled: 1,489)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 4,060)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 567)

- present: @id, @type, beta:formattedDescription, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, description, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 515)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, scheduleTimezone, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 567)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, description, geo, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace, image

### PostalAddress  (instances sampled: 567)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 796)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 515)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,542)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 515)

- present: @type, name, value

### Towels (nested)  (instances sampled: 515)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 515)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 515)

- present: @type, name, value

## https://conwy.gs-signature.cloud/OpenActive/
_publisher: Conwy_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-Conwy-live-facility-uses` (FacilityUse, n=30), `opendata-leisurecloud-live-api-feeds-Conwy-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-Conwy-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-Conwy-live-slots` (Slot, n=500)

### FacilityUse  (instances sampled: 30)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, offers, potentialAction, url

### Offer  (instances sampled: 500)

- present: @type, price, priceCurrency
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 210)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 530)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 530)

- present: @type, address, identifier, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 530)

- present: @type
- absent (model): addressCountry, addressLocality, addressRegion, postalCode, streetAddress

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, genderRestriction, identifier, location, name, organizer, startDate, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,211)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

## https://coramsfields.bookteq.com/api/open-active
_publisher: Coram's Fields_

- feeds sampled: `coramsfields-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=10), `coramsfields-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 10)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 10)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 10)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 55)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 10)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 10)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 10)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://coramsfieldsindoorspaces.bookteq.com/api/open-active
_publisher: Coram's Fields_

- feeds sampled: `coramsfieldsindoorspaces-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=7), `coramsfieldsindoorspaces-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 7)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 7)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 7)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 40)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 7)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 7)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 7)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://danburyparishcouncil.bookteq.com/api/open-active
_publisher: Danbury Parish Council_

- feeds sampled: `danburyparishcouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=16), `danburyparishcouncil-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 16)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 16)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 16)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 77)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 16)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 16)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 16)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://data.bookwhen.com/
_publisher: Bookwhen_

- feeds sampled: `bookwhen-com-api-openactive-courseinstances` (CourseInstance, n=469), `bookwhen-com-api-openactive-events` (Event, n=316), `bookwhen-com-api-openactive-scheduledsessions` (ScheduledSession, n=500), `bookwhen-com-api-openactive-sessionseries` (SessionSeries, n=500)

### BabyChanging (nested)  (instances sampled: 746)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 753)

- present: @type, name, value

### Concept  (instances sampled: 2,050)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### CourseInstance  (instances sampled: 469)

- present: @id, @type, activity, beta:formattedDescription, beta:participantSuppliedEquipment, description, endDate, eventAttendanceMode, genderRestriction, name, organizer, startDate, url, offers, eventSchedule, duration, subEvent, category, attendeeInstructions, location, maximumAttendeeCapacity, image, level, beta:virtualLocation, ageRange, isCoached, accessibilityInformation, specialRequirements, leader, beta:isInteractivityPreferred, beta:isWheelchairAccessible, accessibilitySupport, beta:donationPaymentUrl, isAccessibleForFree
- absent (model): contributor, eventStatus, identifier, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 753)

- present: @type, name, value

### Event  (instances sampled: 316)

- present: @id, @type, activity, beta:attendeeCount, beta:formattedDescription, beta:participantSuppliedEquipment, description, duration, endDate, eventAttendanceMode, genderRestriction, name, organizer, startDate, url, offers, remainingAttendeeCapacity, location, maximumAttendeeCapacity, attendeeInstructions, image, ageRange, category, level, leader, isCoached, beta:virtualLocation, beta:isWheelchairAccessible, isAccessibleForFree, accessibilityInformation, specialRequirements, accessibilitySupport
- absent (model): contributor, eventSchedule, eventStatus, identifier, meetingPoint, potentialAction, programme, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 1,103)

- present: latitude, longitude, type
- absent (model): —

### ImageObject  (instances sampled: 3,331)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 753)

- present: @type, name, value

### Offer  (instances sampled: 2,310)

- present: @type, price, name, priceCurrency, description, beta:partySize, validFrom, validThrough
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 1,285)

- present: @id, @type, name, email, url, telephone, beta:formalCriteriaMet
- absent (model): address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, vatID

### Parking (nested)  (instances sampled: 753)

- present: @type, name, value

### PartialSchedule  (instances sampled: 182)

- present: @type, duration, endTime, idTemplate, repeatFrequency, scheduleTimezone, scheduledEventType, startDate, startTime, urlTemplate, byDay, exceptDate
- absent (model): byMonth, byMonthDay, endDate, repeatCount

### Person  (instances sampled: 164)

- present: @id, @type, identifier, name
- absent (model): contactPoint, description, email, gender, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 1,110)

- present: @id, @type, address, name, geo, amenityFeature, description, telephone
- absent (model): containedInPlace, containsPlace, identifier, image, openingHoursSpecification, url

### QuantitativeValue (nested)  (instances sampled: 963)

- present: @type, maxValue, minValue

### Schedule  (instances sampled: 776)

- present: @type, duration, endTime, idTemplate, repeatCount, repeatFrequency, scheduleTimezone, scheduledEventType, startDate, startTime, urlTemplate, byDay, exceptDate, endDate, byMonthDay
- absent (model): byMonth

### ScheduledSession  (instances sampled: 2,939)

- present: @type, duration, endDate, startDate, url, @id, beta:attendeeCount, superEvent, remainingAttendeeCapacity, leader, beta:virtualLocation
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, identifier, image, isAccessibleForFree, isCoached, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent

### SessionSeries  (instances sampled: 500)

- present: @id, @type, activity, beta:participantSuppliedEquipment, endDate, eventAttendanceMode, genderRestriction, name, organizer, startDate, url, beta:formattedDescription, description, eventSchedule, location, attendeeInstructions, maximumAttendeeCapacity, offers, category, image, level, isCoached, subEvent, beta:virtualLocation, ageRange, beta:isWheelchairAccessible, specialRequirements, leader, accessibilityInformation, beta:isInteractivityPreferred, accessibilitySupport, isAccessibleForFree, beta:donationPaymentUrl
- absent (model): contributor, duration, eventStatus, identifier, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, superEvent

### Showers (nested)  (instances sampled: 753)

- present: @type, name, value

### Toilets (nested)  (instances sampled: 746)

- present: @type, name, value

### Towels (nested)  (instances sampled: 753)

- present: @type, name, value

### VirtualLocation (nested)  (instances sampled: 228)

- present: @id, @type, name, description

## https://data.englandnetball.co.uk/
_publisher: England Netball_

- feeds sampled: `api-englandnetball-co-uk-api-openactive-sessions` (CourseInstance, n=33), `api-englandnetball-co-uk-api-openactive-sessions` (ScheduledSession, n=500)

### Brand  (instances sampled: 500)

- present: @type, name, beta:video, description, logo, url
- absent (model): @id, identifier, video

### Concept  (instances sampled: 566)

- present: inScheme, prefLabel, @id, @type, id, type
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 33)

- present: activity, author, beta:video, description, logo, name, type, url
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, duration, endDate, eventSchedule, eventStatus, genderRestriction, identifier, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent

### CourseInstance  (instances sampled: 33)

- present: @id, activity, ageRange, beta:course, category, endDate, eventSchedule, eventStatus, identifier, leader, level, location, maximumAttendeeCapacity, name, offers, organizer, participation_type, remainingAttendeeCapacity, startDate, type, url, sameAs
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, description, duration, genderRestriction, image, isAccessibleForFree, isCoached, meetingPoint, potentialAction, programme, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 533)

- present: latitude, longitude, @type, type
- absent (model): —

### ImageObject  (instances sampled: 531)

- present: url, @type, type
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 565)

- present: name, price, priceCurrency, @type, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 566)

- present: @id, name, url, @type, sameAs, telephone, type
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, taxID, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, endDate, repeatFrequency
- absent (model): byDay, byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, startDate, startTime, urlTemplate

### Person  (instances sampled: 533)

- present: email, name, @type, telephone, jobTitle, type
- absent (model): @id, contactPoint, description, gender, identifier, image, sameAs, url

### Place  (instances sampled: 533)

- present: address, geo, name, @type, telephone, type, url, description
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification

### PostalAddress  (instances sampled: 533)

- present: addressCountry, postalCode, @type, streetAddress, addressLocality, addressRegion, type
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 33)

- present: maxValue, minValue, type

### Schedule  (instances sampled: 33)

- present: duration, endDate, endTime, repeatCount, repeatFrequency, scheduledEventType, startDate, startTime, type
- absent (model): byDay, byMonth, byMonthDay, exceptDate, idTemplate, urlTemplate

### ScheduledSession  (instances sampled: 500)

- present: @id, duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, participation_type, remainingAttendeeCapacity, startDate, superEvent, type, url
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent

### SessionSeries  (instances sampled: 500)

- present: @id, activity, category, endDate, eventSchedule, identifier, leader, level, location, name, offers, organizer, participation_type, programme, startDate, type, url, description
- absent (model): accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, maximumAttendeeCapacity, meetingPoint, potentialAction, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

## https://data.everyoneactive.com/OpenActive/
_publisher: Everyone Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-EveryoneActive-live-course-instance` (CourseInstance, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-live-facility-uses` (FacilityUse, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 1,395)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 1,395)

- present: @type, name, value

### Concept  (instances sampled: 1,701)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 500)

- present: @id, @type, activity, ageRange, author, beta:formattedDescription, category, description, genderRestriction, level, name, image
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, duration, endDate, eventSchedule, eventStatus, identifier, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventStatus, identifier, instanceOfCourse, isCoached, level, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent, url, image, additionalAdmissionRestriction, attendeeInstructions, beta:isWheelchairAccessible
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, isAccessibleForFree, leader, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 1,395)

- present: @type, name, value

### Event  (instances sampled: 1,000)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 500)

- present: @type, activity, beta:formattedDescription, description, endDate, genderRestriction, identifier, level, name, organizer, startDate, image, ageRange, isCoached, beta:isVirtuallyCoached, accessibilityInformation, attendeeInstructions
- absent (model): @id, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 500)

- present: @id, @type, activity, alternateName, beta:facilitySetting, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, beta:formattedDescription, description, image, attendeeInstructions, beta:facilityType
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 1,395)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 3,378)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 1,395)

- present: @type, name, value

### Offer  (instances sampled: 3,394)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 13,230)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1,500)

- present: @id, @type, beta:formattedDescription, beta:video, description, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, email, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 1,395)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, byDay, duration, endTime, startDate, startTime, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 1,500)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, geo, url, telephone, openingHoursSpecification, image
- absent (model): @id, containedInPlace, containsPlace, description

### PostalAddress  (instances sampled: 1,500)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 5,758)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent, additionalAdmissionRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, superEvent, url, attendeeInstructions, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 1,395)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate, additionalAdmissionRestriction
- absent (model): —

### SportsActivityLocation  (instances sampled: 3,160)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 1,395)

- present: @type, name, value

### Towels (nested)  (instances sampled: 1,395)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 1,500)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 1,395)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 1,395)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 3,787)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://debdaleparksports.bookteq.com/api/open-active
_publisher: Debdale Park Sports & Recreation Club_

- feeds sampled: `debdaleparksports-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=17), `debdaleparksports-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 17)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 17)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 17)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 103)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 17)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 17)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 17)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://derbyactive-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Derby Active_

- feeds sampled: `derbyactive-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=15), `derbyactive-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `derbyactive-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 782)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 15)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 508)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 512)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 61)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 451)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 512)

- present: address, identifier, name, type, geo, telephone, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 512)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 465)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://dev.myeveryoneactive.com/OpenActive/
_publisher: Everyone Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-EveryoneActive-test-course-instance` (CourseInstance, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-test-facility-uses` (FacilityUse, n=75), `opendata-leisurecloud-live-api-feeds-EveryoneActive-test-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-test-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActive-test-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 1,075)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 1,075)

- present: @type, name, value

### Concept  (instances sampled: 1,049)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 500)

- present: @id, @type, activity, ageRange, author, beta:formattedDescription, category, description, genderRestriction, level, name
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, duration, endDate, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventStatus, identifier, instanceOfCourse, isCoached, level, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent, url, additionalAdmissionRestriction, beta:isWheelchairAccessible, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, leader, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 1,075)

- present: @type, name, value

### Event  (instances sampled: 1,000)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 451)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, level, name, organizer, startDate, ageRange, description, image, isCoached, beta:isVirtuallyCoached, attendeeInstructions
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 75)

- present: @id, @type, activity, alternateName, beta:facilitySetting, beta:formattedDescription, beta:offerValidityPeriod, category, description, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, image, attendeeInstructions, beta:facilityType
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 1,075)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 1,652)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 1,075)

- present: @type, name, value

### Offer  (instances sampled: 3,095)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 8,046)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1,075)

- present: @id, @type, beta:formattedDescription, beta:video, description, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, email, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 1,075)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 1,075)

- present: @type, address, amenityFeature, beta:formattedDescription, geo, identifier, name, openingHoursSpecification, telephone, url, image, description
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 1,075)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 3,225)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent, additionalAdmissionRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, attendeeInstructions, offers, superEvent, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 1,075)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate, additionalAdmissionRestriction
- absent (model): —

### SportsActivityLocation  (instances sampled: 3,068)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 1,075)

- present: @type, name, value

### Towels (nested)  (instances sampled: 1,075)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 1,075)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 1,075)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 1,075)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 580)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://didcottowncouncil.bookteq.com/api/open-active
_publisher: Didcot Town Council_

- feeds sampled: `didcottowncouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=39), `didcottowncouncil-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 39)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 39)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 39)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 222)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 39)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 39)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 39)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://ealingboroughcouncil.bookteq.com/api/open-active
_publisher: London Borough of Ealing Council_

- feeds sampled: `ealingboroughcouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=43), `ealingboroughcouncil-bookteq-com-api-open-active-slots` (Slot, n=8)

### Concept  (instances sampled: 43)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 43)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 43)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 8)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 2)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 43)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 43)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 43)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 8)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://earlsdon.bookteq.com/api/open-active
_publisher: Earlsdon Rugby Club_

- feeds sampled: `earlsdon-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=8), `earlsdon-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 8)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 8)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 8)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 28)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 8)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 8)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 8)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://eastmidlandsacademytrust.bookteq.com/api/open-active
_publisher: East Midlands Academy Trust_

- feeds sampled: `eastmidlandsacademytrust-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=25), `eastmidlandsacademytrust-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 25)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 25)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 25)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 175)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 25)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 25)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 25)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://eireoggaa.bookteq.com/api/open-active
_publisher: Eire Og GAA_

- feeds sampled: `eireoggaa-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=18), `eireoggaa-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 18)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 18)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 18)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 119)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 18)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 18)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 18)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://elgarparkregionalhockeyassociation.bookteq.com/api/open-active
_publisher: Elgar Park Regional Hockey Association_

- feeds sampled: `elgarparkregionalhockeyassociation-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=17), `elgarparkregionalhockeyassociation-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 17)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 17)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 17)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 103)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 17)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 17)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 17)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://enfielddrillhallsportsclub.bookteq.com/api/open-active
_publisher: Enfield Drill Hall Sports Club_

- feeds sampled: `enfielddrillhallsportsclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=9), `enfielddrillhallsportsclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 9)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 9)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 9)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 35)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 9)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 9)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 9)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://featherstonesportscentre.bookteq.com/api/open-active
_publisher: Featherstone Sports Centre Trust_

- feeds sampled: `featherstonesportscentre-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=57), `featherstonesportscentre-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 57)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 57)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 57)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 310)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 57)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 57)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 57)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://fleetcc.bookteq.com/api/open-active
_publisher: Mark Allen_

- feeds sampled: `fleetcc-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=2), `fleetcc-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 2)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 2)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 2)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 14)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 2)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 2)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 2)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://football567.bookteq.com/api/open-active
_publisher: Football 567_

- feeds sampled: `football567-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=3), `football567-bookteq-com-api-open-active-slots` (Slot, n=240)

### Concept  (instances sampled: 3)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 3)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 3)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 240)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 13)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 3)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 3)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 3)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 240)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://footballsamuraiacademylimited.bookteq.com/api/open-active
_publisher: Football Samurai Academy Limited _

- feeds sampled: `footballsamuraiacademylimited-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=4), `footballsamuraiacademylimited-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 4)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 4)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 4)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 28)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 4)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 4)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 4)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://fyldecoastymca.gs-signature.cloud/OpenActive/
_publisher: Fylde Coast YMCA_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-FyldeCoastYMCA-live-facility-uses` (FacilityUse, n=12), `opendata-leisurecloud-live-api-feeds-FyldeCoastYMCA-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-FyldeCoastYMCA-live-session-series` (SessionSeries, n=463), `opendata-leisurecloud-live-api-feeds-FyldeCoastYMCA-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 95)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 95)

- present: @type, name, value

### Concept  (instances sampled: 378)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 95)

- present: @type, name, value

### EventSeries  (instances sampled: 355)

- present: @type, activity, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, description, isCoached, beta:isVirtuallyCoached, level, accessibilityInformation, accessibilitySupport, ageRange, beta:isWheelchairAccessible
- absent (model): @id, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 12)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions, activity, alternateName, beta:formattedDescription, beta:facilitySetting, beta:facilityType, beta:isWheelchairAccessible
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 473)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 172)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 95)

- present: @type, name, value

### Offer  (instances sampled: 2,053)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,374)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 475)

- present: @id, @type, legalName, name, beta:formattedDescription, description, email, logo, sameAs, url
- absent (model): address, contactPoint, identifier, image, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 95)

- present: @type, name, value

### PartialSchedule  (instances sampled: 463)

- present: @type, duration, endTime, startDate, startTime, scheduleTimezone, byDay
- absent (model): byMonth, byMonthDay, endDate, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 475)

- present: @type, address, identifier, name, beta:formattedDescription, geo, telephone, url, openingHoursSpecification, amenityFeature, description, image
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 475)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 753)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 463)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 95)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,199)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 95)

- present: @type, name, value

### Towels (nested)  (instances sampled: 95)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 95)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 95)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 47)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://fz2024ltd.bookteq.com/api/open-active
_publisher: FZ 2024 Ltd_

- feeds sampled: `fz2024ltd-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=3), `fz2024ltd-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 3)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 3)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 3)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 5)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 3)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 3)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 3)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://gmcommunitylettings.bookteq.com/api/open-active
_publisher: gmcommunitylettings_

- feeds sampled: `gmcommunitylettings-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=121), `gmcommunitylettings-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 121)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 121)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 121)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 505)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 121)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 121)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 121)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://goteamup.com/api/openactive/v1/
_publisher: TeamUp_

- feeds sampled: `goteamup-com-api-openactive-v1-events` (Event, n=500), `goteamup-com-api-openactive-v1-scheduledsessions` (ScheduledSession, n=500), `goteamup-com-api-openactive-v1-sessionseries` (SessionSeries, n=500)

### Concept  (instances sampled: 477)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: @id, @type, duration, endDate, eventAttendanceMode, offers, startDate, superEvent, url, location, maximumAttendeeCapacity, remainingAttendeeCapacity, name, beta:virtualLocation, isAccessibleForFree
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, identifier, image, isCoached, leader, level, meetingPoint, organizer, potentialAction, programme, schedulingNote, subEvent

### EventSeries  (instances sampled: 1,000)

- present: @id, @type, beta:formattedDescription, description, endDate, name, organizer, startDate, url, activity, ageRange, genderRestriction, level
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 956)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 1,000)

- present: type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 1,000)

- present: @type, price, url, eligibleCustomerType, priceCurrency
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, validFromBeforeStartDate

### Organization  (instances sampled: 1,000)

- present: @id, @type, beta:formalCriteriaMet, logo, name, url, description
- absent (model): address, contactPoint, email, identifier, image, legalName, sameAs, taxID, telephone, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, byDay, duration, endTime, repeatFrequency, scheduleTimezone, startDate, startTime, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Place  (instances sampled: 977)

- present: @id, name, type, address, geo
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 956)

- present: addressCountry, type, addressLocality, postalCode, streetAddress, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 477)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, duration, endDate, name, startDate, superEvent, url, maximumAttendeeCapacity, remainingAttendeeCapacity
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, identifier, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, offers, organizer, potentialAction, programme, schedulingNote, subEvent

### SessionSeries  (instances sampled: 500)

- present: @id, @type, endDate, eventAttendanceMode, eventSchedule, location, offers, startDate, superEvent, url, beta:virtualLocation, isAccessibleForFree
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, duration, eventStatus, genderRestriction, identifier, image, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### VirtualLocation (nested)  (instances sampled: 44)

- present: @type, name

## https://graveshamlegendsports.bookteq.com/api/open-active
_publisher: Gravesham Legend Sports Ltd_

- feeds sampled: `graveshamlegendsports-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=9), `graveshamlegendsports-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 9)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 9)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 9)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 29)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 9)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 9)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 9)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://halo-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Halo_

- feeds sampled: `halo-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=121), `halo-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `halo-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 625)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 121)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 598)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,086)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 600)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 493)

- present: endDate, repeatFrequency, startDate, startTime, type, byDay
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 20)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 600)

- present: address, identifier, name, type, geo, telephone, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 600)

- present: addressCountry, postalCode, streetAddress, type, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 527)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://harbornecricketclub.bookteq.com/api/open-active
_publisher: Harborne Cricket Club_

- feeds sampled: `harbornecricketclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=8), `harbornecricketclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 8)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 8)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 8)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 14)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 8)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 8)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 8)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://haringeycouncil.bookteq.com/api/open-active
_publisher: Haringey Council_

- feeds sampled: `haringeycouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=54), `haringeycouncil-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 54)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 54)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 54)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 99)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 54)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 54)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 54)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://harpurhillsportscentrecic.bookteq.com/api/open-active
_publisher: Harpur Hill Sports Centre CIC_

- feeds sampled: `harpurhillsportscentrecic-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=28), `harpurhillsportscentrecic-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 28)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 28)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 28)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 196)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 28)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 28)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 28)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://hcandl-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `hcandl-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500)

### Offer  (instances sampled: 500)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://hillviewprimaryschool.bookteq.com/api/open-active
_publisher: Hill View Primary School_

- feeds sampled: `hillviewprimaryschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=5), `hillviewprimaryschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 5)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 5)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 5)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 35)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 5)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 5)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 5)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://hollingworthlearningtrust.bookteq.com/api/open-active

- feeds sampled: `hollingworthlearningtrust-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=13), `hollingworthlearningtrust-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 13)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 13)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 13)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 61)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 13)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 13)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 13)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://horizonlc-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `horizonlc-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=13), `horizonlc-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `horizonlc-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 1,376)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 13)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 511)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,298)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 511)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 404)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 155)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 511)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 511)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,153)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://hythecsc.bookteq.com/api/open-active
_publisher: Hythe Cricket & Squash Club_

- feeds sampled: `hythecsc-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=11), `hythecsc-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 11)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 11)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 11)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 49)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 11)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 11)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 11)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://idverdecharnwood.bookteq.com/api/open-active
_publisher: ID Verde Charnwood_

- feeds sampled: `idverdecharnwood-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=31), `idverdecharnwood-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 31)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 31)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 31)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 469)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 31)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 31)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 31)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://inside.ledleisure.co.uk/OpenActive/
_publisher: LED Leisure Management Ltd_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-LED-live-live-facility-uses` (FacilityUse, n=2), `opendata-leisurecloud-live-api-feeds-LED-live-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-LED-live-live-session-series` (SessionSeries, n=74)

### BabyChanging (nested)  (instances sampled: 74)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 74)

- present: @type, name, value

### Concept  (instances sampled: 51)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 74)

- present: @type, name, value

### EventSeries  (instances sampled: 46)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, name, organizer, startDate, attendeeInstructions, description, image, isCoached, level, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 2)

- present: @id, @type, activity, alternateName, attendeeInstructions, beta:facilitySetting, beta:facilityType, beta:formattedDescription, beta:offerValidityPeriod, category, description, endDate, hoursAvailable, identifier, image, location, name, offers, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 74)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 502)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 74)

- present: @type, name, value

### Offer  (instances sampled: 152)

- present: @type, description, identifier, name, price, priceCurrency, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 14)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 76)

- present: @id, @type, beta:formattedDescription, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, description, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 74)

- present: @type, name, value

### PartialSchedule  (instances sampled: 74)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 76)

- present: @type, address, beta:formattedDescription, identifier, name, telephone, url, amenityFeature, description, geo, image
- absent (model): @id, containedInPlace, containsPlace, openingHoursSpecification

### PostalAddress  (instances sampled: 76)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 94)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 74)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 74)

- present: @type, name, value

### SportsActivityLocation  (instances sampled: 500)

- present: @type, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, identifier, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 74)

- present: @type, name, value

### Towels (nested)  (instances sampled: 74)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 74)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 74)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 13)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://jmosportslimited.bookteq.com/api/open-active
_publisher: JMO Sports Limited_

- feeds sampled: `jmosportslimited-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=17), `jmosportslimited-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 17)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 17)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 17)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 119)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 17)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 17)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 17)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://jubileehall-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `jubileehall-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=4)

### Concept  (instances sampled: 5)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### FacilityUse  (instances sampled: 4)

- present: activity, endDate, id, identifier, location, name, provider, startDate, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 4)

- present: latitude, longitude, type
- absent (model): —

### Organization  (instances sampled: 4)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 4)

- present: address, geo, identifier, name, telephone, type
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification, url

### PostalAddress  (instances sampled: 4)

- present: addressCountry, addressLocality, postalCode, streetAddress, type
- absent (model): addressRegion

## https://kingswayparkhighschool.bookteq.com/api/open-active
_publisher: Kingsway Park High School_

- feeds sampled: `kingswayparkhighschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=24), `kingswayparkhighschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 24)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 24)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 24)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 139)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 24)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 24)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 24)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://lamptonleisure.gs-signature.cloud/OpenActive/
_publisher: Lampton Leisure_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-LamptonLeisure-live-facility-uses` (FacilityUse, n=32), `opendata-leisurecloud-live-api-feeds-LamptonLeisure-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-LamptonLeisure-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-LamptonLeisure-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 532)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 532)

- present: @type, name, value

### Concept  (instances sampled: 453)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 532)

- present: @type, name, value

### EventSeries  (instances sampled: 444)

- present: @type, activity, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, level, description, isCoached, attendeeInstructions, ageRange, accessibilitySupport, beta:isWheelchairAccessible
- absent (model): @id, accessibilityInformation, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 32)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### Lockers (nested)  (instances sampled: 532)

- present: @type, name, value

### Offer  (instances sampled: 972)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name
- absent (model): @id, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,948)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 532)

- present: @id, @type, beta:formattedDescription, description, legalName, name, url
- absent (model): address, contactPoint, email, identifier, image, logo, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 532)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 532)

- present: @type, address, amenityFeature, beta:formattedDescription, identifier, name, openingHoursSpecification, url, description
- absent (model): @id, containedInPlace, containsPlace, geo, image, telephone

### PostalAddress  (instances sampled: 532)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 18)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 532)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,147)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 532)

- present: @type, name, value

### Towels (nested)  (instances sampled: 532)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 532)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 532)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 32)

- present: @type, identifier, name, price, priceCurrency

## https://lancaster-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `lancaster-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=33), `lancaster-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `lancaster-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 516)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 33)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 516)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 516)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 500)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 476)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 516)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 516)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 18)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: description, endDate, eventSchedule, identifier, location, startDate, superEvent, type, url
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://langleygrange.bookteq.com/api/open-active
_publisher: Langley Grange Pool_

- feeds sampled: `langleygrange-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=7), `langleygrange-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 7)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 7)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 7)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 54)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 7)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 7)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 7)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://larkhallsportsclub.bookteq.com/api/open-active
_publisher: Larkhall Sports Club_

- feeds sampled: `larkhallsportsclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=23), `larkhallsportsclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 23)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 23)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 23)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 154)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 23)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 23)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 23)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://lawntennisassociation.github.io/
_publisher: Lawn Tennis Association_

- feeds sampled: `api-clubspark-uk-odi-public-courses` (SessionSeries, n=500)

### Concept  (instances sampled: 500)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### CourseFeatureSpecification (nested)  (instances sampled: 766)

- present: name, type, value

### GeoCoordinates  (instances sampled: 499)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 1,910)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 5,641)

- present: @type, identifier, name, price, priceCurrency, eligibleCustomerType
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 2,999)

- present: @id, @type, name, url, email, telephone, description, image
- absent (model): address, contactPoint, identifier, legalName, logo, sameAs, taxID, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, startDate, startTime, byDay, repeatFrequency
- absent (model): byMonth, byMonthDay, duration, endDate, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Place  (instances sampled: 500)

- present: @id, @type, address, name, geo
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 500)

- present: @type, addressCountry, postalCode, streetAddress, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 5,330)

- present: @type, unitCode, value, minValue, maxValue

### ScheduledSession  (instances sampled: 4,330)

- present: @id, @type, beta:estimatedDuration, category, eventStatus, isAccessibleForFree, isCoached, name, offers, startDate, url, description, organizer, maximumAttendeeCapacity
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, contributor, duration, endDate, eventSchedule, genderRestriction, identifier, image, leader, level, location, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### SessionSeries  (instances sampled: 500)

- present: @id, @type, activity, ageRange, beta:distance, beta:isWheelchairAccessible, category, endDate, eventSchedule, eventStatus, isAccessibleForFree, isCoached, level, location, name, offers, organizer, startDate, subEvent, url, description, courseFeatures, maximumAttendeeCapacity, genderRestriction, image
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, duration, identifier, leader, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, superEvent

## https://ledleisure.gs-signature.cloud/OpenActive/
_publisher: LED Community Leisure Ltd_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-LEDCommunityLeisureLtd-live-facility-uses` (FacilityUse, n=160), `opendata-leisurecloud-live-api-feeds-LEDCommunityLeisureLtd-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-LEDCommunityLeisureLtd-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-LEDCommunityLeisureLtd-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 626)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 626)

- present: @type, name, value

### Concept  (instances sampled: 645)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 626)

- present: @type, name, value

### EventSeries  (instances sampled: 492)

- present: @type, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, activity, description, attendeeInstructions, level, image, isCoached, ageRange, beta:isVirtuallyCoached, beta:isWheelchairAccessible
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 160)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, attendeeInstructions, activity, alternateName, beta:formattedDescription, beta:facilitySetting, image, beta:facilityType, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 625)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 2,945)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 626)

- present: @type, name, value

### Offer  (instances sampled: 1,298)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 1,120)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 660)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### Parking (nested)  (instances sampled: 626)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, scheduleTimezone, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 660)

- present: @type, address, identifier, name, beta:formattedDescription, telephone, url, amenityFeature, description, geo, image
- absent (model): @id, containedInPlace, containsPlace, openingHoursSpecification

### PostalAddress  (instances sampled: 660)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 519)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, offers, url, superEvent, attendeeInstructions, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 626)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,683)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 626)

- present: @type, name, value

### Towels (nested)  (instances sampled: 626)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 626)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 626)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 296)

- present: @type, identifier, name, price, priceCurrency, ageRestriction, description

## https://leisurecentre-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Parkwood Leisure Ltd, its subsidiaries and partner organisations_

- feeds sampled: `leisurecentre-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=127), `leisurecentre-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `leisurecentre-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 618)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 127)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 518)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,115)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 618)

- present: name, type, email
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 449)

- present: endDate, repeatFrequency, startDate, startTime, type, byDay
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 137)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 618)

- present: address, identifier, name, type, telephone, geo, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 618)

- present: addressCountry, postalCode, streetAddress, type, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 461)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://leisurefocus-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `leisurefocus-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=47), `leisurefocus-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `leisurefocus-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 530)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 47)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 530)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,566)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 530)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 483)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 105)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 530)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 530)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,395)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://leisuresk.leisurecloud.net/OpenActive/
_publisher: Leisure SK_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-LeisureSK-live-facility-uses` (FacilityUse, n=1), `opendata-leisurecloud-live-api-feeds-LeisureSK-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-LeisureSK-live-session-series` (SessionSeries, n=461), `opendata-leisurecloud-live-api-feeds-LeisureSK-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 462)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 462)

- present: @type, name, value

### Creche (nested)  (instances sampled: 462)

- present: @type, name, value

### FacilityUse  (instances sampled: 1)

- present: @id, @type, attendeeInstructions, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 148)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 462)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 462)

- present: @type, name, value

### Offer  (instances sampled: 1,790)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 7)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 462)

- present: @id, @type, beta:formattedDescription, description, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 462)

- present: @type, name, value

### PartialSchedule  (instances sampled: 461)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 462)

- present: @type, address, amenityFeature, beta:formattedDescription, description, identifier, name, telephone, url, geo
- absent (model): @id, containedInPlace, containsPlace, image, openingHoursSpecification

### PostalAddress  (instances sampled: 462)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 387)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 461)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, organizer, startDate, url, genderRestriction, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 462)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,000)

- present: @type, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, identifier, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 462)

- present: @type, name, value

### Towels (nested)  (instances sampled: 462)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 462)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 462)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 3)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://leisureworldmembership.leisurecloud.net/OpenActive/
_publisher: Colchester Leisure World_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-ColchesterLeisureWorld-live-facility-uses` (FacilityUse, n=51), `opendata-leisurecloud-live-api-feeds-ColchesterLeisureWorld-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-ColchesterLeisureWorld-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-ColchesterLeisureWorld-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 9)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 9)

- present: @type, name, value

### Creche (nested)  (instances sampled: 9)

- present: @type, name, value

### FacilityUse  (instances sampled: 51)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, attendeeInstructions, offers, url
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 9)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 13)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 9)

- present: @type, name, value

### Offer  (instances sampled: 1,589)

- present: @type, price, priceCurrency, description, identifier, name, ageRestriction
- absent (model): @id, acceptedPaymentMethod, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 359)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 551)

- present: @id, @type, legalName, name, beta:formattedDescription, description, email, logo, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 9)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, byDay, duration, endDate, endTime, startDate, startTime
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 551)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, geo, telephone, url
- absent (model): @id, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 551)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 379)

- present: @type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, genderRestriction, identifier, location, name, organizer, startDate, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### Showers (nested)  (instances sampled: 9)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,378)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 9)

- present: @type, name, value

### Towels (nested)  (instances sampled: 9)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 9)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 9)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 128)

- present: @type, identifier, name, price, priceCurrency, description, ageRestriction

## https://lifeleisure-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Life Leisure_

- feeds sampled: `lifeleisure-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=30), `lifeleisure-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `lifeleisure-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 791)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 30)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 525)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,617)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 525)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 485)

- present: endDate, repeatFrequency, startDate, startTime, type, byDay
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 1)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 525)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 525)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,872)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://lifestylefitness.bookteq.com/api/open-active
_publisher: Matthew Arnold Sports Centre_

- feeds sampled: `lifestylefitness-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=441), `lifestylefitness-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 441)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 441)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 441)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 1,526)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 441)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 441)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 441)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://lincsinspire-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `lincsinspire-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=4), `lincsinspire-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `lincsinspire-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 504)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, ageRange, genderRestriction, identifier, name, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 4)

- present: activity, endDate, id, identifier, location, name, provider, startDate, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 504)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 504)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 500)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 27)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 504)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 504)

- present: addressCountry, addressRegion, postalCode, streetAddress, type, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 500)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, eventSchedule, identifier, location, startDate, superEvent, type, url, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://lleisure.gs-signature.cloud/OpenActive/
_publisher: Liberty Leisure_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-LibertyLeisure-live-facility-uses` (FacilityUse, n=31), `opendata-leisurecloud-live-api-feeds-LibertyLeisure-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-LibertyLeisure-live-session-series` (SessionSeries, n=413), `opendata-leisurecloud-live-api-feeds-LibertyLeisure-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 342)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 342)

- present: @type, name, value

### Concept  (instances sampled: 354)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 342)

- present: @type, name, value

### EventSeries  (instances sampled: 330)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, name, organizer, startDate, ageRange, description, isCoached, beta:isVirtuallyCoached
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 31)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, activity, alternateName, beta:facilitySetting, beta:formattedDescription, beta:facilityType, attendeeInstructions, beta:isWheelchairAccessible
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 342)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 444)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 342)

- present: @type, name, value

### Offer  (instances sampled: 1,601)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 2,261)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 444)

- present: @id, @type, beta:formattedDescription, description, legalName, logo, name, sameAs, url
- absent (model): address, contactPoint, email, identifier, image, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 342)

- present: @type, name, value

### PartialSchedule  (instances sampled: 413)

- present: @type, duration, endTime, startDate, startTime, byDay, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 444)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, description, geo, telephone, url, openingHoursSpecification
- absent (model): @id, containedInPlace, containsPlace, image

### PostalAddress  (instances sampled: 444)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,095)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 413)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 342)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,192)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 342)

- present: @type, name, value

### Towels (nested)  (instances sampled: 342)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 342)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 342)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 79)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://loughboroughuniversity-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Loughborough University_

- feeds sampled: `loughboroughuniversity-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=10), `loughboroughuniversity-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `loughboroughuniversity-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 508)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 10)

- present: endDate, startDate, activity, description, id, identifier, location, name, provider, type, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 508)

- present: latitude, longitude, type
- absent (model): —

### ImageObject  (instances sampled: 508)

- present: type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 508)

- present: description, email, logo, name, sameAs, telephone, type, url
- absent (model): @id, address, contactPoint, identifier, image, legalName, taxID, vatID

### Place  (instances sampled: 508)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 508)

- present: addressCountry, postalCode, streetAddress, type, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 194)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: description, endDate, identifier, location, startDate, superEvent, type, url
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://lrso.bookteq.com/api/open-active
_publisher: LRSO_

- feeds sampled: `lrso-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=272), `lrso-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 272)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 272)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 272)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 1,723)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 272)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 272)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 272)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://lsbuactive-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `lsbuactive-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=6), `lsbuactive-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `lsbuactive-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=345)

### Concept  (instances sampled: 1,097)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 345)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 6)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### Offer  (instances sampled: 845)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 350)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 294)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Place  (instances sampled: 350)

- present: address, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification

### PostalAddress  (instances sampled: 350)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 59)

- present: maxValue, minValue, type

### ScheduledSession  (instances sampled: 345)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 345)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://manchestercommunicationacademy.bookteq.com/api/open-active
_publisher: Manchester Communication Academy_

- feeds sampled: `manchestercommunicationacademy-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=63), `manchestercommunicationacademy-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 63)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 63)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 63)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 362)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 63)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 63)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 63)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://marchtownfcestovercic.bookteq.com/api/open-active
_publisher: March was Town FC Estover CIC_

- feeds sampled: `marchtownfcestovercic-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=11), `marchtownfcestovercic-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 11)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 11)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 11)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 78)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 11)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 11)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 11)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://marstonmoretaine.bookteq.com/api/open-active
_publisher: Marston Moretaine Playing Fields_

- feeds sampled: `marstonmoretaine-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=4), `marstonmoretaine-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 4)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 4)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 4)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 28)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 4)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 4)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 4)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://mws.ledleisure.co.uk/OpenActive/

- feeds sampled: `opendata-leisurecloud-live-api-feeds-LED-live-live-course-instance` (CourseInstance, n=2), `opendata-leisurecloud-live-api-feeds-LED-live-live-facility-uses` (FacilityUse, n=161), `opendata-leisurecloud-live-api-feeds-LED-live-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-LED-live-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-LED-live-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 633)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 633)

- present: @type, name, value

### Concept  (instances sampled: 646)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 2)

- present: @id, @type, author, category, genderRestriction, name, activity, ageRange, beta:formattedDescription, image, level
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, description, duration, endDate, eventSchedule, eventStatus, identifier, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 2)

- present: @id, @type, attendeeInstructions, category, duration, endDate, eventStatus, identifier, instanceOfCourse, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent, url, image, level
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, isAccessibleForFree, isCoached, leader, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 633)

- present: @type, name, value

### Event  (instances sampled: 2)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 491)

- present: @type, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, activity, description, attendeeInstructions, level, image, isCoached, ageRange, beta:isVirtuallyCoached, beta:isWheelchairAccessible
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 161)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, attendeeInstructions, activity, alternateName, beta:formattedDescription, beta:facilitySetting, image, beta:facilityType, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 632)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 3,606)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 633)

- present: @type, name, value

### Offer  (instances sampled: 1,537)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 1,129)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 663)

- present: @id, @type, beta:formattedDescription, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, description, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 633)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 663)

- present: @type, address, beta:formattedDescription, identifier, name, telephone, url, amenityFeature, description, geo, image
- absent (model): @id, containedInPlace, containsPlace, openingHoursSpecification

### PostalAddress  (instances sampled: 663)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 981)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 633)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,733)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 633)

- present: @type, name, value

### Towels (nested)  (instances sampled: 633)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 633)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 633)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 721)

- present: @type, identifier, name, price, priceCurrency, description, ageRestriction

## https://nxtlevelsportandeducation.bookteq.com/api/open-active
_publisher: NXT Level Sport & Education Ltd_

- feeds sampled: `nxtlevelsportandeducation-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=116), `nxtlevelsportandeducation-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 116)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 116)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 116)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 748)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 116)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 116)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 116)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://ocll.gs-signature.cloud/OpenActive/
_publisher: Oldham Community Leisure_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-OldhamCommunityLeisure-live-facility-uses` (FacilityUse, n=6), `opendata-leisurecloud-live-api-feeds-OldhamCommunityLeisure-live-session-series` (SessionSeries, n=441)

### BabyChanging (nested)  (instances sampled: 447)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 447)

- present: @type, name, value

### Concept  (instances sampled: 318)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 447)

- present: @type, name, value

### EventSeries  (instances sampled: 312)

- present: @type, activity, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, ageRange, description, isCoached
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 6)

- present: @id, @type, activity, alternateName, attendeeInstructions, beta:formattedDescription, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 442)

- present: @type, latitude, longitude
- absent (model): —

### Lockers (nested)  (instances sampled: 447)

- present: @type, name, value

### Offer  (instances sampled: 1,569)

- present: @type, acceptedPaymentMethod, description, identifier, name, price, priceCurrency, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,153)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 447)

- present: @id, @type, beta:formattedDescription, legalName, name, url
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 447)

- present: @type, name, value

### PartialSchedule  (instances sampled: 441)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 447)

- present: @type, address, amenityFeature, beta:formattedDescription, description, identifier, name, telephone, url, openingHoursSpecification, geo
- absent (model): @id, containedInPlace, containsPlace, image

### PostalAddress  (instances sampled: 447)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 596)

- present: @type, maxValue, minValue

### SessionSeries  (instances sampled: 441)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, attendeeInstructions, superEvent, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 447)

- present: @type, name, value

### Toilets (nested)  (instances sampled: 447)

- present: @type, name, value

### Towels (nested)  (instances sampled: 447)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 447)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 447)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 24)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://oldnorthamptonians.bookteq.com/api/open-active
_publisher: Old Northamptonians Association_

- feeds sampled: `oldnorthamptonians-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=7), `oldnorthamptonians-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 7)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 7)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 7)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 49)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 7)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 7)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 7)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://oldwhitgiftianscc.bookteq.com/api/open-active
_publisher: Old Whitgiftians Cricket Club_

- feeds sampled: `oldwhitgiftianscc-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=3), `oldwhitgiftianscc-bookteq-com-api-open-active-slots` (Slot, n=36)

### Concept  (instances sampled: 3)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 3)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 3)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 36)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 6)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 3)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 3)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 3)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 36)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://oneleisure.gs-signature.cloud/OpenActive/
_publisher: Huntingdonshire District Council_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-HuntingdonshireDistrictCouncil-live-facility-uses` (FacilityUse, n=86), `opendata-leisurecloud-live-api-feeds-HuntingdonshireDistrictCouncil-live-session-series` (SessionSeries, n=432), `opendata-leisurecloud-live-api-feeds-HuntingdonshireDistrictCouncil-live-slots` (Slot, n=500), `opendata-leisurecloud-live-api-feeds-OneLeisure-live-facility-uses` (FacilityUse, n=91), `opendata-leisurecloud-live-api-feeds-OneLeisure-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-OneLeisure-live-session-series` (SessionSeries, n=458), `opendata-leisurecloud-live-api-feeds-OneLeisure-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 916)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 916)

- present: @type, name, value

### Concept  (instances sampled: 1,141)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 916)

- present: @type, name, value

### EventSeries  (instances sampled: 752)

- present: @type, activity, beta:formattedDescription, description, endDate, identifier, name, organizer, startDate, genderRestriction, level, isCoached, ageRange, beta:isWheelchairAccessible, attendeeInstructions, accessibilityInformation, accessibilitySupport, image, beta:isVirtuallyCoached
- absent (model): @id, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 177)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, activity, alternateName, beta:facilitySetting, beta:formattedDescription, description, beta:isWheelchairAccessible, attendeeInstructions, beta:facilityType
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 916)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 3,059)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 916)

- present: @type, name, value

### Offer  (instances sampled: 4,215)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 7,657)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1,067)

- present: @id, @type, beta:formattedDescription, beta:video, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, description, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 916)

- present: @type, name, value

### PartialSchedule  (instances sampled: 890)

- present: @type, duration, endTime, startDate, startTime, byDay, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 1,067)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, description, geo, image, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 1,067)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,695)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 890)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 916)

- present: @type, name, value

### Slot  (instances sampled: 1,000)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,300)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 916)

- present: @type, name, value

### Towels (nested)  (instances sampled: 916)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 1,067)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 916)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 916)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 1,492)

- present: @type, identifier, name, price, priceCurrency, description, ageRestriction

## https://openactive.goodgym.org/

- feeds sampled: `goodgym-org-api-openactive-events` (Event, n=500)

### Brand  (instances sampled: 500)

- present: @type, name, url
- absent (model): @id, description, identifier, logo, video

### Concept  (instances sampled: 500)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: @type, activity, ageRange, beta:formattedDescription, description, disambiguatingDescription, duration, endDate, id, identifier, location, name, offers, organizer, programme, startDate, url, leader
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, level, maximumAttendeeCapacity, meetingPoint, potentialAction, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 405)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 500)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 500)

- present: @id, @type, price, priceCurrency
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: @id, @type, email, logo, name, telephone, url
- absent (model): address, contactPoint, description, identifier, image, legalName, sameAs, taxID, vatID

### Person  (instances sampled: 430)

- present: @type, name, description
- absent (model): @id, contactPoint, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 500)

- present: @type, address, name, geo, description
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 500)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 500)

- present: @type, minValue

## https://openactive.opensessions.io/
_publisher: Open Sessions_

- feeds sampled: `opensessions-io-api-rpde-events` (Event, n=104), `opensessions-io-api-rpde-session-series` (SessionSeries, n=500)

### BabyChanging (nested)  (instances sampled: 603)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 603)

- present: @type, name, value

### Concept  (instances sampled: 2,197)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### ContactPoint  (instances sampled: 244)

- present: @type, email, name, telephone
- absent (model): availableLanguage, contactType, url

### Creche (nested)  (instances sampled: 603)

- present: @type, name, value

### Event  (instances sampled: 104)

- present: @id, @type, activity, ageRange, beta:contactPoint, beta:isFirstSessionAccessibleForFree, description, duration, endDate, eventAttendanceMode, genderRestriction, isAccessibleForFree, isCoached, location, meetingPoint, name, offers, organizer, startDate, url, attendeeInstructions, image, accessibilitySupport
- absent (model): accessibilityInformation, category, contributor, eventSchedule, eventStatus, identifier, leader, level, maximumAttendeeCapacity, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 601)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 561)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 603)

- present: @type, name, value

### Offer  (instances sampled: 603)

- present: @type, price, priceCurrency, url, acceptedPaymentMethod, name
- absent (model): @id, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, validFromBeforeStartDate

### Organization  (instances sampled: 604)

- present: @id, @type, name, url, email, telephone, beta:formalCriteriaMet, sameAs, logo, description
- absent (model): address, contactPoint, identifier, image, legalName, taxID, vatID

### Parking (nested)  (instances sampled: 603)

- present: @type, name, value

### Person  (instances sampled: 3)

- present: @type, name
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 603)

- present: @type, address, amenityFeature, name, geo
- absent (model): @id, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### QuantitativeValue (nested)  (instances sampled: 588)

- present: @type, minValue, maxValue

### Schedule  (instances sampled: 500)

- present: @type, duration, endDate, endTime, idTemplate, repeatFrequency, scheduleTimezone, scheduledEventType, startDate, startTime, urlTemplate, byDay, exceptDate, byMonthDay
- absent (model): byMonth, repeatCount

### SessionSeries  (instances sampled: 500)

- present: @id, @type, activity, description, duration, endDate, eventSchedule, isAccessibleForFree, isCoached, name, organizer, startDate, url, location, offers, ageRange, genderRestriction, image, subEventUrl, accessibilitySupport, level, beta:contactPoint, beta:formattedDescription, beta:isFirstSessionAccessibleForFree, eventAttendanceMode, meetingPoint, beta:facilitySetting, attendeeInstructions, maximumAttendeeCapacity, accessibilityInformation, beta:video, leader, beta:virtualLocation
- absent (model): category, contributor, eventStatus, identifier, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 603)

- present: @type, name, value

### Toilets (nested)  (instances sampled: 603)

- present: @type, name, value

### Towels (nested)  (instances sampled: 603)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 17)

- present: type, url

### VirtualLocation (nested)  (instances sampled: 1)

- present: @type, name

## https://openactive.played.co/openactive/
_publisher: Played_

- feeds sampled: `openactive-played-co-feeds-facility-use-slots` (Slot, n=500), `openactive-played-co-feeds-facility-uses` (FacilityUse, n=91), `openactive-played-co-feeds-scheduled-sessions` (ScheduledSession, n=500), `openactive-played-co-feeds-session-series` (SessionSeries, n=500)

### Concept  (instances sampled: 1,094)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### FacilityUse  (instances sampled: 91)

- present: @id, @type, activity, description, endDate, image, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, identifier, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 577)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 1,518)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### LocationFeatureSpecification (nested)  (instances sampled: 945)

- present: @type, name, value

### Offer  (instances sampled: 1,606)

- present: @type, price, priceCurrency, @id, name, validFromBeforeStartDate, identifier
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url

### Organization  (instances sampled: 591)

- present: @id, @type, identifier, name, taxMode, email, logo
- absent (model): address, contactPoint, description, image, legalName, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 55)

- present: @type, endTime, repeatFrequency, scheduleTimezone, startDate, startTime, endDate, byDay
- absent (model): byMonth, byMonthDay, duration, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Place  (instances sampled: 591)

- present: @type, address, identifier, name, geo, description, telephone, url, image, amenityFeature
- absent (model): @id, containedInPlace, containsPlace, openingHoursSpecification

### PostalAddress  (instances sampled: 591)

- present: @type, addressCountry, postalCode, streetAddress, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 325)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, duration, endDate, identifier, remainingAttendeeCapacity, startDate, superEvent, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, description, endDate, genderRestriction, image, location, name, organizer, startDate, url, offers, activity, ageRange, attendeeInstructions, accessibilitySupport, eventSchedule
- absent (model): accessibilityInformation, category, contributor, duration, eventStatus, identifier, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate, url
- absent (model): —

## https://openactive.upshot.org.uk/
_publisher: Upshot_

- feeds sampled: `app-upshot-org-uk-api-v0-openactive-v1-0` (Event, n=500)

### Concept  (instances sampled: 420)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: @id, duration, endDate, eventStatus, location, name, offers, startDate, superEvent, type, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, category, contributor, description, eventSchedule, genderRestriction, identifier, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### EventSeries  (instances sampled: 500)

- present: activity, category, endDate, identifier, name, organizer, startDate, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, contributor, description, duration, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### GeoCoordinates  (instances sampled: 500)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 500)

- present: @type, price
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, priceCurrency, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: @id, @type, identifier, name
- absent (model): address, contactPoint, description, email, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 500)

- present: address, geo, name, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone

### PostalAddress  (instances sampled: 500)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

## https://opendata.exercise-anywhere.com/
_publisher: Exercise Anywhere_

- feeds sampled: `opendata-exercise-anywhere-com-api-rpde-events` (Event, n=500), `opendata-exercise-anywhere-com-api-rpde-scheduled-sessions` (ScheduledSession, n=146), `opendata-exercise-anywhere-com-api-rpde-session-series` (SessionSeries, n=13)

### ChangingFacilities (nested)  (instances sampled: 495)

- present: name, type, value

### Concept  (instances sampled: 513)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: activity, ageRange, description, duration, endDate, eventAttendanceMode, eventStatus, id, identifier, isAccessibleForFree, leader, level, meetingPoint, name, offers, organizer, startDate, type, url, beta:formattedDescription, beta:FacilitySettingType, location, image, maximumAttendeeCapacity, remainingAttendeeCapacity, beta:isInteractivityPreferred, beta:participantSuppliedEquipment
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, genderRestriction, isCoached, potentialAction, programme, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 495)

- present: latitude, longitude, type
- absent (model): —

### ImageObject  (instances sampled: 2,447)

- present: type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 659)

- present: identifier, price, priceCurrency, type, id, ageRange, name, url
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 482)

- present: closes, dayOfWeek, opens, type
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 513)

- present: name, telephone, type, url, id, sameAs, email
- absent (model): address, contactPoint, description, identifier, image, legalName, logo, taxID, vatID

### PartialSchedule  (instances sampled: 13)

- present: byDay, duration, endDate, endTime, scheduleTimezone, startDate, startTime, type
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Person  (instances sampled: 659)

- present: familyName, givenName, id, type, jobTitle, identifier
- absent (model): contactPoint, description, email, gender, image, name, sameAs, telephone, url

### Place  (instances sampled: 495)

- present: address, amenityFeature, description, geo, id, identifier, name, telephone, type, openingHoursSpecification
- absent (model): containedInPlace, containsPlace, image, url

### PostalAddress  (instances sampled: 495)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 659)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 146)

- present: beta:FacilitySettingType, duration, endDate, eventAttendanceMode, eventStatus, id, identifier, leader, name, offers, startDate, superEvent, type, url, maximumAttendeeCapacity, remainingAttendeeCapacity
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, organizer, potentialAction, programme, schedulingNote, subEvent

### SessionSeries  (instances sampled: 13)

- present: activity, ageRange, beta:FacilitySettingType, category, description, duration, endDate, eventAttendanceMode, eventSchedule, genderRestriction, id, identifier, leader, level, location, name, offers, organizer, startDate, type, url, image
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, eventStatus, isAccessibleForFree, isCoached, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 495)

- present: name, type, value

## https://orchardlearningalliance.bookteq.com/api/open-active
_publisher: Orchard Learning Alliance_

- feeds sampled: `orchardlearningalliance-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=60), `orchardlearningalliance-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 60)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 60)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 60)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 284)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 60)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 60)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 60)

- present: @type, addressCountry, addressLocality, postalCode, streetAddress, addressRegion
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://ourparks.org.uk/openactive
_publisher: Our Parks_

- feeds sampled: `ourparks-org-uk-api-events` (Event, n=500)

### Brand  (instances sampled: 500)

- present: @type, identifier, name, url, logo, description
- absent (model): @id, video

### Concept  (instances sampled: 500)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: @type, activity, ageRange, beta:donationPaymentUrl, beta:formattedDescription, beta:participantSuppliedEquipment, description, duration, endDate, eventAttendanceMode, eventStatus, genderRestriction, identifier, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, programme, remainingAttendeeCapacity, startDate, url, level, beta:video
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, isCoached, potentialAction, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 500)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 1,933)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 500)

- present: @type, name, price, priceCurrency
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: @id, @type, email, identifier, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, description, image, legalName, taxID, vatID

### Person  (instances sampled: 500)

- present: @type, email, gender, name, url
- absent (model): @id, contactPoint, description, identifier, image, jobTitle, sameAs, telephone

### Place  (instances sampled: 500)

- present: @type, address, geo, identifier, name, url, description, image
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, openingHoursSpecification, telephone

### PostalAddress  (instances sampled: 500)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 500)

- present: @type, minValue

## https://oxforduniversity.leisurecloud.net/OpenActive/
_publisher: Oxford University_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-OxfordUniversity-live-facility-uses` (FacilityUse, n=50), `opendata-leisurecloud-live-api-feeds-OxfordUniversity-live-scheduled-sessions` (ScheduledSession, n=289), `opendata-leisurecloud-live-api-feeds-OxfordUniversity-live-session-series` (SessionSeries, n=70), `opendata-leisurecloud-live-api-feeds-OxfordUniversity-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 112)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 112)

- present: @type, name, value

### Concept  (instances sampled: 40)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 112)

- present: @type, name, value

### FacilityUse  (instances sampled: 50)

- present: @id, @type, attendeeInstructions, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, alternateName, beta:formattedDescription, activity, beta:facilitySetting, image, description, beta:isWheelchairAccessible, beta:facilityType, accessibilityInformation, beta:video
- absent (model): accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 112)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 1,488)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 112)

- present: @type, name, value

### Offer  (instances sampled: 776)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name
- absent (model): @id, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 355)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 120)

- present: @id, @type, beta:formattedDescription, beta:video, description, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 112)

- present: @type, name, value

### PartialSchedule  (instances sampled: 70)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, endDate, byDay
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 120)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, description, geo, image, telephone, url
- absent (model): @id, containedInPlace, containsPlace, openingHoursSpecification

### PostalAddress  (instances sampled: 120)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### ScheduledSession  (instances sampled: 289)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 70)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, organizer, startDate, url, genderRestriction, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 112)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,159)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 112)

- present: @type, name, value

### Towels (nested)  (instances sampled: 112)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 122)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 112)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 112)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 176)

- present: @type, identifier, name, price, priceCurrency, description

## https://partners.playfootball.net/OpenActive/
_publisher: PlayFootball_

- feeds sampled: `partners-playfootball-net-OpenActive-feeds-facility-use-slots` (Slot, n=500), `partners-playfootball-net-OpenActive-feeds-facility-uses` (FacilityUse, n=15)

### ChangingFacilities (nested)  (instances sampled: 3)

- present: @type, name, value

### Concept  (instances sampled: 15)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### FacilityUse  (instances sampled: 15)

- present: @id, @type, beta:facilitySetting, endDate, facilityType, hoursAvailable, identifier, location, name, offers, provider, startDate, url, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 15)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 15)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, price, priceCurrency
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 210)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 15)

- present: @id, @type, address, description, email, identifier, isOpenBookingAllowed, legalName, logo, name, taxMode, telephone, termsOfService, url
- absent (model): contactPoint, image, sameAs, taxID, vatID

### Place  (instances sampled: 15)

- present: @id, @type, address, geo, identifier, name, openingHoursSpecification, telephone, url, description, amenityFeature
- absent (model): containedInPlace, containsPlace, image

### PostalAddress  (instances sampled: 30)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### PrivacyPolicy (nested)  (instances sampled: 15)

- present: @type, dateModified, name, requiresExplicitConsent, url

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### TermsOfUse (nested)  (instances sampled: 15)

- present: @type, dateModified, name, requiresExplicitConsent, url

### beta:IndicativeOffer (nested)  (instances sampled: 29)

- present: @id, @type, identifier, name, price, priceCurrency

## https://pentest-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `pentest-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=5), `pentest-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500)

### Concept  (instances sampled: 5)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### FacilityUse  (instances sampled: 5)

- present: activity, endDate, id, identifier, location, name, provider, startDate, type, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### Offer  (instances sampled: 500)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 5)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 5)

- present: address, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification

### PostalAddress  (instances sampled: 5)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://placesleisure.gs-signature.cloud/OpenActive/
_publisher: Places Leisure_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-PlacesLeisure-live-course-instance` (CourseInstance, n=4), `opendata-leisurecloud-live-api-feeds-PlacesLeisure-live-facility-uses` (FacilityUse, n=500), `opendata-leisurecloud-live-api-feeds-PlacesLeisure-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-PlacesLeisure-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-PlacesLeisure-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 879)

- present: @type, name, value

### Brand  (instances sampled: 88)

- present: @id, @type, beta:video, description, logo, name, url
- absent (model): identifier, video

### ChangingFacilities (nested)  (instances sampled: 879)

- present: @type, name, value

### Concept  (instances sampled: 998)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 4)

- present: @id, @type, author, category, genderRestriction, name
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, contributor, description, duration, endDate, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 4)

- present: @id, @type, category, duration, endDate, eventStatus, identifier, instanceOfCourse, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 879)

- present: @type, name, value

### Event  (instances sampled: 5)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 453)

- present: @type, activity, attendeeInstructions, beta:formattedDescription, description, endDate, genderRestriction, identifier, image, level, name, organizer, startDate, accessibilityInformation, ageRange, isCoached, programme, beta:isVirtuallyCoached, accessibilitySupport
- absent (model): @id, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 500)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, attendeeInstructions, activity, alternateName, beta:formattedDescription, description, accessibilityInformation, beta:facilitySetting, image, beta:isWheelchairAccessible, beta:facilityType
- absent (model): accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 879)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 13,741)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 879)

- present: @type, name, value

### Offer  (instances sampled: 1,999)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 9,619)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1,004)

- present: @id, @type, beta:formattedDescription, description, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 879)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, scheduleTimezone, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 1,004)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, geo, openingHoursSpecification, url, telephone, image, description
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 1,004)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,297)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, offers, startDate, url, attendeeInstructions, superEvent, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 879)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,576)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 879)

- present: @type, name, value

### Towels (nested)  (instances sampled: 879)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 88)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 879)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 879)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 1,967)

- present: @type, identifier, name, price, priceCurrency, description, ageRestriction

## https://playwaze.com/opendata/openactive
_publisher: Playwaze_

- feeds sampled: `playwaze-com-feeds-events` (Event, n=77), `playwaze-com-feeds-on-demand-event` (OnDemandEvent, n=352), `playwaze-com-feeds-scheduled-sessions` (ScheduledSession, n=500), `playwaze-com-feeds-session-series` (SessionSeries, n=500)

### Concept  (instances sampled: 1,364)

- present: @type, inScheme, prefLabel, @id
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 77)

- present: @id, @type, activity, description, endDate, eventAttendanceMode, eventStatus, genderRestriction, identifier, image, name, organizer, startDate, url, location, maximumAttendeeCapacity, ageRange, level, offers, isAccessibleForFree, beta:virtualLocation
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, isCoached, leader, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 612)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 929)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 887)

- present: @id, @type, name, price, priceCurrency, url
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, validFromBeforeStartDate

### OnDemandEvent  (instances sampled: 352)

- present: @id, @type, endDate, eventAttendanceMode, genderRestriction, identifier, image, name, organizer, startDate, url, beta:virtualLocation, description, activity, level, ageRange, offers, beta:video
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Organization  (instances sampled: 650)

- present: @id, @type, name, taxMode, url, email, address, telephone, beta:formalCriteriaMet
- absent (model): contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, vatID

### Person  (instances sampled: 779)

- present: @id, @type, name, taxMode, url, beta:formalCriteriaMet, address
- absent (model): contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone

### Place  (instances sampled: 612)

- present: @type, geo, identifier, name, address, description
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 422)

- present: @type, addressCountry, streetAddress, postalCode, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 801)

- present: @type, minValue, maxValue

### Schedule  (instances sampled: 563)

- present: @type, duration, endTime, scheduleTimezone, scheduledEventType, startDate, startTime, byDay, repeatFrequency, endDate, byMonthDay
- absent (model): byMonth, exceptDate, idTemplate, repeatCount, urlTemplate

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, activity, description, endDate, eventAttendanceMode, eventStatus, genderRestriction, identifier, image, name, organizer, startDate, superEvent, url, duration, offers, level, ageRange, isAccessibleForFree, maximumAttendeeCapacity, location, beta:virtualLocation
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, isCoached, leader, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### SessionSeries  (instances sampled: 500)

- present: @id, @type, activity, description, endDate, eventAttendanceMode, eventSchedule, identifier, name, offers, organizer, startDate, url, location, ageRange, isAccessibleForFree, beta:virtualLocation
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### VideoObject (nested)  (instances sampled: 4)

- present: @type, url

### VirtualLocation (nested)  (instances sampled: 351)

- present: @type, name, url

## https://plymouthcouncil.gs-signature.cloud/OpenActive/
_publisher: Plymouth Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-PlymouthCouncil-live-facility-uses` (FacilityUse, n=23), `opendata-leisurecloud-live-api-feeds-PlymouthCouncil-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-PlymouthCouncil-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-PlymouthCouncil-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 518)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 518)

- present: @type, name, value

### Concept  (instances sampled: 701)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 518)

- present: @type, name, value

### EventSeries  (instances sampled: 446)

- present: @type, activity, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, description, level, accessibilityInformation, ageRange, isCoached, accessibilitySupport, attendeeInstructions, beta:isWheelchairAccessible, beta:isVirtuallyCoached
- absent (model): @id, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 23)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 518)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 944)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 518)

- present: @type, name, value

### Offer  (instances sampled: 1,394)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,486)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 523)

- present: @id, @type, beta:formattedDescription, beta:video, description, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 518)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, scheduleTimezone, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 523)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, geo, telephone, url, description, openingHoursSpecification, image
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 523)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 637)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 518)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,115)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 518)

- present: @type, name, value

### Towels (nested)  (instances sampled: 518)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 523)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 518)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 518)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 40)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://pomphreyhill.bookteq.com/api/open-active
_publisher: Pomphrey Hill Community Sports Association_

- feeds sampled: `pomphreyhill-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=36), `pomphreyhill-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 36)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 36)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 36)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 197)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 36)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 36)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 36)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://precisionfootballarena.bookteq.com/api/open-active
_publisher: Precision Football Arena_

- feeds sampled: `precisionfootballarena-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=2), `precisionfootballarena-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 2)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 2)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 2)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 21)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 2)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 2)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 2)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://preessportsclub.bookteq.com/api/open-active
_publisher: Prees Sports and Social Club_

- feeds sampled: `preessportsclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=14), `preessportsclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 14)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 14)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 14)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 98)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 14)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 14)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 14)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://princesparkyouthfc.bookteq.com/api/open-active
_publisher: Princes Park Youth Football Club_

- feeds sampled: `princesparkyouthfc-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=1), `princesparkyouthfc-bookteq-com-api-open-active-slots` (Slot, n=328)

### Concept  (instances sampled: 1)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 1)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 1)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 328)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 9)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 1)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 1)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 328)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://prioryfederation.bookteq.com/api/open-active
_publisher: Priory Federation of Academies_

- feeds sampled: `prioryfederation-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=49), `prioryfederation-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 49)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 49)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 49)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 294)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 49)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 49)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 49)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://qhmemorialsportsground.bookteq.com/api/open-active
_publisher: QH Memorial Sports Ground - River Pitches_

- feeds sampled: `qhmemorialsportsground-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=29), `qhmemorialsportsground-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 29)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 29)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 29)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 182)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 29)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 29)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 29)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://readingrugbyclub.bookteq.com/api/open-active
_publisher: Reading Rugby Club_

- feeds sampled: `readingrugbyclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=30), `readingrugbyclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 30)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 30)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 30)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 189)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 30)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 30)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 30)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://risecommunitycic.bookteq.com/api/open-active
_publisher: The Hub - Rise Community_

- feeds sampled: `risecommunitycic-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=5), `risecommunitycic-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 5)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 5)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 5)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 25)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 5)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 5)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 5)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://riversfitness.gs-signature.cloud/OpenActive/
_publisher: Rivers Fitness_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-WychavonLeisure-live-facility-uses` (FacilityUse, n=12), `opendata-leisurecloud-live-api-feeds-WychavonLeisure-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-WychavonLeisure-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-WychavonLeisure-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 512)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 512)

- present: @type, name, value

### Concept  (instances sampled: 251)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 512)

- present: @type, name, value

### EventSeries  (instances sampled: 246)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, name, organizer, startDate, level, ageRange, description, isCoached, beta:isVirtuallyCoached, attendeeInstructions
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 12)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 512)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 2,048)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 512)

- present: @type, name, value

### Offer  (instances sampled: 5,077)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,668)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 512)

- present: @id, @type, beta:formattedDescription, beta:video, description, email, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 512)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 512)

- present: @type, address, amenityFeature, beta:formattedDescription, description, geo, identifier, image, name, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 512)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 4,581)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, organizer, genderRestriction, superEvent, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 512)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,810)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 512)

- present: @type, name, value

### Towels (nested)  (instances sampled: 512)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 512)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 512)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 512)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 240)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://rslonline.leisurecloud.net/OpenActive/
_publisher: Redbridge Sports Centre_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-RedbridgeSportsCentre-live-facility-uses` (FacilityUse, n=41), `opendata-leisurecloud-live-api-feeds-RedbridgeSportsCentre-live-session-series` (SessionSeries, n=76)

### BabyChanging (nested)  (instances sampled: 117)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 117)

- present: @type, name, value

### Creche (nested)  (instances sampled: 117)

- present: @type, name, value

### FacilityUse  (instances sampled: 41)

- present: @id, @type, attendeeInstructions, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 117)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 468)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 117)

- present: @type, name, value

### Offer  (instances sampled: 145)

- present: @type, acceptedPaymentMethod, description, identifier, name, price, priceCurrency, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 320)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 117)

- present: @id, @type, beta:formattedDescription, legalName, logo, name, url
- absent (model): address, contactPoint, description, email, identifier, image, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 117)

- present: @type, name, value

### PartialSchedule  (instances sampled: 76)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay
- absent (model): byMonth, byMonthDay, endDate, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 117)

- present: @type, address, amenityFeature, beta:formattedDescription, description, geo, identifier, image, name, telephone
- absent (model): @id, containedInPlace, containsPlace, openingHoursSpecification, url

### PostalAddress  (instances sampled: 117)

- present: @type, addressCountry, addressLocality, postalCode, streetAddress
- absent (model): addressRegion

### QuantitativeValue (nested)  (instances sampled: 110)

- present: @type, maxValue

### SessionSeries  (instances sampled: 76)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, organizer, startDate, url, genderRestriction, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### Showers (nested)  (instances sampled: 117)

- present: @type, name, value

### Toilets (nested)  (instances sampled: 117)

- present: @type, name, value

### Towels (nested)  (instances sampled: 117)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 117)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 117)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 68)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://salfordcommunityleisure-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `salfordcommunityleisure-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=52), `salfordcommunityleisure-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `salfordcommunityleisure-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 997)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 52)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 541)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,025)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 541)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 476)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 289)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 541)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 541)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 251)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://schoolenterprises.bookteq.com/api/open-active
_publisher: School Enterprises Ltd_

- feeds sampled: `schoolenterprises-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=256), `schoolenterprises-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 256)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 256)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 256)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate, latestCancellationBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 1,126)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 256)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 256)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 256)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://serco-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Serco Leisure_

- feeds sampled: `serco-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=167), `serco-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `serco-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 637)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 167)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 491)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,432)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 636)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 416)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 124)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 636)

- present: address, identifier, name, type, url, telephone, geo
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 636)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,690)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://shikogroupltd.bookteq.com/api/open-active
_publisher: Courts Club_

- feeds sampled: `shikogroupltd-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=5), `shikogroupltd-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 5)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 5)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 5)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 29)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 5)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 5)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 5)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://shirleyhighschool.bookteq.com/api/open-active
_publisher: Shirley High School_

- feeds sampled: `shirleyhighschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=26), `shirleyhighschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 26)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 26)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 26)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 182)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 26)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 26)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 26)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://sllandinspireall-openactive.legendonlineservices.co.uk/OpenActive
_publisher: SLL and InspireAll_

- feeds sampled: `sllandinspireall-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=230), `sllandinspireall-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `sllandinspireall-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 606)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 230)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, url, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 595)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,216)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 595)

- present: email, name, type, url
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, vatID

### PartialSchedule  (instances sampled: 470)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 75)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 595)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 595)

- present: addressCountry, postalCode, streetAddress, type, addressRegion, addressLocality
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 1,039)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://southwarkcouncil-oa.leisurecloud.net/OpenActive/
_publisher: Southwark Council_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-SouthwarkCouncil-live-course-instance` (CourseInstance, n=2), `opendata-leisurecloud-live-api-feeds-SouthwarkCouncil-live-facility-uses` (FacilityUse, n=9), `opendata-leisurecloud-live-api-feeds-SouthwarkCouncil-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-SouthwarkCouncil-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-SouthwarkCouncil-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 185)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 185)

- present: @type, name, value

### Concept  (instances sampled: 492)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 2)

- present: @id, @type, author, category, genderRestriction, name
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, contributor, description, duration, endDate, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 2)

- present: @id, @type, attendeeInstructions, category, duration, endDate, eventStatus, identifier, instanceOfCourse, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent, url
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 185)

- present: @type, name, value

### Event  (instances sampled: 2)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 490)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, name, organizer, startDate, level
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, description, duration, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 9)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, attendeeInstructions, url, activity, alternateName, beta:facilityType, beta:formattedDescription
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 410)

- present: @type, latitude, longitude
- absent (model): —

### Lockers (nested)  (instances sampled: 185)

- present: @type, name, value

### Offer  (instances sampled: 1,798)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 2,933)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 511)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### Parking (nested)  (instances sampled: 185)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, byDay, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 511)

- present: @type, address, identifier, name, beta:formattedDescription, geo, openingHoursSpecification, url, amenityFeature
- absent (model): @id, containedInPlace, containsPlace, description, image, telephone

### PostalAddress  (instances sampled: 511)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 970)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, offers, superEvent, url, attendeeInstructions, organizer, genderRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 185)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,510)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 185)

- present: @type, name, value

### Towels (nested)  (instances sampled: 185)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 185)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 185)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 82)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://southwarkcouncil.bookteq.com/api/open-active
_publisher: Southwark Council_

- feeds sampled: `southwarkcouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=6), `southwarkcouncil-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 6)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 6)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 6)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 16)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 6)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 6)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 6)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://spaldingunitedfootballclub.bookteq.com/api/open-active
_publisher: Spalding United Football Club_

- feeds sampled: `spaldingunitedfootballclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=12), `spaldingunitedfootballclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 12)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 12)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 12)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 10)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 12)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 12)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 12)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://sportsiq.bookteq.com/api/open-active
_publisher: Sports IQ LTD_

- feeds sampled: `sportsiq-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=32), `sportsiq-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 32)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 32)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 32)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 200)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 32)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 32)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 32)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://stanleyprimaryschool.bookteq.com/api/open-active
_publisher: Stanley Primary School_

- feeds sampled: `stanleyprimaryschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=34), `stanleyprimaryschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 34)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 34)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 34)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 150)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 34)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 34)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 34)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://stcuthbertmayneschool.bookteq.com/api/open-active
_publisher: St Cuthbert Mayne School_

- feeds sampled: `stcuthbertmayneschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=7), `stcuthbertmayneschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 7)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 7)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 7)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 49)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 7)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 7)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 7)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://stgeorgesschool.bookteq.com/api/open-active
_publisher: St George's School, Harpenden_

- feeds sampled: `stgeorgesschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=39), `stgeorgesschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 39)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 39)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 39)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 183)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 39)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 39)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 39)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://stoweenterprisesltd.bookteq.com/api/open-active
_publisher: Stowe Enterprises Ltd_

- feeds sampled: `stoweenterprisesltd-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=49), `stoweenterprisesltd-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 49)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 49)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 49)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 316)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 49)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 49)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 49)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://strikersindoorsports.bookteq.com/api/open-active
_publisher: Strikers Indoor Football_

- feeds sampled: `strikersindoorsports-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=13), `strikersindoorsports-bookteq-com-api-open-active-slots` (Slot, n=382)

### Concept  (instances sampled: 13)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 13)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 13)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 382)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 60)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 13)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 13)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 13)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 382)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://strouddistrictcouncil-openactive.legendonlineservices.co.uk/OpenActive

- feeds sampled: `strouddistrictcouncil-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=6), `strouddistrictcouncil-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `strouddistrictcouncil-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 506)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 6)

- present: activity, endDate, id, identifier, location, name, provider, startDate, type
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 506)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,039)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 506)

- present: name, type, email
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 480)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Place  (instances sampled: 506)

- present: address, geo, identifier, name, type, telephone, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 506)

- present: addressCountry, postalCode, streetAddress, type, addressLocality, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 354)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://sunburycricketclub.bookteq.com/api/open-active
_publisher: Sunbury Cricket Club_

- feeds sampled: `sunburycricketclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=6), `sunburycricketclub-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 6)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 6)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 6)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 42)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 6)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 6)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 6)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://tameside-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Active Tameside_

- feeds sampled: `tameside-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=11), `tameside-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `tameside-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 815)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 11)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, url, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 347)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,174)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 509)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 471)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 359)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 509)

- present: address, identifier, name, telephone, type, url, geo
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 509)

- present: addressCountry, addressLocality, postalCode, streetAddress, type, addressRegion
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 619)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, description, eventSchedule
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://tendringcouncil-openactive.legendonlineservices.co.uk/OpenActive
_publisher: Tendring Leisure_

- feeds sampled: `tendringcouncil-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=11), `tendringcouncil-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `tendringcouncil-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 528)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type, ageRange
- absent (model): @id, accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 11)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 510)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,120)

- present: identifier, name, price, priceCurrency, type, ageRange, beta:partySize
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 510)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 499)

- present: byDay, endDate, repeatFrequency, startDate, startTime, type
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 38)

- present: type, name
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 510)

- present: address, geo, identifier, name, telephone, type, url
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 510)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 775)

- present: minValue, type, maxValue

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://theblackprincetrust.bookteq.com/api/open-active
_publisher: The Black Prince Trust _

- feeds sampled: `theblackprincetrust-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=26), `theblackprincetrust-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 26)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 26)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 26)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 178)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 26)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 26)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 26)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://thedownsidesettlement.bookteq.com/api/open-active
_publisher: The Downside Settlement_

- feeds sampled: `thedownsidesettlement-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=15), `thedownsidesettlement-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 15)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 15)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 15)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 105)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 15)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 15)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 15)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://thesportswarehouseltd.bookteq.com/api/open-active
_publisher: The Sports Warehouse (Flint) LTD_

- feeds sampled: `thesportswarehouseltd-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=5), `thesportswarehouseltd-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 5)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 5)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 5)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 21)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 5)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 5)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 5)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://thewoodroffeschool.bookteq.com/api/open-active
_publisher: The Woodroffe School_

- feeds sampled: `thewoodroffeschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=18), `thewoodroffeschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 18)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 18)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 18)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 84)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 18)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 18)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 18)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://tmactive.leisurecloud.net/OpenActive/
_publisher: TM Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-TMActive-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-TMActive-live-slots` (Slot, n=500)

### Offer  (instances sampled: 500)

- present: @type, price, priceCurrency
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,692)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

## https://topcic.bookteq.com/api/open-active
_publisher: 100% TO THE TOP CIC_

- feeds sampled: `topcic-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=2), `topcic-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 2)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 2)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 2)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 14)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 2)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 2)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 2)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://towerhamletscouncil.gs-signature.cloud/OpenActive/
_publisher: Be Well - London Borough of Tower Hamlets_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-TowerHamletsCouncil-live-facility-uses` (FacilityUse, n=16), `opendata-leisurecloud-live-api-feeds-TowerHamletsCouncil-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-TowerHamletsCouncil-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-TowerHamletsCouncil-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 516)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 516)

- present: @type, name, value

### Concept  (instances sampled: 493)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 516)

- present: @type, name, value

### EventSeries  (instances sampled: 473)

- present: @type, activity, beta:formattedDescription, endDate, identifier, name, organizer, startDate, genderRestriction, description, image, level, isCoached, beta:isWheelchairAccessible, ageRange, attendeeInstructions
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 16)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, activity, alternateName, beta:formattedDescription, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 516)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 521)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 516)

- present: @type, name, value

### Offer  (instances sampled: 1,928)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 3,724)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 516)

- present: @id, @type, beta:formattedDescription, description, email, legalName, name, url
- absent (model): address, contactPoint, identifier, image, logo, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 516)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, byDay, duration, endTime, scheduleTimezone, startDate, startTime, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 516)

- present: @type, address, amenityFeature, beta:formattedDescription, description, geo, identifier, name, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace, image

### PostalAddress  (instances sampled: 516)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 677)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, superEvent, attendeeInstructions, genderRestriction, organizer
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 516)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 2,246)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 516)

- present: @type, name, value

### Towels (nested)  (instances sampled: 516)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 516)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 516)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 52)

- present: @type, identifier, name, price, priceCurrency, ageRestriction

## https://traffordleisure.leisurecloud.net/OpenActive/
_publisher: Trafford Community Leisure Trust_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-TraffordCommunityLeisureTrust-live-course-instance` (CourseInstance, n=1), `opendata-leisurecloud-live-api-feeds-TraffordCommunityLeisureTrust-live-facility-uses` (FacilityUse, n=41), `opendata-leisurecloud-live-api-feeds-TraffordCommunityLeisureTrust-live-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-TraffordCommunityLeisureTrust-live-slots` (Slot, n=500)

### Course  (instances sampled: 1)

- present: @id, @type, author, category, genderRestriction, name
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, contributor, description, duration, endDate, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 1)

- present: @id, @type, attendeeInstructions, category, duration, endDate, eventStatus, identifier, instanceOfCourse, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, meetingPoint, potentialAction, programme, schedulingNote, superEvent, url

### Event  (instances sampled: 1)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 41)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, attendeeInstructions, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction, url

### Offer  (instances sampled: 1,654)

- present: @type, price, priceCurrency, ageRestriction, description, identifier, name
- absent (model): @id, acceptedPaymentMethod, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 287)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 542)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 542)

- present: @type, address, identifier, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 542)

- present: @type
- absent (model): addressCountry, addressLocality, addressRegion, postalCode, streetAddress

### QuantitativeValue (nested)  (instances sampled: 1,247)

- present: @type, minValue, maxValue

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, organizer, startDate, genderRestriction, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,210)

- present: @type, identifier, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### beta:IndicativeOffer (nested)  (instances sampled: 93)

- present: @type, ageRestriction, identifier, name, price, priceCurrency

## https://uatbook.myeveryoneactive.com/OpenActive/
_publisher: Everyone Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-EveryoneActiveUAT-uat-course-instance` (CourseInstance, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActiveUAT-uat-facility-uses` (FacilityUse, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActiveUAT-uat-session-series` (SessionSeries, n=500), `opendata-leisurecloud-live-api-feeds-EveryoneActiveUAT-uat-uat-scheduled-sessions` (ScheduledSession, n=500)

### BabyChanging (nested)  (instances sampled: 1,478)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 1,478)

- present: @type, name, value

### Concept  (instances sampled: 1,696)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Course  (instances sampled: 500)

- present: @id, @type, activity, ageRange, author, beta:formattedDescription, category, description, genderRestriction, level, name, image
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, contributor, duration, endDate, eventSchedule, eventStatus, identifier, isAccessibleForFree, isCoached, leader, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### CourseInstance  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventStatus, identifier, instanceOfCourse, isCoached, level, location, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, subEvent, url, image, additionalAdmissionRestriction, beta:isWheelchairAccessible, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventSchedule, genderRestriction, isAccessibleForFree, leader, meetingPoint, potentialAction, programme, schedulingNote, superEvent

### Creche (nested)  (instances sampled: 1,478)

- present: @type, name, value

### Event  (instances sampled: 999)

- present: @type, duration, endDate, eventStatus, identifier, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### EventSeries  (instances sampled: 500)

- present: @type, activity, beta:formattedDescription, description, endDate, genderRestriction, identifier, name, organizer, startDate, level, image, ageRange, isCoached, beta:isVirtuallyCoached, attendeeInstructions, accessibilityInformation
- absent (model): @id, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 500)

- present: @id, @type, activity, alternateName, beta:facilitySetting, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, beta:formattedDescription, description, image, attendeeInstructions, beta:facilityType
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, event, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 1,480)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 3,399)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Lockers (nested)  (instances sampled: 1,478)

- present: @type, name, value

### Offer  (instances sampled: 2,955)

- present: @type, description, identifier, name, price, priceCurrency, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 13,837)

- present: @type, closes, opens, dayOfWeek
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 1,500)

- present: @id, @type, beta:formattedDescription, beta:video, description, legalName, logo, name, sameAs, telephone, url
- absent (model): address, contactPoint, email, identifier, image, taxID, vatID

### Parking (nested)  (instances sampled: 1,478)

- present: @type, name, value

### PartialSchedule  (instances sampled: 500)

- present: @type, duration, endTime, startDate, startTime, byDay, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 1,500)

- present: @type, address, identifier, name, beta:formattedDescription, geo, url, amenityFeature, telephone, openingHoursSpecification, image, description
- absent (model): @id, containedInPlace, containsPlace

### PostalAddress  (instances sampled: 1,500)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 5,770)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent, additionalAdmissionRestriction
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, superEvent, url, attendeeInstructions, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 1,478)

- present: @type, name, value

### SportsActivityLocation  (instances sampled: 500)

- present: @type, name
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, identifier, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 1,478)

- present: @type, name, value

### Towels (nested)  (instances sampled: 1,478)

- present: @type, name, value

### VideoObject (nested)  (instances sampled: 1,500)

- present: @type, url

### beta:Bar (nested)  (instances sampled: 1,478)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 1,478)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 3,772)

- present: @type, description, identifier, name, price, priceCurrency, ageRestriction

## https://universityofbristol-openactive.legendonlineservices.co.uk/OpenActive
_publisher: University of Bristol_

- feeds sampled: `universityofbristol-openactive-legendonlineservices-co-uk-api-facility-uses` (FacilityUse, n=13), `universityofbristol-openactive-legendonlineservices-co-uk-api-facility-uses-events` (Slot, n=500), `universityofbristol-openactive-legendonlineservices-co-uk-api-sessions` (ScheduledSession, n=500)

### Concept  (instances sampled: 513)

- present: id, inScheme, prefLabel, type
- absent (model): altLabel, broader, narrower, notation

### EventSeries  (instances sampled: 500)

- present: activity, genderRestriction, identifier, name, type
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, description, duration, endDate, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, startDate, subEvent, superEvent, url

### FacilityUse  (instances sampled: 13)

- present: endDate, startDate, activity, id, identifier, location, name, provider, type, description
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, event, hoursAvailable, image, individualFacilityUse, offers, potentialAction, url

### GeoCoordinates  (instances sampled: 96)

- present: latitude, longitude, type
- absent (model): —

### Offer  (instances sampled: 1,000)

- present: identifier, name, price, priceCurrency, type
- absent (model): @id, acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 512)

- present: email, name, type
- absent (model): @id, address, contactPoint, description, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 413)

- present: endDate, repeatFrequency, startDate, startTime, type, byDay
- absent (model): byMonth, byMonthDay, duration, endTime, exceptDate, idTemplate, repeatCount, scheduledEventType, urlTemplate

### Person  (instances sampled: 140)

- present: name, type
- absent (model): @id, contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 512)

- present: address, identifier, name, telephone, type, url, geo
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, image, openingHoursSpecification

### PostalAddress  (instances sampled: 512)

- present: addressCountry, addressLocality, addressRegion, postalCode, streetAddress, type
- absent (model): —

### ScheduledSession  (instances sampled: 500)

- present: duration, endDate, eventStatus, identifier, maximumAttendeeCapacity, name, offers, organizer, remainingAttendeeCapacity, startDate, superEvent, type, leader
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, genderRestriction, image, isAccessibleForFree, isCoached, level, location, meetingPoint, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 500)

- present: endDate, identifier, location, startDate, superEvent, type, url, eventSchedule, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, duration, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Slot  (instances sampled: 500)

- present: duration, endDate, facilityUse, id, identifier, maximumUses, offers, remainingUses, startDate, type
- absent (model): —

## https://visionredbridge.gs-signature.cloud/OpenActive/
_publisher: Vision Redbridge_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-VisionRedbridge-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-VisionRedbridge-live-session-series` (SessionSeries, n=123), `opendata-leisurecloud-live-api-feeds-VisionRedbridge-live-slots` (Slot, n=7)

### BabyChanging (nested)  (instances sampled: 93)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 93)

- present: @type, name, value

### Concept  (instances sampled: 46)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 93)

- present: @type, name, value

### EventSeries  (instances sampled: 46)

- present: @type, activity, beta:formattedDescription, endDate, genderRestriction, identifier, name, organizer, startDate
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, description, duration, eventSchedule, eventStatus, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### GeoCoordinates  (instances sampled: 95)

- present: @type, latitude, longitude
- absent (model): —

### Lockers (nested)  (instances sampled: 93)

- present: @type, name, value

### Offer  (instances sampled: 354)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 651)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 123)

- present: @id, @type, beta:formattedDescription, legalName, name, url
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, vatID

### Parking (nested)  (instances sampled: 93)

- present: @type, name, value

### PartialSchedule  (instances sampled: 123)

- present: @type, duration, endTime, startDate, startTime, byDay, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 123)

- present: @type, address, identifier, name, beta:formattedDescription, geo, telephone, url, amenityFeature, openingHoursSpecification
- absent (model): @id, containedInPlace, containsPlace, description, image

### PostalAddress  (instances sampled: 123)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 233)

- present: @type, maxValue, minValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 123)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, offers, attendeeInstructions, organizer, genderRestriction, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 93)

- present: @type, name, value

### Slot  (instances sampled: 7)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 528)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 93)

- present: @type, name, value

### Towels (nested)  (instances sampled: 93)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 93)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 93)

- present: @type, name, value

## https://walthamforestcouncil.bookteq.com/api/open-active
_publisher: Waltham Forest Council_

- feeds sampled: `walthamforestcouncil-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=135), `walthamforestcouncil-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 135)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 135)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 135)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 308)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 135)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 135)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 135)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://waspsfootballclub.bookteq.com/api/open-active
_publisher: Wasps FC - Rugby in West London_

- feeds sampled: `waspsfootballclub-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=8)

### Concept  (instances sampled: 8)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 8)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 8)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### OpeningHoursSpecification  (instances sampled: 39)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 8)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 8)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 8)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

## https://waterliliesswimmingschool.bookteq.com/api/open-active
_publisher: Water Lilies Swimming School Ltd_

- feeds sampled: `waterliliesswimmingschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=7), `waterliliesswimmingschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 7)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 7)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 7)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 59)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 7)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 7)

- present: @id, @type, address, description, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 7)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://wellingtonclub.gs-signature.cloud/OpenActive/
_publisher: Wellington College_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-WellingtonCollege-live-facility-uses` (FacilityUse, n=6), `opendata-leisurecloud-live-api-feeds-WellingtonCollege-live-scheduled-sessions` (ScheduledSession, n=348), `opendata-leisurecloud-live-api-feeds-WellingtonCollege-live-session-series` (SessionSeries, n=155), `opendata-leisurecloud-live-api-feeds-WellingtonCollege-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 161)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 161)

- present: @type, name, value

### Concept  (instances sampled: 148)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 161)

- present: @type, name, value

### EventSeries  (instances sampled: 139)

- present: @type, activity, ageRange, beta:formattedDescription, description, endDate, identifier, level, name, organizer, startDate, genderRestriction, isCoached, attendeeInstructions
- absent (model): @id, accessibilityInformation, accessibilitySupport, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 6)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, url, attendeeInstructions, activity, alternateName, beta:facilityType, beta:formattedDescription
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, offers, potentialAction

### GeoCoordinates  (instances sampled: 161)

- present: @type, latitude, longitude
- absent (model): —

### Lockers (nested)  (instances sampled: 161)

- present: @type, name, value

### Offer  (instances sampled: 501)

- present: @type, price, priceCurrency, acceptedPaymentMethod, description, identifier, name
- absent (model): @id, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 1,169)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 161)

- present: @id, @type, beta:formattedDescription, email, legalName, name, telephone, url
- absent (model): address, contactPoint, description, identifier, image, logo, sameAs, taxID, vatID

### Parking (nested)  (instances sampled: 161)

- present: @type, name, value

### PartialSchedule  (instances sampled: 155)

- present: @type, duration, endTime, scheduleTimezone, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 161)

- present: @type, address, amenityFeature, beta:formattedDescription, geo, identifier, name, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace, description, image

### PostalAddress  (instances sampled: 161)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 139)

- present: @type, minValue

### ScheduledSession  (instances sampled: 348)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 155)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, startDate, url, attendeeInstructions, superEvent, organizer, genderRestriction, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 161)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 3,753)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 161)

- present: @type, name, value

### Towels (nested)  (instances sampled: 161)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 161)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 161)

- present: @type, name, value

## https://wellscathedral.bookteq.com/api/open-active
_publisher: Wells Cathedral School_

- feeds sampled: `wellscathedral-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=16), `wellscathedral-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 16)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 16)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 16)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 107)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 16)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 16)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 16)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://westheathprimaryschool.bookteq.com/api/open-active
_publisher: West Heath Primary School_

- feeds sampled: `westheathprimaryschool-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=30), `westheathprimaryschool-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 30)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 30)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 30)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 186)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 30)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 30)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 30)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://woolmerhillsportspark.bookteq.com/api/open-active
_publisher: Woolmer Hill Sports Association_

- feeds sampled: `woolmerhillsportspark-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=22), `woolmerhillsportspark-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 22)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 22)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 22)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 140)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 22)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 22)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 22)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://wvactive.leisurecloud.net/OpenActive/
_publisher: WV Active_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-WVActive-live-facility-uses` (FacilityUse, n=50), `opendata-leisurecloud-live-api-feeds-WVActive-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-WVActive-live-session-series` (SessionSeries, n=283), `opendata-leisurecloud-live-api-feeds-WVActive-live-slots` (Slot, n=500)

### FacilityUse  (instances sampled: 50)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, provider, startDate, attendeeInstructions, offers
- absent (model): accessibilityInformation, accessibilitySupport, activity, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction, url

### Offer  (instances sampled: 817)

- present: @type, price, priceCurrency, description, identifier, name, ageRestriction
- absent (model): @id, acceptedPaymentMethod, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 350)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 333)

- present: @id, @type, legalName, name
- absent (model): address, contactPoint, description, email, identifier, image, logo, sameAs, taxID, telephone, url, vatID

### PartialSchedule  (instances sampled: 283)

- present: @type, duration, endTime, startDate, startTime, byDay, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 333)

- present: @type, address, identifier, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 333)

- present: @type
- absent (model): addressCountry, addressLocality, addressRegion, postalCode, streetAddress

### QuantitativeValue (nested)  (instances sampled: 400)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 283)

- present: @id, @type, category, duration, endDate, eventSchedule, genderRestriction, identifier, location, name, organizer, startDate, offers, attendeeInstructions
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,873)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### beta:IndicativeOffer (nested)  (instances sampled: 84)

- present: @type, ageRestriction, identifier, name, price, priceCurrency, description

## https://www.goodgym.org/api/openactive/
_publisher: Good Gym_

- feeds sampled: `goodgym-org-api-openactive-events` (Event, n=500)

### Brand  (instances sampled: 500)

- present: @type, name, url
- absent (model): @id, description, identifier, logo, video

### Concept  (instances sampled: 500)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 500)

- present: @type, activity, ageRange, beta:formattedDescription, description, disambiguatingDescription, duration, endDate, id, identifier, location, name, offers, organizer, programme, startDate, url, leader
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, level, maximumAttendeeCapacity, meetingPoint, potentialAction, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 397)

- present: @type, latitude, longitude
- absent (model): —

### ImageObject  (instances sampled: 500)

- present: @type, url
- absent (model): description, height, name, thumbnail, width

### Offer  (instances sampled: 500)

- present: @id, @type, price, priceCurrency
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### Organization  (instances sampled: 500)

- present: @id, @type, email, logo, name, telephone, url
- absent (model): address, contactPoint, description, identifier, image, legalName, sameAs, taxID, vatID

### Person  (instances sampled: 417)

- present: @type, name, description
- absent (model): @id, contactPoint, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 500)

- present: @type, address, name, geo, description
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 500)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 500)

- present: @type, minValue

## https://www.sportsuite.co.uk/odapikey/datasite
_publisher: SportSuite_

- feeds sampled: `sportsuite-co-uk-api-cs-api-openactive` (Event, n=25), `sportsuite-co-uk-api-cs-api-openactive` (SessionSeries, n=500)

### Concept  (instances sampled: 525)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Event  (instances sampled: 25)

- present: @id, @type, activity, ageRange, endDate, eventAttendanceMode, genderRestriction, location, name, offers, organizer, startDate, url, description, duration
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent

### GeoCoordinates  (instances sampled: 524)

- present: @type, latitude, longitude
- absent (model): —

### Offer  (instances sampled: 525)

- present: @id, @type, price, priceCurrency, url
- absent (model): acceptedPaymentMethod, ageRestriction, allowCustomerCancellationFullRefund, availability, availableChannel, description, identifier, latestCancellationBeforeStartDate, name, openBookingFlowRequirement, prepayment, validFromBeforeStartDate

### Organization  (instances sampled: 508)

- present: @id, @type, name, taxMode, url, description, telephone
- absent (model): address, contactPoint, email, identifier, image, legalName, logo, sameAs, taxID, vatID

### Person  (instances sampled: 17)

- present: @id, @type, name, taxMode
- absent (model): contactPoint, description, email, gender, identifier, image, jobTitle, sameAs, telephone, url

### Place  (instances sampled: 525)

- present: @type, address, geo, name
- absent (model): @id, amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 304)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 525)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 9,621)

- present: @id, @type, startDate, duration, endDate
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, identifier, image, isAccessibleForFree, isCoached, leader, level, location, maximumAttendeeCapacity, meetingPoint, name, offers, organizer, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### SessionSeries  (instances sampled: 500)

- present: @id, @type, activity, ageRange, description, endDate, eventAttendanceMode, genderRestriction, location, name, offers, organizer, startDate, subEvent, url
- absent (model): accessibilityInformation, accessibilitySupport, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, identifier, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, superEvent

## https://wycliffecollege.bookteq.com/api/open-active
_publisher: Wycliffe College_

- feeds sampled: `wycliffecollege-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=21), `wycliffecollege-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 21)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 21)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 21)

- present: @id, @type, endDate, facilityType, identifier, location, name, provider, startDate, url, hoursAvailable
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 117)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 21)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 21)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 21)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://wymondhamtownunitedfc.bookteq.com/api/open-active
_publisher: Wymondham Town United FC_

- feeds sampled: `wymondhamtownunitedfc-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=20), `wymondhamtownunitedfc-bookteq-com-api-open-active-slots` (Slot, n=500)

### Concept  (instances sampled: 20)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 20)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 20)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### Offer  (instances sampled: 500)

- present: @id, @type, allowCustomerCancellationFullRefund, identifier, latestCancellationBeforeStartDate, name, openBookingInAdvance, price, priceCurrency, url, validFromBeforeStartDate, validThroughBeforeStartDate
- absent (model): acceptedPaymentMethod, ageRestriction, availability, availableChannel, description, openBookingFlowRequirement, prepayment

### OpeningHoursSpecification  (instances sampled: 140)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 20)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 20)

- present: @id, @type, address, geo, name, description
- absent (model): amenityFeature, containedInPlace, containsPlace, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 20)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### Slot  (instances sampled: 500)

- present: @id, @type, duration, endDate, facilityUse, identifier, offers, remainingUses, startDate
- absent (model): maximumUses

## https://ymcahumber.bookteq.com/api/open-active

- feeds sampled: `ymcahumber-bookteq-com-api-open-active-facility-uses` (IndividualFacilityUse, n=16)

### Concept  (instances sampled: 16)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### GeoCoordinates  (instances sampled: 16)

- present: @type, latitude, longitude
- absent (model): —

### IndividualFacilityUse  (instances sampled: 16)

- present: @id, @type, endDate, facilityType, hoursAvailable, identifier, location, name, provider, startDate, url
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, attendeeInstructions, category, description, event, image, offers, potentialAction

### OpeningHoursSpecification  (instances sampled: 112)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 16)

- present: @id, @type, isOpenBookingAllowed, name, taxMode
- absent (model): address, contactPoint, description, email, identifier, image, legalName, logo, sameAs, taxID, telephone, url, vatID

### Place  (instances sampled: 16)

- present: @id, @type, address, geo, name
- absent (model): amenityFeature, containedInPlace, containsPlace, description, identifier, image, openingHoursSpecification, telephone, url

### PostalAddress  (instances sampled: 16)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

## https://yourleisure.gs-signature.cloud/OpenActive/
_publisher: Your Leisure_

- feeds sampled: `opendata-leisurecloud-live-api-feeds-YourLeisure-live-facility-uses` (FacilityUse, n=38), `opendata-leisurecloud-live-api-feeds-YourLeisure-live-scheduled-sessions` (ScheduledSession, n=500), `opendata-leisurecloud-live-api-feeds-YourLeisure-live-session-series` (SessionSeries, n=388), `opendata-leisurecloud-live-api-feeds-YourLeisure-live-slots` (Slot, n=500)

### BabyChanging (nested)  (instances sampled: 355)

- present: @type, name, value

### ChangingFacilities (nested)  (instances sampled: 355)

- present: @type, name, value

### Concept  (instances sampled: 31)

- present: @id, @type, inScheme, prefLabel
- absent (model): altLabel, broader, narrower, notation

### Creche (nested)  (instances sampled: 355)

- present: @type, name, value

### EventSeries  (instances sampled: 11)

- present: @type, activity, beta:formattedDescription, beta:isVirtuallyCoached, endDate, genderRestriction, identifier, isCoached, name, organizer, startDate, level, description
- absent (model): @id, accessibilityInformation, accessibilitySupport, ageRange, attendeeInstructions, category, contributor, duration, eventSchedule, eventStatus, image, isAccessibleForFree, leader, location, maximumAttendeeCapacity, meetingPoint, offers, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent, superEvent, url

### FacilityUse  (instances sampled: 38)

- present: @id, @type, beta:offerValidityPeriod, category, endDate, hoursAvailable, identifier, location, name, offers, provider, startDate, url, attendeeInstructions, activity, alternateName, beta:facilitySetting, beta:facilityType, beta:formattedDescription
- absent (model): accessibilityInformation, accessibilitySupport, aggregateFacilityUse, description, event, image, individualFacilityUse, potentialAction

### GeoCoordinates  (instances sampled: 355)

- present: @type, latitude, longitude
- absent (model): —

### Lockers (nested)  (instances sampled: 355)

- present: @type, name, value

### Offer  (instances sampled: 2,584)

- present: @type, price, priceCurrency, description, identifier, name, acceptedPaymentMethod, ageRestriction
- absent (model): @id, allowCustomerCancellationFullRefund, availability, availableChannel, latestCancellationBeforeStartDate, openBookingFlowRequirement, prepayment, url, validFromBeforeStartDate

### OpeningHoursSpecification  (instances sampled: 2,751)

- present: @type, closes, dayOfWeek, opens
- absent (model): validFrom, validThrough

### Organization  (instances sampled: 426)

- present: @id, @type, beta:formattedDescription, email, legalName, name, telephone, url
- absent (model): address, contactPoint, description, identifier, image, logo, sameAs, taxID, vatID

### Parking (nested)  (instances sampled: 355)

- present: @type, name, value

### PartialSchedule  (instances sampled: 388)

- present: @type, duration, endTime, startDate, startTime, byDay, scheduleTimezone, endDate
- absent (model): byMonth, byMonthDay, exceptDate, idTemplate, repeatCount, repeatFrequency, scheduledEventType, urlTemplate

### Place  (instances sampled: 426)

- present: @type, address, identifier, name, amenityFeature, beta:formattedDescription, geo, openingHoursSpecification, telephone, url
- absent (model): @id, containedInPlace, containsPlace, description, image

### PostalAddress  (instances sampled: 426)

- present: @type, addressCountry, addressLocality, addressRegion, postalCode, streetAddress
- absent (model): —

### QuantitativeValue (nested)  (instances sampled: 743)

- present: @type, minValue, maxValue

### ScheduledSession  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, identifier, maximumAttendeeCapacity, remainingAttendeeCapacity, startDate, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, attendeeInstructions, category, contributor, description, eventSchedule, eventStatus, genderRestriction, image, isAccessibleForFree, isCoached, leader, level, location, meetingPoint, name, offers, organizer, potentialAction, programme, schedulingNote, subEvent, url

### SessionSeries  (instances sampled: 388)

- present: @id, @type, category, duration, endDate, eventSchedule, identifier, location, name, offers, startDate, url, attendeeInstructions, genderRestriction, organizer, superEvent
- absent (model): accessibilityInformation, accessibilitySupport, activity, ageRange, contributor, description, eventStatus, image, isAccessibleForFree, isCoached, leader, level, maximumAttendeeCapacity, meetingPoint, potentialAction, programme, remainingAttendeeCapacity, schedulingNote, subEvent

### Showers (nested)  (instances sampled: 355)

- present: @type, name, value

### Slot  (instances sampled: 500)

- present: @id, @type, beta:sportsActivityLocation, duration, endDate, facilityUse, identifier, maximumUses, offers, remainingUses, startDate
- absent (model): —

### SportsActivityLocation  (instances sampled: 1,081)

- present: @type, name, identifier
- absent (model): @id, address, amenityFeature, containedInPlace, containsPlace, description, geo, image, openingHoursSpecification, telephone, url

### Toilets (nested)  (instances sampled: 355)

- present: @type, name, value

### Towels (nested)  (instances sampled: 355)

- present: @type, name, value

### beta:Bar (nested)  (instances sampled: 355)

- present: @type, name, value

### beta:Cafe (nested)  (instances sampled: 355)

- present: @type, name, value

### beta:IndicativeOffer (nested)  (instances sampled: 138)

- present: @type, identifier, name, price, priceCurrency, ageRestriction
