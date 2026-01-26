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

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_superevent_id_v_subevent_ids, get_event_type, get_item_kinds, get_item_types
from settings import *

# --------------------------------------------------------------------------------------------------

def analyse_location_feed(geojson_path, name_property, output_folder, filter_names=None, verbose=False):
    """
    Analyse opportunities data by geographic regions defined in a GeoJSON file.
    
    Args:
        geojson_path: Path to the GeoJSON file defining regions
        name_property: Property name in GeoJSON containing region names (e.g., 'PARNCP25NM')
        output_folder: Path to output folder for CSV files
        filter_names: Optional list of region names to filter (None = all regions)
        verbose: Whether to print verbose output
    
    Returns:
        Dictionary with analysis results per region
    """
    
    print(f'Loading GeoJSON from: {geojson_path}')
    print(f'Name property: {name_property}')
    print(f'Output folder: {output_folder}')
    if filter_names:
        print(f'Filtering to regions: {filter_names}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Load the GeoJSON file
    gdf_regions = gpd.read_file(geojson_path)
    gdf_regions = gdf_regions.to_crs(4326)
    
    # Validate name_property exists
    if name_property not in gdf_regions.columns:
        raise ValueError(f"Property '{name_property}' not found in GeoJSON. Available properties: {list(gdf_regions.columns)}")
    
    # Get all unique region names
    all_region_names = gdf_regions[name_property].unique().tolist()
    
    # Filter regions if specified
    if filter_names:
        # Validate filter_names exist in the data
        invalid_names = [name for name in filter_names if name not in all_region_names]
        if invalid_names:
            print(f'WARNING: The following region names were not found: {invalid_names}')
        region_names = [name for name in filter_names if name in all_region_names]
        if not region_names:
            raise ValueError('No valid region names to analyse')
    else:
        region_names = all_region_names
    
    print(f'Analysing {len(region_names)} regions')
    
    # --------------------------------------------------------------------------------------------------
    
    todays_date = datetime.now().date()
    next_weeks_date = todays_date + timedelta(days=7)
    
    # --------------------------------------------------------------------------------------------------
    
    # Initialize counters for each region
    region_stats = {
        region_name: {
            'region_name': region_name,
            'total_items': 0,
            'future_items': 0,
            'future_week_items': 0,
            'organisations': set(),
            'places': set(),
            'facilities': set(),
            'activities': set(),
            'future_week_activities_breakdown': defaultdict(int),
            'future_week_age_range_breakdown': defaultdict(int),
        }
        for region_name in region_names
    }
    
    # Add an "unmatched" category for items that don't fall in any region
    region_stats['_UNMATCHED'] = {
        'region_name': '_UNMATCHED',
        'total_items': 0,
        'future_items': 0,
        'future_week_items': 0,
        'organisations': set(),
        'places': set(),
        'facilities': set(),
        'activities': set(),
        'future_week_activities_breakdown': defaultdict(int),
        'future_week_age_range_breakdown': defaultdict(int),
    }
    
    # Add a "no_location" category for items without location data
    region_stats['_NO_LOCATION'] = {
        'region_name': '_NO_LOCATION',
        'total_items': 0,
        'future_items': 0,
        'future_week_items': 0,
        'organisations': set(),
        'places': set(),
        'facilities': set(),
        'activities': set(),
        'future_week_activities_breakdown': defaultdict(int),
        'future_week_age_range_breakdown': defaultdict(int),
    }
    
    # --------------------------------------------------------------------------------------------------
    
    filename_pairs = get_filename_pairs()
    num_filename_pairs = len(filename_pairs)
    
    print(f'Processing {num_filename_pairs} file pairs ...')
    
    t1_overall = datetime.now()
    
    for filename_pair_idx, filename_pair in enumerate(filename_pairs):
        
        if verbose:
            print(f'File pair: {filename_pair_idx + 1}/{num_filename_pairs}')
        
        # --------------------------------------------------------------------------------------------------
        
        # Load both files in the pair to enable parent-child relationship detection
        opportunities_pair = [None, None]
        event_type_pair = [None, None]
        item_types_counts_pair = [None, None]
        item_kinds_counts_pair = [None, None]
        feed_type_pair = [None, None]
        
        for idx, filename in enumerate(filename_pair):
            if filename is None:
                continue
            
            try:
                with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + filename, 'rb') as file_in:
                    opportunities_pair[idx] = pickle.load(file_in)
                    
                    # Get feed type, item kinds, and item types
                    try:
                        feed_type_pair[idx] = opportunities_pair[idx]['feed']['type']
                    except:
                        pass
                    try:
                        item_kinds_counts_pair[idx] = get_item_kinds(opportunities_pair[idx])
                    except:
                        pass
                    try:
                        item_types_counts_pair[idx] = get_item_types(opportunities_pair[idx])
                    except:
                        pass
                    
                    # Determine event type for relationship building (same logic as analyse_separate_opportunities.py)
                    event_type = None
                    if item_types_counts_pair[idx] is not None:
                        event_types = [
                            get_event_type(item_type)
                            for item_type in item_types_counts_pair[idx].keys()
                        ]
                        if len(set(event_types)) == 1:
                            event_type = event_types[0]
                    if event_type is None and item_kinds_counts_pair[idx] is not None:
                        event_types = [
                            get_event_type(item_kind)
                            for item_kind in item_kinds_counts_pair[idx].keys()
                        ]
                        if len(set(event_types)) == 1:
                            event_type = event_types[0]
                    if event_type is None and feed_type_pair[idx] is not None:
                        event_type = get_event_type(feed_type_pair[idx])
                    event_type_pair[idx] = event_type
            except Exception as error:
                print(f'ERROR loading {filename}: {error}')
                continue
        
        # Build parent-child relationships between events in this file pair
        superevent_id_v_subevent_ids, subevent_id_v_superevent_id, superevent_opportunities = \
            build_event_relationships(opportunities_pair, event_type_pair)
        
        if verbose:
            print(f'  Event types: {event_type_pair}')
            print(f'  Item types: {item_types_counts_pair}')
            if subevent_id_v_superevent_id:
                print(f'  Found {len(subevent_id_v_superevent_id)} child events with parent relationships')
            elif 'superevent' in event_type_pair and 'subevent' in event_type_pair:
                print(f'  Superevent/subevent pair detected but no relationships found')
        
        # --------------------------------------------------------------------------------------------------
        
        # Process all items from both files in the pair
        for idx, opportunities in enumerate(opportunities_pair):
            if opportunities is None:
                continue
            
            # --------------------------------------------------------------------------------------------------
            
            for item_id, item in opportunities['items'].items():
                
                item_data = item.get('data', {})
                
                # --------------------------------------------------------------------------------------------------
                
                # Handle parent-child relationships: inherit missing properties from parent
                # This implements schema:subEvent / schema:superEvent property inheritance
                
                parent_data = get_parent_data_for_item(item_id, subevent_id_v_superevent_id, superevent_opportunities)
                if parent_data:
                    item_data = inherit_properties_from_parent(item_data, parent_data)
                
                # --------------------------------------------------------------------------------------------------
                
                # When - determine start dates
                
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
                
                if len(start_dates) > 0:
                    start_date = start_dates[0]
                else:
                    start_date = None
                
                # Determine opportunity start dates
                if len(subevent_start_dates) > 0:
                    opportunity_start_dates = subevent_start_dates
                elif start_date is not None:
                    opportunity_start_dates = [start_date]
                else:
                    opportunity_start_dates = []
                
                # Determine if future/future week
                is_future = any(d >= todays_date for d in opportunity_start_dates)
                is_future_week = any(d >= todays_date and d < next_weeks_date for d in opportunity_start_dates)
                
                # --------------------------------------------------------------------------------------------------
                
                # Who - organizer
                
                organizer_names = get_values(item_data, 'organizer', 'name')
                try:
                    organizer_name = strip(organizer_names[0])
                except:
                    organizer_name = None
                
                # --------------------------------------------------------------------------------------------------
                
                # What - activities and facilities
                
                activities = list(set([strip(value) for value in get_values(item_data, 'activity', 'prefLabel')]))
                facilities = list(set([strip(value) for value in get_values(item_data, 'facilityType', 'prefLabel')]))
                
                # --------------------------------------------------------------------------------------------------
                
                # Who - age range
                
                age_ranges = []
                # Try to get ageRange from item_data
                age_range_data = get_values(item_data, 'ageRange')
                for ar in age_range_data:
                    # if isinstance(ar, dict):
                    #     min_age = ar.get('minValue') or ar.get('minvalue')
                    #     max_age = ar.get('maxValue') or ar.get('maxvalue')
                    #     if min_age is not None or max_age is not None:
                    #         age_range_str = f"{min_age or '?'}-{max_age or '?'}"
                    #         age_ranges.append(age_range_str)
                    if isinstance(ar, str):
                        age_ranges.append(strip(ar))
                
                # Also check for specific age fields
                # if not age_ranges:
                #     min_age = item_data.get('minAge') or item_data.get('minimumAge')
                #     max_age = item_data.get('maxAge') or item_data.get('maximumAge')
                #     if min_age is not None or max_age is not None:
                #         age_range_str = f"{min_age or '?'}-{max_age or '?'}"
                #         age_ranges.append(age_range_str)
                
                age_ranges = list(set(age_ranges)) if age_ranges else ['Unknown']
                
                # --------------------------------------------------------------------------------------------------
                
                # Where - location
                
                locations = get_values(item_data, 'location')
                try:
                    place_name = strip(locations[0].get('name'))
                except:
                    place_name = None
                try:
                    latitude = round(float(locations[0]['geo']['latitude']), 6)
                except:
                    latitude = None
                try:
                    longitude = round(float(locations[0]['geo']['longitude']), 6)
                except:
                    longitude = None
                
                # --------------------------------------------------------------------------------------------------
                
                # Determine which region this item belongs to
                
                region_name = None
                
                if longitude is not None and latitude is not None:
                    try:
                        point = gpd.points_from_xy([longitude], [latitude])[0]
                        contains_mask = gdf_regions.contains(point)
                        if contains_mask.any():
                            region_name = gdf_regions[name_property][contains_mask].iloc[0]
                    except Exception as e:
                        if verbose:
                            print(f'Error matching point: {e}')
                        pass
                
                # Determine which stats bucket to update
                if longitude is None or latitude is None:
                    stats_key = '_NO_LOCATION'
                elif region_name is None:
                    stats_key = '_UNMATCHED'
                elif region_name in region_stats:
                    stats_key = region_name
                else:
                    # Region exists in GeoJSON but was filtered out
                    continue
                
                # --------------------------------------------------------------------------------------------------
                
                # Update stats
                
                stats = region_stats[stats_key]
                stats['total_items'] += 1
                
                if is_future:
                    stats['future_items'] += 1
                
                if is_future_week:
                    stats['future_week_items'] += 1
                    
                    # Track activity breakdown for future week items
                    if activities:
                        for activity in activities:
                            if activity:
                                stats['future_week_activities_breakdown'][activity] += 1
                    else:
                        stats['future_week_activities_breakdown']['Unknown'] += 1
                    
                    # Track age range breakdown for future week items
                    for age_range in age_ranges:
                        stats['future_week_age_range_breakdown'][age_range] += 1
                
                if organizer_name:
                    stats['organisations'].add(organizer_name)
                
                if place_name:
                    stats['places'].add(place_name)
                
                for activity in activities:
                    if activity:
                        stats['activities'].add(activity)
                
                for facility in facilities:
                    if facility:
                        stats['facilities'].add(facility)
    
    # --------------------------------------------------------------------------------------------------
    
    t2_overall = datetime.now()
    print(f'Processing completed in: {t2_overall - t1_overall}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # --------------------------------------------------------------------------------------------------
    
    # Prepare output data - convert sets to counts
    output_data = []
    for region_name, stats in region_stats.items():
        # Sort breakdowns by count descending for better readability
        activities_breakdown = dict(sorted(
            stats['future_week_activities_breakdown'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        age_range_breakdown = dict(sorted(
            stats['future_week_age_range_breakdown'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        output_data.append({
            'region_name': stats['region_name'],
            'total_items': stats['total_items'],
            'future_items': stats['future_items'],
            'future_week_items': stats['future_week_items'],
            'organisation_count': len(stats['organisations']),
            'place_count': len(stats['places']),
            'facility_count': len(stats['facilities']),
            'activity_count': len(stats['activities']),
            'future_week_activities_breakdown': json.dumps(activities_breakdown) if activities_breakdown else '{}',
            'future_week_age_range_breakdown': json.dumps(age_range_breakdown) if age_range_breakdown else '{}',
        })
    
    # Sort by region name, but put special categories at the end
    output_data.sort(key=lambda x: (x['region_name'].startswith('_'), x['region_name']))
    
    # --------------------------------------------------------------------------------------------------
    
    # Write summary CSV
    summary_csv_path = os.path.join(output_folder, 'location_analysis_summary.csv')
    
    fieldnames = [
        'region_name',
        'total_items',
        'future_items',
        'future_week_items',
        'organisation_count',
        'place_count',
        'facility_count',
        'activity_count',
        'future_week_activities_breakdown',
        'future_week_age_range_breakdown',
    ]
    
    with open(summary_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)
    
    print(f'Summary CSV written to: {summary_csv_path}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Write detailed CSV with additional computed fields
    details_csv_path = os.path.join(output_folder, 'location_analysis_details.csv')
    
    detailed_fieldnames = [
        'region_name',
        'total_items',
        'future_items',
        'future_week_items',
        'past_items',
        'future_percentage',
        'organisation_count',
        'place_count',
        'facility_count',
        'activity_count',
        'items_per_organisation',
        'items_per_place',
        'future_week_activities_breakdown',
        'future_week_age_range_breakdown',
    ]
    
    detailed_data = []
    for row in output_data:
        total = row['total_items']
        future = row['future_items']
        org_count = row['organisation_count']
        place_count = row['place_count']
        
        detailed_data.append({
            'region_name': row['region_name'],
            'total_items': total,
            'future_items': future,
            'future_week_items': row['future_week_items'],
            'past_items': total - future,
            'future_percentage': round(future / total * 100, 2) if total > 0 else 0,
            'organisation_count': org_count,
            'place_count': place_count,
            'facility_count': row['facility_count'],
            'activity_count': row['activity_count'],
            'items_per_organisation': round(total / org_count, 2) if org_count > 0 else 0,
            'items_per_place': round(total / place_count, 2) if place_count > 0 else 0,
            'future_week_activities_breakdown': row['future_week_activities_breakdown'],
            'future_week_age_range_breakdown': row['future_week_age_range_breakdown'],
        })
    
    with open(details_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=detailed_fieldnames)
        writer.writeheader()
        writer.writerows(detailed_data)
    
    print(f'Details CSV written to: {details_csv_path}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Write per-region breakdown of organisations
    orgs_csv_path = os.path.join(output_folder, 'location_analysis_organisations.csv')
    
    org_rows = []
    for region_name, stats in region_stats.items():
        for org in sorted(stats['organisations']):
            org_rows.append({
                'region_name': region_name,
                'organisation_name': org,
            })
    
    with open(orgs_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['region_name', 'organisation_name'])
        writer.writeheader()
        writer.writerows(org_rows)
    
    print(f'Organisations CSV written to: {orgs_csv_path}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Write per-region breakdown of places
    places_csv_path = os.path.join(output_folder, 'location_analysis_places.csv')
    
    place_rows = []
    for region_name, stats in region_stats.items():
        for place in sorted(stats['places']):
            place_rows.append({
                'region_name': region_name,
                'place_name': place,
            })
    
    with open(places_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['region_name', 'place_name'])
        writer.writeheader()
        writer.writerows(place_rows)
    
    print(f'Places CSV written to: {places_csv_path}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Write per-region breakdown of activities
    activities_csv_path = os.path.join(output_folder, 'location_analysis_activities.csv')
    
    activity_rows = []
    for region_name, stats in region_stats.items():
        for activity in sorted(stats['activities']):
            activity_rows.append({
                'region_name': region_name,
                'activity_name': activity,
            })
    
    with open(activities_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['region_name', 'activity_name'])
        writer.writeheader()
        writer.writerows(activity_rows)
    
    print(f'Activities CSV written to: {activities_csv_path}')
    
    # --------------------------------------------------------------------------------------------------
    
    # Write per-region breakdown of facilities
    facilities_csv_path = os.path.join(output_folder, 'location_analysis_facilities.csv')
    
    facility_rows = []
    for region_name, stats in region_stats.items():
        for facility in sorted(stats['facilities']):
            facility_rows.append({
                'region_name': region_name,
                'facility_name': facility,
            })
    
    with open(facilities_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['region_name', 'facility_name'])
        writer.writeheader()
        writer.writerows(facility_rows)
    
    print(f'Facilities CSV written to: {facilities_csv_path}')
    
    # --------------------------------------------------------------------------------------------------
    
    print('\nAnalysis complete!')
    
    # Print summary to console
    total_items = sum(row['total_items'] for row in output_data if not row['region_name'].startswith('_'))
    total_future = sum(row['future_items'] for row in output_data if not row['region_name'].startswith('_'))
    total_orgs = sum(row['organisation_count'] for row in output_data if not row['region_name'].startswith('_'))
    total_places = sum(row['place_count'] for row in output_data if not row['region_name'].startswith('_'))
    
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
    
    return region_stats

# --------------------------------------------------------------------------------------------------

def get_values(data, sought_parent_keys, sought_child_keys=None, continue_to_next_layer=True):
    """
    Recursively search for values in nested data structures.
    
    Copied from analyse_separate_opportunities.py for consistency.
    """
    values = []

    if (not isinstance(sought_parent_keys, list)):
        sought_parent_keys = [sought_parent_keys]

    if (isinstance(data, dict)):
        for key, val in data.items():
            if (key in sought_parent_keys):
                if (sought_child_keys is None):
                    if (    (val)
                        and (val is not None)
                    ):
                        values.append(val)
                elif (type(val) in [dict, list]):
                    values = get_values(val, sought_child_keys, continue_to_next_layer=False)
            elif (  (type(val) in [dict, list])
                and (continue_to_next_layer)
            ):
                values = get_values(val, sought_parent_keys, sought_child_keys, continue_to_next_layer)
            if (len(values) > 0):
                break
    elif (isinstance(data, list)):
        values = [
            value
            for datum in data
            for value in get_values(datum, sought_parent_keys, sought_child_keys, continue_to_next_layer)
        ]

    return values

# --------------------------------------------------------------------------------------------------

def strip(value):
    """Strip whitespace from a value, returning None if value is None."""
    if (value is not None):
        return str(value).strip()
    else:
        return value

# --------------------------------------------------------------------------------------------------

def inherit_properties_from_parent(child_data, parent_data, properties_to_inherit=None):
    """
    Inherit missing properties from a parent event to a child event.
    
    This handles the schema:subEvent and schema:superEvent relationship where
    child events (e.g., individual races) may be missing properties that exist
    on their parent event (e.g., whole day event).
    
    Args:
        child_data: The child event's data dictionary
        parent_data: The parent event's data dictionary
        properties_to_inherit: Optional list of property names to inherit.
                              If None, defaults to common properties like location, organizer, etc.
    
    Returns:
        A copy of child_data with inherited properties filled in
    """
    if properties_to_inherit is None:
        # Default properties that are commonly inherited from parent to child events
        properties_to_inherit = [
            'location',          # Where the event takes place
            'organizer',         # Who is organizing the event
            'activity',          # What type of activity
            'facilityType',      # Type of facility
            'ageRange',          # Age restrictions
            'genderRestriction', # Gender restrictions
            'accessibilityInformation',  # Accessibility info
            'attendeeInstructions',      # Instructions for attendees
            'eventAttendanceMode',       # In-person, online, mixed
        ]
    
    # Create a copy to avoid modifying the original
    enhanced_data = dict(child_data)
    
    for prop in properties_to_inherit:
        # Only inherit if child is missing this property and parent has it
        if prop not in enhanced_data or enhanced_data[prop] is None:
            if prop in parent_data and parent_data[prop] is not None:
                enhanced_data[prop] = parent_data[prop]
    
    return enhanced_data

# --------------------------------------------------------------------------------------------------

def build_event_relationships(opportunities_pair, event_type_pair):
    """
    Build mappings between parent (super) events and child (sub) events.
    
    Handles two scenarios:
    1. @id-based relationships: Parent and child events in separate files, linked by @id references
       (e.g., SessionSeries in one file, ScheduledSession in another with superEvent reference)
    2. Inline subEvent relationships: Parent event contains embedded subEvent array
       (e.g., HeadlineEvent with inline Event children)
    
    Args:
        opportunities_pair: Tuple of two opportunities dictionaries (may be None)
        event_type_pair: Tuple of event types ('superevent', 'subevent', or None)
    
    Returns:
        Tuple of (superevent_id_v_subevent_ids, subevent_id_v_superevent_id, superevent_opportunities)
        - superevent_id_v_subevent_ids: Dict mapping parent IDs to lists of child IDs
        - subevent_id_v_superevent_id: Dict mapping child IDs to parent IDs
        - superevent_opportunities: The opportunities dict containing parent events (or None)
    """
    superevent_id_v_subevent_ids = {}
    subevent_id_v_superevent_id = {}
    superevent_opportunities = None
    
    # Scenario 1: @id-based relationships between file pairs
    if (    opportunities_pair[0] is not None 
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
        except Exception as error:
            # Silently ignore errors in relationship building - events without relationships
            # will just be processed without inheritance
            pass
    
    return superevent_id_v_subevent_ids, subevent_id_v_superevent_id, superevent_opportunities

# --------------------------------------------------------------------------------------------------

def get_parent_data_for_item(item_id, subevent_id_v_superevent_id, superevent_opportunities):
    """
    Get the parent event's data for a given child event.
    
    Args:
        item_id: The ID of the child event
        subevent_id_v_superevent_id: Mapping of child IDs to parent IDs
        superevent_opportunities: The opportunities dict containing parent events
    
    Returns:
        The parent event's data dictionary, or None if no parent found
    """
    if (    item_id in subevent_id_v_superevent_id 
        and superevent_opportunities is not None
    ):
        parent_id = subevent_id_v_superevent_id[item_id]
        if parent_id in superevent_opportunities['items']:
            return superevent_opportunities['items'][parent_id].get('data', {})
    return None

# --------------------------------------------------------------------------------------------------

@click.command()
@click.option(
    '--geojson-path', '-g',
    required=True,
    type=click.Path(exists=True),
    help='Path to GeoJSON file defining regions (e.g., volume-1/data-analysis/000-location-parishes.geojson)'
)
@click.option(
    '--name-property', '-n',
    required=True,
    type=str,
    help="Property name in GeoJSON containing region names (e.g., 'PARNCP25NM')"
)
@click.option(
    '--filter-names', '-f',
    multiple=True,
    type=str,
    help='Optional region names to filter (can be specified multiple times). If not provided, all regions are analysed.'
)
@click.option(
    '--output-folder', '-o',
    required=True,
    type=click.Path(),
    help='Path to output folder for CSV files'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
def main(geojson_path, name_property, filter_names, output_folder, verbose):
    """
    Analyse feed data by geographic regions.

    This script reads a GeoJSON file defining geographic regions, then analyses
    all feed data to count events, organisations, places, activities and facilities
    within each region.

    Examples:

    \b
        # Analyse all parishes
        python analyse_location_feed.py \\
            -g ../volume-1/data-analysis/000-location-parishes.geojson \\
            -n PARNCP25NM \\
            -o ./output -v

    \b
        # Analyse specific parishes
        python analyse_location_feed.py \\
            -g ../volume-1/data-analysis/000-location-parishes.geojson \\
            -n PARNCP25NM \\
            -f "Blackrod" -f "Bolton" \\
            -o ./output -v

    \b
        # Analyse regions
        python analyse_location_feed.py \\
            -g ../volume-1/data-analysis/000-location-regions.geojson \\
            -n eer18nm \\
            -o ./output -v
    """
    
    filter_list = list(filter_names) if filter_names else None
    
    analyse_location_feed(
        geojson_path=geojson_path,
        name_property=name_property,
        output_folder=output_folder,
        filter_names=filter_list,
        verbose=verbose,
    )

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
