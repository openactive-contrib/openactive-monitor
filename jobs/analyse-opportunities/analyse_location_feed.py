"""
python analyse_location_feed.py \            
            -g ../volume-1/data-analysis/000-location-districts.geojson \
            -n LAD24NM \
            -o ./output7 \
            -p ../volume-1/data-analysis/000-population/000-population-district.csv \
            -pl Name \
            -pv All_ages -v

python analyse_location_feed.py -g ../volume-1/data-analysis/000-location-nhstrusts.geojson -n TrustName -d 16-02-2026 -o ./output8 -v

python analyse_location_feed.py -g ../volume-1/data-analysis/000-location-gps.geojson -n Name -d 16-02-2026 -o ./output9 -v


"""

import click
import csv
import geopandas as gpd
import gzip
import json
import os
import pandas as pd
import pickle
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil import parser

from functools import lru_cache
from uklookup import lookup_postcode_lat_long
from postal.parser import parse_address

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_superevent_id_v_subevent_ids, get_event_type, get_item_kinds, get_item_types
from settings import *

# ==================================================================================================
# DATE CONFIGURATION
# ==================================================================================================
# Set CUSTOM_DATE to override today's date for testing (format: "DD-MM-YYYY" or date object)
# Example: CUSTOM_DATE = "16-02-2026" or CUSTOM_DATE = datetime(2026, 2, 16).date()
CUSTOM_DATE = None

def get_todays_date(custom_date=None):
    """
    Get today's date, optionally overridden by a custom date.
    
    Args:
        custom_date: Optional date override. Can be:
            - A date object
            - A string in "DD-MM-YYYY" format
            - None to use module-level CUSTOM_DATE or current date
    
    Returns:
        date object
    """
    date_to_use = custom_date or CUSTOM_DATE
    
    if date_to_use is None:
        return datetime.now().date()
    elif isinstance(date_to_use, str):
        return datetime.strptime(date_to_use, "%d-%m-%Y").date()
    else:
        return date_to_use

# ==================================================================================================
# HELPER FUNCTIONS - Data Loading
# ==================================================================================================

def load_population_data(population_csv, label_column, value_column, verbose=False):
    """
    Load population data from CSV into a case-insensitive lookup dictionary.
    
    Args:
        population_csv: Path to population CSV file
        label_column: Column name containing region names
        value_column: Column name containing population values
        verbose: Whether to print warnings
    
    Returns:
        Dictionary mapping lowercase region names to population values
    """
    print(f'Loading population data from: {population_csv}')
    pop_df = pd.read_csv(population_csv)
    
    if label_column not in pop_df.columns:
        raise ValueError(f"Label column '{label_column}' not found. Available: {list(pop_df.columns)}")
    if value_column not in pop_df.columns:
        raise ValueError(f"Value column '{value_column}' not found. Available: {list(pop_df.columns)}")
    
    population_lookup = {}
    for _, row in pop_df.iterrows():
        label = str(row[label_column]).strip().lower()
        try:
            value_str = str(row[value_column]).replace(',', '')
            population_lookup[label] = float(value_str)
        except (ValueError, TypeError):
            if verbose:
                print(f"  Warning: Could not parse population for '{row[label_column]}'")
    
    print(f'  Loaded population data for {len(population_lookup)} regions')
    return population_lookup


def load_geojson_regions(geojson_path, name_property, filter_names=None):
    """
    Load GeoJSON file and extract region information.
    
    Args:
        geojson_path: Path to GeoJSON file
        name_property: Property name containing region names
        filter_names: Optional list of region names to filter
    
    Returns:
        Tuple of (GeoDataFrame, list of region names to analyse)
    """
    gdf_regions = gpd.read_file(geojson_path)
    gdf_regions = gdf_regions.to_crs(4326)
    
    if name_property not in gdf_regions.columns:
        raise ValueError(f"Property '{name_property}' not found. Available: {list(gdf_regions.columns)}")
    
    all_region_names = gdf_regions[name_property].unique().tolist()
    
    if filter_names:
        invalid_names = [name for name in filter_names if name not in all_region_names]
        if invalid_names:
            print(f'WARNING: Region names not found: {invalid_names}')
        region_names = [name for name in filter_names if name in all_region_names]
        if not region_names:
            raise ValueError('No valid region names to analyse')
    else:
        region_names = all_region_names
    
    return gdf_regions, region_names


