from typing import Any

from functools import lru_cache
from uklookup import lookup_postcode_lat_long


def _build_location(raw_location: object) -> dict[str, Any]:
    """
    Extract a clean geolocation location info from an OpenActive location value.
    If geolocation already exists, uses it.
    If postalCode exists, resolves geolocation from it.
    If an address string exists, extracts postalcode from it and resolves geolocation from it.
    """
    location: dict[str, Any] = {}
    locations = (
        raw_location if isinstance(raw_location, list)
        else [raw_location] if raw_location else []
    )
    if locations:
        geo_exists = False
        first = locations[0]
        if not isinstance(first, dict):
            return {}

        loc: dict[str, Any] = first

        geo = loc.get("geo") if isinstance(loc.get("geo"), dict) else {}
        for coord in ("latitude", "longitude"):
            try:
                val = geo.get(coord)
                if val is not None:
                    location[coord] = round(float(val), 6)
                    geo_exists = True
            except (TypeError, ValueError):
                pass

        raw_address = loc.get("address")
        if not geo_exists and raw_address:
            process_raw_address(raw_address, location)
            if "latitude" in location and "longitude" in location:
                geo_exists = True

        if not geo_exists and loc.get("containsPlace"):
            lc = _build_location(loc.get("containsPlace"))
            if "latitude" in location and "longitude" in location:
                location = lc
                geo_exists = True

        if not geo_exists and loc.get("name"):
            # just provide name for future geocoding if no geolocation info is found, as a last resort
            name = loc.get("name")
            if isinstance(name, str):
                location["place_name"] = name.strip()

    return location


def process_raw_address(raw_address: Any | None, location: dict[str, Any]):
    """
    Extract geolocation info from an address. Address can be a string or a dict.
    Args:
        raw_address: raw address value from the location, can be a string or a dict with "postalCode" field.
        location: location dict to populate with extracted info. Will be modified in-place.
    Returns:
        None. Location dict will be modified in-place.
    """
    postal_code = None
    if isinstance(raw_address, str):
        location["address"] = raw_address.strip()
        postal_code = extract_postcode(raw_address)
    elif isinstance(raw_address, dict):
        postal_code = raw_address.get("postalCode")

    if postal_code:
        location["postal_code"] = postal_code.strip()
        lat, long = get_postcode_point(postal_code.strip())
        if lat and long:
            location["latitude"] = lat
            location["longitude"] = long


@lru_cache(maxsize=50_000)
def get_postcode_point(postal_code):
    """
    Get latitude and longitude from a postal code.
    Args:
        postal_code: postal code to lookup.
    Returns:
        latitude and longitude of the postal code, or (None, None) if not found or error occurs.
    """
    try:
        lat_long = lookup_postcode_lat_long(postal_code)
        if lat_long:
            lat, long = lat_long
            return lat, long
    except Exception as e:
        pass
    return None, None


import re

@lru_cache(maxsize=50_000)
def extract_postcode(address_string):
    """
    Extract postal code from an address string.
    Args:
        address_string: address string to extract postal code from.
    Returns:
        postal_code: postal code extracted from the address string.
    """
    # Official UK Postcode Regex pattern
    regex = r'([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})'

    match = re.search(regex, address_string)
    return match.group(0) if match else None