def extract_facility_uses(opportunities):
    """
    Extract FacilityUse and IndividualFacilityUse objects from opportunities
    into a lookup dictionary keyed by their IDs/URLs.
    
    Args:
        opportunities: The opportunities dictionary
    
    Returns:
        Dictionary mapping FacilityUse IDs/URLs to their item data
    """
    facility_uses = {}
    
    if opportunities is None or 'items' not in opportunities:
        return facility_uses
    
    for item_id, item in opportunities['items'].items():
        item_data = item.get('data', {})
        item_type = item_data.get('type') or item_data.get('@type', '')
        
        if item_type in ('FacilityUse', 'IndividualFacilityUse'):
            # Index by item_id (key in opportunities dict)
            facility_uses[item_id] = item_data
            
            # Also index by @id and id from the data for flexible lookup
            for id_key in ['@id', 'id']:
                if id_key in item_data and isinstance(item_data[id_key], str):
                    facility_uses[item_data[id_key]] = item_data
    
    return facility_uses


def load_opportunity_file(filename, filepath_prefix):
    """
    Load a single opportunity file and extract metadata.
    
    Args:
        filename: Name of the file to load
        filepath_prefix: Directory prefix for the file
    
    Returns:
        Tuple of (opportunities_dict, feed_type, item_kinds, item_types, event_type, facility_uses)
        or (None, None, None, None, None, {}) if loading fails
    """
    try:
        with gzip.open(f'{filepath_prefix}/{filename}', 'rb') as file_in:
            opportunities = pickle.load(file_in)
            
            feed_type = None
            item_kinds = None
            item_types = None
            
            try:
                feed_type = opportunities['feed']['type']
            except:
                pass
            try:
                item_kinds = get_item_kinds(opportunities)
            except:
                pass
            try:
                item_types = get_item_types(opportunities)
            except:
                pass
            
            event_type = determine_event_type(item_types, item_kinds, feed_type)
            facility_uses = extract_facility_uses(opportunities)
            
            return opportunities, feed_type, item_kinds, item_types, event_type, facility_uses
    except Exception as error:
        print(f'ERROR loading {filename}: {error}')
        return None, None, None, None, None, {}


def determine_event_type(item_types, item_kinds, feed_type):
    """
    Determine the event type (superevent/subevent) from item metadata.
    
    Args:
        item_types: Dictionary of item types and counts
        item_kinds: Dictionary of item kinds and counts
        feed_type: The feed type string
    
    Returns:
        Event type string or None
    """
    event_type = None
    
    if item_types is not None:
        event_types = [get_event_type(t) for t in item_types.keys()]
        if len(set(event_types)) == 1:
            event_type = event_types[0]
    
    if event_type is None and item_kinds is not None:
        event_types = [get_event_type(k) for k in item_kinds.keys()]
        if len(set(event_types)) == 1:
            event_type = event_types[0]
    
    if event_type is None and feed_type is not None:
        event_type = get_event_type(feed_type)
    
    return event_type


# ==================================================================================================
# HELPER FUNCTIONS - Region Stats
# ==================================================================================================

def create_empty_region_stats(region_name):
    """Create an empty stats dictionary for a region."""
    return {
        'region_name': region_name,
        'total_items': 0,
        'future_items': 0,
        'future_week_items': 0,
        'organisations': defaultdict(int),
        'places': set(),
        'facilities': set(),
        'activities': set(),
        'future_week_activities_breakdown': defaultdict(int),
        'future_week_age_range_breakdown': defaultdict(int),
        'future_event_types': defaultdict(int),
    }


def initialize_all_region_stats(region_names):
    """
    Initialize stats dictionaries for all regions including special categories.
    
    Args:
        region_names: List of region names
    
    Returns:
        Dictionary mapping region names to their stats
    """
    region_stats = {name: create_empty_region_stats(name) for name in region_names}
    region_stats['_UNMATCHED'] = create_empty_region_stats('_UNMATCHED')
    region_stats['_NO_LOCATION'] = create_empty_region_stats('_NO_LOCATION')
    return region_stats


# ==================================================================================================
# HELPER FUNCTIONS - Item Data Extraction
# ==================================================================================================

def extract_opportunity_dates(item_data, todays_date, next_weeks_date):
    """
    Extract start dates and determine if opportunity is future/future week.
    
    Args:
        item_data: The item's data dictionary
        todays_date: Today's date
        next_weeks_date: Date one week from today
    
    Returns:
        Tuple of (is_future, is_future_week)
    """
    start_dates = []
    for start_datetime in get_values(item_data, ['startDate', 'dateStart'], continue_to_next_layer=False):
        try:
            start_dates.append(parser.parse(start_datetime).date())
        except:
            pass
    
    subevent_start_dates = []
    for subevent_start_datetime in get_values(item_data, 'subEvent', ['startDate', 'dateStart'], continue_to_next_layer=False):
        try:
            subevent_start_dates.append(parser.parse(subevent_start_datetime).date())
        except:
            pass
    
    # Determine opportunity start dates
    if subevent_start_dates:
        opportunity_start_dates = subevent_start_dates
    elif start_dates:
        opportunity_start_dates = start_dates
    else:
        opportunity_start_dates = []
    
    is_future = any(d >= todays_date for d in opportunity_start_dates)
    is_future_week = any(todays_date <= d < next_weeks_date for d in opportunity_start_dates)
    
    return is_future, is_future_week


def extract_item_details(item_data, facility_uses_lookup=None):
    """
    Extract various details from an item.
    
    Args:
        item_data: The item's data dictionary
        facility_uses_lookup: Optional dictionary mapping FacilityUse IDs/URLs to their item data
    
    Returns:
        Dictionary with organizer_name, activities, facilities, age_ranges, location info
    """
    # Organizer
    organizer_names = get_values(item_data, 'organizer', 'name')
    organizer_name = strip(organizer_names[0]) if organizer_names else None
    
    # If organizer not found, try FacilityUse provider name
    if not organizer_name and facility_uses_lookup:
        facility_use_ref = item_data.get('facilityUse')
        if isinstance(facility_use_ref, dict):
            facility_use_ref = facility_use_ref.get('@id') or facility_use_ref.get('id')
        if facility_use_ref and isinstance(facility_use_ref, str) and facility_use_ref in facility_uses_lookup:
            fu_data = facility_uses_lookup[facility_use_ref]
            provider_names = get_values(fu_data, 'provider', 'name')
            if provider_names:
                organizer_name = strip(provider_names[0])
    
    # Activities and facilities
    activities = list(set([strip(v) for v in get_values(item_data, 'activity', 'prefLabel')]))
    facilities = list(set([strip(v) for v in get_values(item_data, 'facilityType', 'prefLabel')]))
    
    # Age ranges
    age_ranges = []
    for ar in get_values(item_data, 'ageRange'):
        if isinstance(ar, dict):
            min_val = ar.get('minValue')
            max_val = ar.get('maxValue')
            if min_val is not None and max_val is not None:
                age_ranges.append(f"{min_val}-{max_val}")
            elif min_val is not None:
                age_ranges.append(f"{min_val}+")
            elif max_val is not None:
                age_ranges.append(f"0-{max_val}")
        elif isinstance(ar, str) and ar.strip():
            age_ranges.append(strip(ar))
    age_ranges = list(set(age_ranges)) if age_ranges else ['Unknown']
    
    # Location
    locations = get_values(item_data, 'location')
    place_name = None
    latitude = None
    longitude = None
    postal_code = None
    address = None
    
    if locations:
        try:
            place_name = strip(locations[0].get('name'))
        except:
            pass
        try:
            latitude = round(float(locations[0]['geo']['latitude']), 6)
        except:
            pass
        try:
            longitude = round(float(locations[0]['geo']['longitude']), 6)
        except:
            pass
        try:
            postal_code = strip(locations[0].get('address', {}).get('postalCode'))
        except:
            pass
        try: 
            # if address is string  
            if isinstance(locations[0].get('address'), str):
                address = strip(locations[0].get('address'))         
        except:
            pass
    return {
        'organizer_name': organizer_name,
        'activities': activities,
        'facilities': facilities,
        'age_ranges': age_ranges,
        'place_name': place_name,
        'latitude': latitude,
        'longitude': longitude,
        'postal_code': postal_code,
        'address': address,
    }

# Dict cache for region lookups
_region_cache = {}

def find_region_for_location(longitude, latitude, postal_code, address, gdf_regions, name_property, verbose=False):
    """
    Find which region a geographic point belongs to (with caching).
    
    Args:
        longitude: Point longitude
        latitude: Point latitude
        postal_code: Postal code for fallback matching
        address: Address for fallback matching
        gdf_regions: GeoDataFrame with region polygons
        name_property: Property name containing region names
        verbose: Whether to print errors
    
    Returns:
        Region name or None if not found
    """
    cache_key = (longitude, latitude, postal_code, address)
    if cache_key in _region_cache:
        return _region_cache[cache_key]

    region = None
    region = find_region_for_point(longitude, latitude, gdf_regions, name_property, verbose)

    # if lat-long not matched, try to match by postal code if available
    if not region and postal_code:
        lat, long = get_postcode_point(postal_code)
        if lat is not None and long is not None:
            region = find_region_for_point(long, lat, gdf_regions, name_property, verbose)
        
    # if still not matched, try to parse address and match by postcode if available
    if not region and address and type(address) == str:
        try:
            parsed = parse_address(address)
            parsed_address = {label: value.strip().upper() for value, label in parsed}
            if parsed_address.get('postcode'):
                lat, long = get_postcode_point(parsed_address.get('postcode'))
                if lat is not None and long is not None:
                    region = find_region_for_point(long, lat, gdf_regions, name_property, verbose)
        except Exception as e:
            pass

    _region_cache[cache_key] = region
    return region

@lru_cache(maxsize=50_000)
def get_postcode_point(postal_code):
    try:
        lat_long = lookup_postcode_lat_long(postal_code)
        if lat_long:
            lat, long = lat_long
            return lat, long
    except Exception as e:
        pass
    return None, None

def find_region_for_point(longitude, latitude, gdf_regions, name_property, verbose=False):
    """
    Find which region a geographic point belongs to by checking which polygon contains the point.
    
    Args:
        longitude: Point longitude
        latitude: Point latitude
        gdf_regions: GeoDataFrame with region polygons
        name_property: Property name containing region names
        verbose: Whether to print errors
    Returns:
        Region name or None if not found
    """
    if longitude is not None and latitude is not None:
        try:
            point = gpd.points_from_xy([longitude], [latitude])[0]
            contains_mask = gdf_regions.contains(point)
            if contains_mask.any():
                return gdf_regions[name_property][contains_mask].iloc[0]
        except Exception as e:
            if verbose:
                print(f'Error matching point: {e}')
    return None

def resolve_region_via_facility_use(item_data, details, facility_uses_lookup, gdf_regions, name_property, verbose=False):
    """
    Try to find a region by looking up the item's referenced FacilityUse location.
    Also backfills missing location fields in details if FacilityUse has them.
    
    Args:
        item_data: The raw item data
        details: Extracted item details dict (modified in place)
        facility_uses_lookup: Dictionary mapping FacilityUse IDs/URLs to their item data
        gdf_regions: GeoDataFrame with region polygons
        name_property: Property name containing region names
        verbose: Whether to print errors
    
    Returns:
        Region name or None if not resolved
    """
    if not facility_uses_lookup:
        return None
    
    facility_use_ref = item_data.get('facilityUse')
    if isinstance(facility_use_ref, dict):
        facility_use_ref = facility_use_ref.get('@id') or facility_use_ref.get('id')
    if not (facility_use_ref and isinstance(facility_use_ref, str) and facility_use_ref in facility_uses_lookup):
        return None
    
    fu_data = facility_uses_lookup[facility_use_ref]
    fu_details = extract_item_details(fu_data)
    fu_lon = fu_details['longitude']
    fu_lat = fu_details['latitude']
    fu_postal = fu_details['postal_code']
    fu_address = fu_details['address']
    
    if fu_lon is None and fu_lat is None and fu_postal is None and fu_address is None:
        return None
    
    region_name = find_region_for_location(
        fu_lon, fu_lat, fu_postal, fu_address,
        gdf_regions, name_property, verbose
    )
    
    # Backfill missing location fields from FacilityUse
    if details['longitude'] is None and details['latitude'] is None:
        details['longitude'] = fu_lon
        details['latitude'] = fu_lat
    if details['postal_code'] is None:
        details['postal_code'] = fu_postal
    if details['address'] is None:
        details['address'] = fu_address
    if details['place_name'] is None:
        details['place_name'] = fu_details['place_name']
    
    return region_name


def determine_stats_key(longitude, latitude, postal_code, address, region_name, region_stats):
    """
    Determine which stats bucket an item belongs to.
    
    Args:
        longitude: Item longitude
        latitude: Item latitude
        postal_code: Item postal code
        address: Item address
        region_name: Matched region name (may be None)
        region_stats: Dictionary of all region stats
    
    Returns:
        Stats key string, or None if item should be skipped
    """
    if (longitude is None or latitude is None) and postal_code is None and address is None:
        return '_NO_LOCATION'
    elif region_name is None:
        return '_UNMATCHED'
    elif region_name in region_stats:
        return region_name
    else:
        return None  # Region was filtered out


def update_stats_for_item(stats, item_data, details, is_future, is_future_week, filename=None, facility_uses_lookup=None):
    """
    Update region stats with data from a single item.
    
    Args:
        stats: The region stats dictionary to update
        item_data: The raw item data
        details: Extracted item details from extract_item_details()
        is_future: Whether the item is in the future
        is_future_week: Whether the item is in the next week
        filename: Source filename (for debugging unknown activities)
        facility_uses_lookup: Dictionary mapping FacilityUse IDs/URLs to their item data
    """
    stats['total_items'] += 1
    
    if is_future:
        stats['future_items'] += 1
        item_kind = item_data.get('@type') or item_data.get('type', 'Unknown')
        stats['future_event_types'][item_kind] += 1
    
    if is_future_week:
        stats['future_week_items'] += 1
        
        # Track activity breakdown
        activity_found = False
        if details['activities']:
            for activity in details['activities']:
                if activity:
                    stats['future_week_activities_breakdown'][activity] += 1
                    activity_found = True
        
        # If no activity found yet, check facilityType and offers as fallback options
        if not activity_found and 'offers' in item_data:
            if 'facilityType' in item_data and len(item_data['facilityType']) > 0 and 'prefLabel' in item_data['facilityType'][0]:
                stats['future_week_activities_breakdown'][item_data['facilityType'][0]['prefLabel'] + " - Offer"] += 1
                activity_found = True
            elif 'name' in item_data['offers']:
                stats['future_week_activities_breakdown'][item_data['offers']['name'] + " - Offer"] += 1
                activity_found = True
            elif type(item_data['offers']) == list and len(item_data['offers']) > 0 and 'name' in item_data['offers'][0]:
                stats['future_week_activities_breakdown'][item_data['offers'][0]['name'] + " - Offer"] += 1
                activity_found = True

        # if still no activity found, check superEvent (EventSeries) as a last resort 
        if not activity_found and 'superSuperEvent' in item_data:
            super_event = item_data['superSuperEvent']
            if 'activity' in super_event and len(super_event['activity']) > 0 and 'prefLabel' in super_event['activity'][0]:
                stats['future_week_activities_breakdown'][super_event['activity'][0]['prefLabel']] += 1
                activity_found = True
            elif 'name' in super_event:
                stats['future_week_activities_breakdown'][super_event['name']] += 1
                activity_found = True
        
        # if still no activity found, check facilityUse reference
        if not activity_found and facility_uses_lookup:
            facility_use_ref = item_data.get('facilityUse')
            # Handle facilityUse as a dict with @id/id
            if isinstance(facility_use_ref, dict):
                facility_use_ref = facility_use_ref.get('@id') or facility_use_ref.get('id')
            if facility_use_ref and isinstance(facility_use_ref, str) and facility_use_ref in facility_uses_lookup:
                fu_data = facility_uses_lookup[facility_use_ref]
                # Try activity -> prefLabel pattern (list of dicts)
                fu_activities = get_values(fu_data, 'activity', 'prefLabel')
                if fu_activities:
                    for act in fu_activities:
                        if act:
                            stats['future_week_activities_breakdown'][strip(act)] += 1
                            activity_found = True
                # Try activity as a direct string
                if not activity_found:
                    fu_activity = fu_data.get('activity')
                    if isinstance(fu_activity, str) and fu_activity.strip():
                        stats['future_week_activities_breakdown'][fu_activity.strip()] += 1
                        activity_found = True
                # Try activity as a direct string named 'name'
                if not activity_found:
                    fu_activity = fu_data.get('name')
                    if isinstance(fu_activity, str) and fu_activity.strip():
                        stats['future_week_activities_breakdown'][fu_activity.strip()] += 1
                        activity_found = True
        
        if not activity_found:
            stats['future_week_activities_breakdown']['Unknown'] += 1
            if filename:
                print(f'Unknown activity in file: {filename}')
                print(f'Opportunity: {json.dumps(item_data, indent=2, default=str)}')
        
        # Track age range breakdown
        for age_range in details['age_ranges']:
            stats['future_week_age_range_breakdown'][age_range] += 1
    
    if details['organizer_name']:
        stats['organisations'][details['organizer_name']] += 1
    
    if details['place_name']:
        stats['places'].add(details['place_name'])
    
    for activity in details['activities']:
        if activity:
            stats['activities'].add(activity)
    
    for facility in details['facilities']:
        if facility:
            stats['facilities'].add(facility)


# ==================================================================================================
# HELPER FUNCTIONS - Output
# ==================================================================================================

def prepare_region_output(stats, population_lookup):
    """
    Prepare output data for a single region.
    
    Args:
        stats: The region stats dictionary
        population_lookup: Dictionary mapping region names to population
    
    Returns:
        Dictionary with output data for the region
    """
    # Sort breakdowns by count descending
    activities_breakdown = dict(sorted(
        stats['future_week_activities_breakdown'].items(),
        key=lambda x: x[1], reverse=True
    ))
    age_range_breakdown = dict(sorted(
        stats['future_week_age_range_breakdown'].items(),
        key=lambda x: x[1], reverse=True
    ))
    future_event_types = dict(sorted(
        stats['future_event_types'].items(),
        key=lambda x: x[1], reverse=True
    ))
    
    # Look up population
    population = population_lookup.get(stats['region_name'].lower())
    future_items = stats['future_items']
    
    # Calculate activities per 1k population
    activities_per_1k = None
    if population and population > 0:
        activities_per_1k = round((future_items / population) * 1000, 4)
    
    return {
        'region_name': stats['region_name'],
        'total_items': stats['total_items'],
        'future_items': future_items,
        'future_week_items': stats['future_week_items'],
        'population': population,
        'activities_per_1k': activities_per_1k,
        'organisation_count': len(stats['organisations']),
        'unique_organisations': json.dumps(dict(sorted(stats['organisations'].items(), key=lambda x: x[1], reverse=True))),
        'activity_count': len(stats['activities']),
        'unique_activities': json.dumps(list(stats['activities'])),
        'place_count': len(stats['places']),
        'facility_count': len(stats['facilities']),
        'unique_facilities': json.dumps(list(stats['facilities'])),
        'future_week_activities_breakdown': json.dumps(activities_breakdown) if activities_breakdown else '{}',
        'future_week_age_range_breakdown': json.dumps(age_range_breakdown) if age_range_breakdown else '{}',
        'future_event_types': json.dumps(future_event_types) if future_event_types else '{}',
    }


def write_details_csv(output_folder, output_data):
    """
    Write the detailed analysis CSV file.
    
    Args:
        output_folder: Path to output folder
        output_data: List of region output dictionaries
    """
    details_csv_path = os.path.join(output_folder, 'location_analysis_details.csv')
    
    fieldnames = [
        'region_name', 'total_items', 'future_items', 'future_week_items',
        'past_items', 'future_percentage', 'population', 'activities_per_1k',
        'organisation_count', 'unique_organisations', 'activity_count', 'unique_activities',
        'place_count', 'facility_count', 'unique_facilities', 'items_per_organisation',
        'future_week_activities_breakdown', 'future_week_age_range_breakdown', 'future_event_types',
    ]
    
    detailed_data = []
    for row in output_data:
        total = row['total_items']
        future = row['future_items']
        org_count = row['organisation_count']
        
        detailed_data.append({
            'region_name': row['region_name'],
            'total_items': total,
            'future_items': future,
            'future_week_items': row['future_week_items'],
            'past_items': total - future,
            'future_percentage': round(future / total * 100, 2) if total > 0 else 0,
            'population': row['population'],
            'activities_per_1k': row['activities_per_1k'],
            'organisation_count': org_count,
            'unique_organisations': row['unique_organisations'],
            'activity_count': row['activity_count'],
            'unique_activities': row['unique_activities'],
            'place_count': row['place_count'],
            'facility_count': row['facility_count'],
            'unique_facilities': row['unique_facilities'],
            'items_per_organisation': round(total / org_count, 2) if org_count > 0 else 0,
            'future_week_activities_breakdown': row['future_week_activities_breakdown'],
            'future_week_age_range_breakdown': row['future_week_age_range_breakdown'],
            'future_event_types': row['future_event_types'],
        })
    
    with open(details_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detailed_data)
    
    print(f'Details CSV written to: {details_csv_path}')


def print_analysis_summary(output_data, region_names, region_stats):
    """Print analysis summary to console."""
    total_items = sum(r['total_items'] for r in output_data if not r['region_name'].startswith('_'))
    total_future = sum(r['future_items'] for r in output_data if not r['region_name'].startswith('_'))
    total_orgs = sum(r['organisation_count'] for r in output_data if not r['region_name'].startswith('_'))
    total_places = sum(r['place_count'] for r in output_data if not r['region_name'].startswith('_'))
    
    print('\n' + '=' * 60)
    print('ANALYSIS SUMMARY (matched regions only)')
    print('=' * 60)
    print(f'Total regions analysed: {len([r for r in region_names if r in region_stats])}')
    print(f'Total items: {total_items}')
    print(f'Total future items: {total_future}')
    print(f'Total unique organisations: {total_orgs}')
    print(f'Total unique places: {total_places}')
    print(f"Items without location: {region_stats['_NO_LOCATION']['total_items']}")
    print(f"Items unmatched to any region: {region_stats['_UNMATCHED']['total_items']}")
    print('=' * 60)


# ==================================================================================================
# HELPER FUNCTIONS - Data Extraction Utilities
# ==================================================================================================

def get_values(data, sought_parent_keys, sought_child_keys=None, continue_to_next_layer=True):
    """Recursively search for values in nested data structures."""
    values = []

    if not isinstance(sought_parent_keys, list):
        sought_parent_keys = [sought_parent_keys]

    if isinstance(data, dict):
        for key, val in data.items():
            if key in sought_parent_keys:
                if sought_child_keys is None:
                    if val is not None:
                        values.append(val)
                elif type(val) in [dict, list]:
                    values = get_values(val, sought_child_keys, continue_to_next_layer=False)
            elif type(val) in [dict, list] and continue_to_next_layer:
                values = get_values(val, sought_parent_keys, sought_child_keys, continue_to_next_layer)
            if len(values) > 0:
                break
    elif isinstance(data, list):
        values = [
            value
            for datum in data
            for value in get_values(datum, sought_parent_keys, sought_child_keys, continue_to_next_layer)
        ]

    return values


def strip(value):
    """Strip whitespace from a value, returning None if value is None."""
    return str(value).strip() if value is not None else None


def inherit_properties_from_parent(child_data, parent_data, properties_to_inherit=None):
    """
    Inherit missing properties from a parent event to a child event.
    """
    if properties_to_inherit is None:
        properties_to_inherit = [
            'location', 'organizer', 'activity', 'facilityType', 'ageRange',
            'genderRestriction', 'accessibilityInformation',
            'attendeeInstructions', 'eventAttendanceMode', 'offers'
        ]
    
    enhanced_data = dict(child_data)
    
    for prop in properties_to_inherit:
        if prop not in enhanced_data or enhanced_data[prop] is None:
            if prop in parent_data and parent_data[prop] is not None:
                enhanced_data[prop] = parent_data[prop]
    
    properties_to_inherit_with_rename = {
        'superEvent': 'superSuperEvent'
    }
    for prop, new_prop in properties_to_inherit_with_rename.items():
        if prop in parent_data and parent_data[prop] is not None:
            enhanced_data[new_prop] = parent_data[prop]
    
    return enhanced_data


def build_event_relationships(opportunities_pair, event_type_pair):
    """Build mappings between parent (super) events and child (sub) events."""
    superevent_id_v_subevent_ids = {}
    subevent_id_v_superevent_id = {}
    superevent_opportunities = None
    
    if (opportunities_pair[0] is not None 
        and opportunities_pair[1] is not None
        and 'superevent' in event_type_pair 
        and 'subevent' in event_type_pair
    ):
        try:
            superevent_idx = event_type_pair.index('superevent')
            superevent_opportunities = opportunities_pair[superevent_idx]
            
            superevent_id_v_subevent_ids = get_superevent_id_v_subevent_ids(
                opportunities_pair[superevent_idx],
                opportunities_pair[event_type_pair.index('subevent')]
            )
            
            for superevent_id, subevent_ids in superevent_id_v_subevent_ids.items():
                for subevent_id in subevent_ids:
                    subevent_id_v_superevent_id[subevent_id] = superevent_id
        except Exception:
            pass
    
    return superevent_id_v_subevent_ids, subevent_id_v_superevent_id, superevent_opportunities


def get_parent_data_for_item(item_id, subevent_id_v_superevent_id, superevent_opportunities):
    """Get the parent event's data for a given child event."""
    if item_id in subevent_id_v_superevent_id and superevent_opportunities is not None:
        parent_id = subevent_id_v_superevent_id[item_id]
        if parent_id in superevent_opportunities['items']:
            return superevent_opportunities['items'][parent_id].get('data', {})
    return None


# ==================================================================================================
# MAIN ANALYSIS FUNCTION
# ==================================================================================================

def analyse_location_feed(geojson_path, name_property, output_folder, filter_names=None, verbose=False,
                          population_csv=None, population_label_column=None, population_value_column=None,
                          custom_date=None):
    """
    Analyse opportunities data by geographic regions defined in a GeoJSON file.
    
    Args:
        geojson_path: Path to the GeoJSON file defining regions
        name_property: Property name in GeoJSON containing region names
        output_folder: Path to output folder for CSV files
        filter_names: Optional list of region names to filter
        verbose: Whether to print verbose output
        population_csv: Optional path to population CSV file
        population_label_column: Column name in population CSV for region names
        population_value_column: Column name in population CSV for values
    
    Returns:
        Dictionary with analysis results per region
    """
    print(f'Loading GeoJSON from: {geojson_path}')
    print(f'Name property: {name_property}')
    print(f'Output folder: {output_folder}')
    if filter_names:
        print(f'Filtering to regions: {filter_names}')
    
    # Load data
    population_lookup = {}
    if population_csv:
        if not population_label_column or not population_value_column:
            raise ValueError('Both population-label-column and population-value-column must be specified')
        population_lookup = load_population_data(
            population_csv, population_label_column, population_value_column, verbose
        )
    
    gdf_regions, region_names = load_geojson_regions(geojson_path, name_property, filter_names)
    print(f'Analysing {len(region_names)} regions')
    
    # Time boundaries
    todays_date = get_todays_date(custom_date)
    next_weeks_date = todays_date + timedelta(days=7)
    print(f"Using date: {todays_date} (next week: {next_weeks_date})")
    
    # Initialize stats
    region_stats = initialize_all_region_stats(region_names)
    
    # Process files
    filename_pairs = get_filename_pairs()
    num_filename_pairs = len(filename_pairs)
    print(f'Processing {num_filename_pairs} file pairs ...')
    
    t1_overall = datetime.now()
    
    # TODO: for debugging - only process a limited number of files
    # offset = 180
    # limit = 1
    offset = None
    limit = None
    count = 0
    for filename_pair_idx, filename_pair in enumerate(filename_pairs):
        if verbose:
            print(f'File pair: {filename_pair_idx + 1}/{num_filename_pairs}.')
            print(f'  Filenames: {filename_pair}')

        # TODO: for debugging
        if offset and filename_pair_idx < offset:
            continue
        if limit and count >= limit:
            break
        
        # Load file pair
        opportunities_pair = [None, None]
        event_type_pair = [None, None]
        item_types_counts_pair = [None, None]
        
        # Collect FacilityUse objects from both files in the pair
        facility_uses_lookup = {}
        
        for idx, filename in enumerate(filename_pair):
            if filename is None:
                continue
            opportunities, feed_type, item_kinds, item_types, event_type, facility_uses = load_opportunity_file(
                filename, OPPORTUNITIES_RELATIVE_FILEPATH
            )
            opportunities_pair[idx] = opportunities
            event_type_pair[idx] = event_type
            item_types_counts_pair[idx] = item_types
            facility_uses_lookup.update(facility_uses)
        
        # Build relationships
        superevent_id_v_subevent_ids, subevent_id_v_superevent_id, superevent_opportunities = \
            build_event_relationships(opportunities_pair, event_type_pair)
        
        if verbose:
            print(f'  Event types: {event_type_pair}')
            print(f'  Item types: {item_types_counts_pair}')
            if facility_uses_lookup:
                print(f'  Found {len(facility_uses_lookup)} FacilityUse objects')
            if subevent_id_v_superevent_id:
                print(f'  Found {len(subevent_id_v_superevent_id)} child events with parent relationships')
        
        # Process items
        for idx, opportunities in enumerate(opportunities_pair):
            if opportunities is None:
                continue
            
            for item_id, item in opportunities['items'].items():
                item_data = item.get('data', {})
                
                # Inherit from parent if applicable
                parent_data = get_parent_data_for_item(item_id, subevent_id_v_superevent_id, superevent_opportunities)
                if parent_data:
                    item_data = inherit_properties_from_parent(item_data, parent_data)
                
                # Extract data
                is_future, is_future_week = extract_opportunity_dates(item_data, todays_date, next_weeks_date)
                details = extract_item_details(item_data, facility_uses_lookup=facility_uses_lookup)
                
                # Find region
                region_name = find_region_for_location(
                    details['longitude'], details['latitude'], details['postal_code'], details['address'],
                    gdf_regions, name_property, verbose
                )
                
                # If no location or unmatched, try FacilityUse location as fallback
                if region_name is None:
                    region_name = resolve_region_via_facility_use(
                        item_data, details, facility_uses_lookup,
                        gdf_regions, name_property, verbose
                    )
                
                # Determine stats bucket
                stats_key = determine_stats_key(
                    details['longitude'], details['latitude'], details['postal_code'], details['address'],
                    region_name, region_stats
                )
                # if stats_key == '_NO_LOCATION':
                    # TODO: Offers may not have location - they have `facilityUse` and it has location
                    # if verbose:
                    #     print(f'Unknown location in file: {filename}')
                    #     print(f'NO LOCATION: {json.dumps(item_data, indent=2, default=str)}')
                    # continue  # Region was filtered out

                # if stats_key == '_UNMATCHED' and verbose:
                #     print(f'UNMATCHED LOCATION: {json.dumps(item_data, indent=2, default=str)}')

                # Update stats
                update_stats_for_item(
                    region_stats[stats_key], item_data, details,
                    is_future, is_future_week, filename_pair[idx],
                    facility_uses_lookup=facility_uses_lookup
                )
        
        count += 1
    
    t2_overall = datetime.now()
    print(f'Processing completed in: {t2_overall - t1_overall}')
    
    # Generate output
    os.makedirs(output_folder, exist_ok=True)
    
    output_data = [prepare_region_output(stats, population_lookup) for stats in region_stats.values()]
    output_data.sort(key=lambda x: (x['region_name'].startswith('_'), x['region_name']))
    
    write_details_csv(output_folder, output_data)
    
    print('\nAnalysis complete!')
    print_analysis_summary(output_data, region_names, region_stats)
    
    return region_stats


# ==================================================================================================
# CLI
# ==================================================================================================

@click.command()
@click.option('--geojson-path', '-g', required=True, type=click.Path(exists=True),
              help='Path to GeoJSON file defining regions')
@click.option('--name-property', '-n', required=True, type=str,
              help="Property name in GeoJSON containing region names")
@click.option('--filter-names', '-f', multiple=True, type=str,
              help='Optional region names to filter (can be specified multiple times)')
@click.option('--output-folder', '-o', required=True, type=click.Path(),
              help='Path to output folder for CSV files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--population-csv', '-p', type=click.Path(exists=True),
              help='Optional path to population CSV file')
@click.option('--population-label-column', '-pl', type=str,
              help='Column name in population CSV containing region names')
@click.option('--population-value-column', '-pv', type=str,
              help='Column name in population CSV containing population values')
@click.option('--custom-date', '-d', type=str, default=None,
              help='Custom date for testing (format: DD-MM-YYYY, e.g., 16-02-2026)')
def main(geojson_path, name_property, filter_names, output_folder, verbose,
         population_csv, population_label_column, population_value_column, custom_date):
    """Analyse feed data by geographic regions."""
    analyse_location_feed(
        geojson_path=geojson_path,
        name_property=name_property,
        output_folder=output_folder,
        filter_names=list(filter_names) if filter_names else None,
        verbose=verbose,
        population_csv=population_csv,
        population_label_column=population_label_column,
        population_value_column=population_value_column,
        custom_date=custom_date,
    )


if __name__ == '__main__':
    main()
