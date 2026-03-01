import geopandas as gpd
import gzip
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import parser
from functools import lru_cache

from shapely import STRtree
from shapely.geometry import Point

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_item_kinds, get_item_types, get_event_type, get_superevent_id_v_subevent_ids
from settings import *


def build_spatial_index(gdf, name_column):
    """
    Build a spatial index for fast point-in-polygon lookups.
    Args:
        gdf (GeoDataFrame): GeoDataFrame containing the geometries and names.
        name_column (str): Name of the column in gdf that contains the names to return on lookup.
    Returns:
        tree (STRtree): Spatial index for the geometries.
        geometries (list): List of geometries corresponding to the index.
        names (list): List of names corresponding to the geometries.
    """
    tree = STRtree(gdf.geometry.values)
    geometries = gdf.geometry.values
    names = gdf[name_column].values
    return tree, geometries, names

def lookup_location(point, tree, geometries, names):
    """
    Fast point-in-polygon lookup using spatial index.
    Args:
        point (Point): The point to look up.
        tree (STRtree): Spatial index for the geometries.
        geometries (list): List of geometries corresponding to the index.
        names (list): List of names corresponding to the geometries.
    Returns:
        str: The name corresponding to the geometry that contains the point, or None if not found.
    """
    if point is None:
        return None
    candidates = tree.query(point)
    for idx in candidates:
        try:
            if geometries[idx].contains(point):
                return names[idx]
        except Exception:
            # Skip geometries that cause TopologyException or other errors
            continue
    return None

# Global spatial indexes (set by analyse_separate_opportunities)
_regions_index = None
_districts_index = None
_parishes_index = None
_gps_index = None

@lru_cache(maxsize=100000)
def cached_geo_lookup(longitude, latitude):
    """
    Cached geo lookup for repeated coordinates.
    Returns tuple of (region, district, parish, gp).
    """
    global _regions_index, _districts_index, _parishes_index, _gps_index
    try:
        point = Point(longitude, latitude)
    except:
        return None, None, None, None
    
    region = lookup_location(point, *_regions_index)
    district = lookup_location(point, *_districts_index)
    parish = lookup_location(point, *_parishes_index)
    gp = lookup_location(point, *_gps_index)
    
    return region, district, parish, gp

def parse_date(date_string):
    """
    Fast date parsing with fallback to dateutil.
    Tries ISO format first (most common), then falls back to dateutil.parser.
    """
    if date_string is None:
        return None
    try:
        return parser.parse(date_string).date()
    except:
        return None

def extract_location_data(item_data):
    """
    Extract location data (postcode, latitude, longitude) from item data.
    Returns dict with postcode, latitude, longitude keys.
    """
    locations = get_values(item_data, 'location')
    try:
        postcode = strip(locations[0]['address']['postalCode'])
    except:
        postcode = None
    try:
        latitude = round(float(locations[0]['geo']['latitude']), 6)
    except:
        latitude = None
    try:
        longitude = round(float(locations[0]['geo']['longitude']), 6)
    except:
        longitude = None
    
    return {
        'postcode': postcode,
        'latitude': latitude,
        'longitude': longitude
    }

def get_geo_names(longitude, latitude):
    """
    Get region, district, parish, gp names for a coordinate using cached lookup.
    Returns tuple of (region, district, parish, gp).
    """
    if longitude is None or latitude is None:
        return None, None, None, None
    return cached_geo_lookup(longitude, latitude)

def analyse_separate_opportunities(**kwargs):
    verbose = kwargs.get('verbose', False)

    # --------------------------------------------------------------------------------------------------

    gdf_regions = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_REGIONS_FILENAME)
    gdf_regions = gdf_regions.to_crs(4326)

    gdf_districts = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_DISTRICTS_FILENAME)
    gdf_districts = gdf_districts.to_crs(4326)

    gdf_parishes = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_PARISHES_FILENAME)
    gdf_parishes = gdf_parishes.to_crs(4326)

    gdf_gps = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_GPS_FILENAME)
    gdf_gps = gdf_gps.to_crs(4326)

    # Build spatial indexes for fast point-in-polygon lookups
    print('Building spatial indexes...')
    global _regions_index, _districts_index, _parishes_index, _gps_index
    _regions_index = build_spatial_index(gdf_regions, 'eer18nm')
    _districts_index = build_spatial_index(gdf_districts, 'LAD24NM')
    _parishes_index = build_spatial_index(gdf_parishes, 'PARNCP25NM')
    _gps_index = build_spatial_index(gdf_gps, 'Name')
    
    # Clear the geo lookup cache for fresh run
    cached_geo_lookup.cache_clear()

    todays_date = datetime.now().date()
    # todays_date = datetime(2026,2,16).date() # Use this to set to a fixed date if needed for testing e.g. running on the same input data but working over multiple days
    next_weeks_date = todays_date + timedelta(days=7)

    # --------------------------------------------------------------------------------------------------

    filename_pairs = get_filename_pairs()
    num_filename_pairs = len(filename_pairs)

    filenames = [
        filename
        for filename_pair in filename_pairs
        for filename in filename_pair
        if filename is not None
    ]
    unique_filenames = list(set(filenames))

    num_filenames = len(filenames)
    num_unique_filenames = len(unique_filenames)

    if (num_filenames != num_unique_filenames):
        raise Exception('At least one filename has been partnered with more than one other filename. This should not occur and the filename pairing procedure needs to be investigated.')

    # If we want to know the total number of items in all opportunities files before they are processed,
    # (in order to e.g. pre-size containers such as lists or dataframes) then we can determine this
    # from the file name stamps as follows, which is much quicker than opening the files to count the
    # items:

    # total_num_items = 0
    # for filename in filenames:
    #     total_num_items += int(filename.split('numItems-')[1].split('--')[0])

    # --------------------------------------------------------------------------------------------------

    # List the items we want to collect for each feed. These column headers need to be specified here in
    # advance of row insertion into the DataFrame.

    # The comments after each line show the data types.

    # Entries which can't be determined are filled with None rather than the empty version of the type
    # they relate to e.g. an empty string for strings, or zero for integers etc.

    feeds = pd.DataFrame(columns=[
        'feed_id', # STR
        'partner_feed_id', # STR
        'file_name', # STR
        'dataset_name', # STR
        'publisher_name', # STR

        'feed_url', # STR
        'dataset_url', # STR
        'discussion_url', # STR
        'license_url', # STR
        'logo_url', # STR

        'status', # STR
        'is_regular', # BOOL
        'event_type', # STR
        'feed_type', # STR
        'item_kinds_counts', # {STR: INT}
        'item_types_counts', # {STR: INT}
        'merged_item_kinds_counts', # {STR: INT}
        'merged_item_types_counts', # {STR: INT}

        'organizer_names_counts', # {STR: INT}
        'activities_counts', # {STR: INT}
        'facilities_counts', # {STR: INT}
        'accessibilities_counts', # {STR: INT}
        'regions_counts', # {STR: INT}
        'districts_counts', # {STR: INT}
        'parishes_counts', # {STR: INT}
        'gps_counts', # {STR: INT}

        'num_items', # INT
        'num_analysis_items', # INT

        'num_partnered_items', # INT
        'num_unpartnered_items', # INT

        'num_opportunity_start_dates', # INT
        'num_future_opportunity_start_dates', # INT
        'num_future_week_opportunity_start_dates', # INT

        'num_opportunity_items', # INT
        'num_future_opportunity_items', # INT
        'num_future_week_opportunity_items', # INT
    ])

    filenames_sampleitems = {}

    # --------------------------------------------------------------------------------------------------

    prepare_times = []
    process_times = []

    t1_overall = datetime.now()

    for filename_pair_idx, filename_pair in enumerate(filename_pairs):

        # Use if need to do a limited run for testing:
        # if (filename_pair_idx == 1):
        #     break

        t1 = datetime.now()

        print(f'File pair: {filename_pair_idx + 1}/{num_filename_pairs}')
        print('Preparing ...')

        # --------------------------------------------------------------------------------------------------

        opportunities_pair = []
        for filename in filename_pair:
            opportunities = None
            if (filename is not None):
                try:
                    with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + filename, 'rb') as file_in:
                        opportunities = pickle.load(file_in)
                except Exception as error:
                    print('ERROR:', error)
            opportunities_pair.append(opportunities)

        # --------------------------------------------------------------------------------------------------

        feed_type_pair = []
        for opportunities in opportunities_pair:
            feed_type = None
            if (opportunities is not None):
                try:
                    feed_type = opportunities['feed']['type']
                except Exception as error:
                    print('ERROR:', error)
            feed_type_pair.append(feed_type)

        # --------------------------------------------------------------------------------------------------

        item_kinds_counts_pair = []
        for opportunities in opportunities_pair:
            item_kinds_counts = None
            if (opportunities is not None):
                try:
                    item_kinds_counts = get_item_kinds(opportunities)
                except Exception as error:
                    print('ERROR:', error)
            item_kinds_counts_pair.append(item_kinds_counts)

        # --------------------------------------------------------------------------------------------------

        item_types_counts_pair = []
        for opportunities in opportunities_pair:
            item_types_counts = None
            if (opportunities is not None):
                try:
                    item_types_counts = get_item_types(opportunities)
                except Exception as error:
                    print('ERROR:', error)
            item_types_counts_pair.append(item_types_counts)

        # --------------------------------------------------------------------------------------------------

        event_type_pair = []
        for opportunity_idx, opportunities in enumerate(opportunities_pair):
            event_type = None
            if (opportunities is not None):
                try:
                    if (item_types_counts_pair[opportunity_idx] is not None):
                        event_types = [
                            get_event_type(item_type)
                            for item_type in item_types_counts_pair[opportunity_idx].keys()
                        ]
                        if (len(set(event_types)) == 1):
                            event_type = event_types[0]
                    if (    (event_type is None)
                        and (item_kinds_counts_pair[opportunity_idx] is not None)
                    ):
                        event_types = [
                            get_event_type(item_kind)
                            for item_kind in item_kinds_counts_pair[opportunity_idx].keys()
                        ]
                        if (len(set(event_types)) == 1):
                            event_type = event_types[0]
                    if (    (event_type is None)
                        and (feed_type_pair[opportunity_idx] is not None)
                    ):
                        event_type = get_event_type(feed_type_pair[opportunity_idx])
                except Exception as error:
                    print('ERROR:', error)
            event_type_pair.append(event_type)

        # --------------------------------------------------------------------------------------------------

        superevent_id_v_subevent_ids = {}
        subevent_id_v_superevent_id = {}
        num_partnered_superevent_items = None
        num_partnered_subevent_items = None
        num_unpartnered_superevent_items = None
        num_unpartnered_subevent_items = None
        if (    ('superevent' in event_type_pair)
            and ('subevent' in event_type_pair)
        ):
            try:
                superevent_id_v_subevent_ids = get_superevent_id_v_subevent_ids(
                    opportunities_pair[event_type_pair.index('superevent')],
                    opportunities_pair[event_type_pair.index('subevent')]
                )
                for superevent_id, subevent_ids in superevent_id_v_subevent_ids.items():
                    for subevent_id in subevent_ids:
                        subevent_id_v_superevent_id[subevent_id] = superevent_id
            except Exception as error:
                print('ERROR:', error)
            num_superevent_items = len(opportunities_pair[event_type_pair.index('superevent')]['items'].keys())
            num_subevent_items = len(opportunities_pair[event_type_pair.index('subevent')]['items'].keys())
            num_partnered_superevent_items = len(superevent_id_v_subevent_ids.keys())
            num_partnered_subevent_items = len(subevent_id_v_superevent_id.keys())
            num_unpartnered_superevent_items = num_superevent_items - num_partnered_superevent_items
            num_unpartnered_subevent_items = num_subevent_items - num_partnered_subevent_items

        # --------------------------------------------------------------------------------------------------

        print(f'\tFile-1:')
        print(f'\t\tName: {filename_pair[0]}')
        print(f'\t\tLoaded: {opportunities_pair[0] is not None}')
        print(f'\t\tEvent type: {event_type_pair[0]}')
        print(f'\t\tFeed type: {feed_type_pair[0]}')
        print(f'\t\tItem kinds: {item_kinds_counts_pair[0]}')
        print(f'\t\tItem types: {item_types_counts_pair[0]}')

        print(f'\tFile-2:')
        print(f'\t\tName: {filename_pair[1]}')
        print(f'\t\tLoaded: {opportunities_pair[1] is not None}')
        print(f'\t\tEvent type: {event_type_pair[1]}')
        print(f'\t\tFeed type: {feed_type_pair[1]}')
        print(f'\t\tItem kinds: {item_kinds_counts_pair[1]}')
        print(f'\t\tItem types: {item_types_counts_pair[1]}')

        print(f'\tItem partnering:')
        print(f'\t\tnum_superevent_items: {num_superevent_items}')
        print(f'\t\tnum_subevent_items: {num_subevent_items}')
        print(f'\t\tnum_partnered_superevent_items: {num_partnered_superevent_items}')
        print(f'\t\tnum_partnered_subevent_items: {num_partnered_subevent_items}')
        print(f'\t\tnum_unpartnered_superevent_items: {num_unpartnered_superevent_items}')
        print(f'\t\tnum_unpartnered_subevent_items: {num_unpartnered_subevent_items}')

        # --------------------------------------------------------------------------------------------------

        t2 = datetime.now()
        prepare_times.append((t2 - t1).total_seconds())

        t1 = datetime.now()

        print('Processing ...')

        for opportunity_idx, opportunities in enumerate(opportunities_pair):
            if (opportunities is None):
                continue

            print(f'\tFile-{opportunity_idx + 1}:')

            # --------------------------------------------------------------------------------------------------

            feed_num_items = len(opportunities['items'].keys())
            feed_num_analysis_items = 0

            feed_num_opportunity_start_dates = 0
            feed_num_future_opportunity_start_dates = 0
            feed_num_future_week_opportunity_start_dates = 0

            feed_num_opportunity_items = 0
            feed_num_future_opportunity_items = 0
            feed_num_future_week_opportunity_items = 0

            future_week_opportunity_item_ids = []

            merged_item_kinds_counts = {}
            merged_item_types_counts = {}
            organizer_names_counts = {}
            activities_counts = {}
            facilities_counts = {}
            accessibilities_counts = {}
            regions_counts = {}
            districts_counts = {}
            parishes_counts = {}
            gps_counts = {}

            for item_idx, item in enumerate(opportunities['items'].values()):
                # TODO: Disable this count if running live on GCloud, as the logs there don't do carriage return, so
                # you'll just end up with a long list of numbers if this is enabled:
                # if (   ((item_idx + 1) % 10 == 0)
                #     or ((item_idx + 1) == feed_num_items)
                # ):
                #     print(f'\t\tItem: {item_idx + 1}/{feed_num_items}', end=('\n' if ((item_idx + 1) == feed_num_items) else '\r'))

                # Leave this in play, we can and do have instances where an item has no data field, so this is a needed
                # safety check:
                item_data = item.get('data', {})

                # --------------------------------------------------------------------------------------------------

                # When

                # Don't use .astimezone(tz.UTC) here - if there is a date but no time then it defaults to midnight,
                # so giving e.g. '2025-06-18' would then be converted to '2025-06-17' by the tz.UTC conversion.

                start_dates = []
                for start_datetime in get_values(item_data, ['startDate', 'dateStart'], continue_to_next_layer=False):
                    parsed = parse_date(start_datetime)
                    if parsed:
                        start_dates.append(parsed)

                subevent_start_dates = []
                for subevent_start_datetime in get_values(item_data, 'subEvent', ['startDate', 'dateStart'], continue_to_next_layer=False):
                    parsed = parse_date(subevent_start_datetime)
                    if parsed:
                        subevent_start_dates.append(parsed)

                if (len(start_dates) > 0):
                    start_date = start_dates[0] # There should only be one i.e. zeroth index
                else:
                    start_date = None

                # Note that a superevent feed with a partnered subevent feed may nonetheless also have some embedded
                # subevent items e.g. https://bookwhen.com/api/openactive/sessionseries. Not sure if this is totally
                # kosher, but it is done.

                # If looking for eventSchedule in further iterations of this code, take care that subEvent with startDate
                # is not also present e.g. https://api.clubspark.uk/odi/public/courses

                # --------------------------------------------------------------------------------------------------

                # If this is a superevent item with subevents via ID and no subevents via embedding, then it will be
                # wholly used and referred to by the subevents via ID, so we skip over it here as it is not something
                # to separately analyse by itself:

                if (    (event_type_pair[opportunity_idx] == 'superevent')
                    and (item['id'] in superevent_id_v_subevent_ids.keys())
                    and (len(subevent_start_dates) == 0)
                ):
                    continue

                feed_num_analysis_items += 1

                # --------------------------------------------------------------------------------------------------

                # If this is a subevent item with a superevent partner, then we modify the subevent content with the
                # contextual superevent info:

                if (    (event_type_pair[opportunity_idx] == 'subevent')
                    and (item['id'] in subevent_id_v_superevent_id.keys())
                ):
                    partner_item_id = subevent_id_v_superevent_id[item['id']]
                    partner_item = opportunities_pair[1-opportunity_idx]['items'][partner_item_id]
                    partner_item_data = partner_item.get('data', {})
                else:
                    partner_item = None

                # --------------------------------------------------------------------------------------------------

                item_kind = strip(item.get('kind', None))
                item_type = strip(item_data.get('type', None) or item_data.get('@type', None))

                if (partner_item is not None):
                    # Define a new item kind and item type for these partnered items:
                    partner_item_kind = strip(partner_item.get('kind', None))
                    partner_item_type = strip(partner_item_data.get('type', None) or partner_item_data.get('@type', None))
                    item_kind = '_x_'.join([str(item_kind), str(partner_item_kind)])
                    item_type = '_x_'.join([str(item_type), str(partner_item_type)])

                # --------------------------------------------------------------------------------------------------

                # Who

                # If we get multiple values back (not expected but possible), use the first only i.e. zeroth index:

                organizer_names = get_values(item_data, 'organizer', 'name')

                try:
                    organizer_name = strip(organizer_names[0])
                except:
                    organizer_name = None

                if (    (partner_item is not None)
                    and (organizer_name is None)
                ):
                    partner_organizer_names = get_values(partner_item_data, 'organizer', 'name')
                    try:
                        organizer_name = strip(partner_organizer_names[0])
                    except:
                        organizer_name = None

                # --------------------------------------------------------------------------------------------------

                # What

                activities = list(set([strip(value) for value in get_values(item_data, 'activity', 'prefLabel')]))
                if (partner_item is not None):
                    partner_activities = list(set([strip(value) for value in get_values(partner_item_data, 'activity', 'prefLabel')]))
                    activities = list(set(activities + partner_activities))
                if (len(activities) == 0):
                    activities = [None]

                facilities = list(set([strip(value) for value in get_values(item_data, 'facilityType', 'prefLabel')]))
                if (partner_item is not None):
                    partner_facilities = list(set([strip(value) for value in get_values(partner_item_data, 'facilityType', 'prefLabel')]))
                    facilities = list(set(facilities + partner_facilities))
                if (len(facilities) == 0):
                    facilities = [None]

                accessibilities = list(set([strip(value) for value in get_values(item_data, 'accessibilitySupport', 'prefLabel')]))
                if (partner_item is not None):
                    partner_accessibilities = list(set([strip(value) for value in get_values(partner_item_data, 'accessibilitySupport', 'prefLabel')]))
                    accessibilities = list(set(accessibilities + partner_accessibilities))
                if (len(accessibilities) == 0):
                    accessibilities = [None]

                # --------------------------------------------------------------------------------------------------

                # Where

                # If we get multiple values back (not expected but possible), use the first only i.e. zeroth index:

                # Note that the point-by-point region/district mapping is slower than the bulk sjoin approach on GeoPandas
                # dataframe input but much more accurate. The more data given to the bulk sjoin approach, the fewer
                # entries are matched. If there is a future need to use the bulk sjoin approach, it may be possible
                # to improve performance by twiddling gpd settings. Search for gpd.sjoin inaccuracies for info.

                # Extract location data using helper function
                loc_data = extract_location_data(item_data)
                postcode = loc_data['postcode']
                latitude = loc_data['latitude']
                longitude = loc_data['longitude']

                # Use cached spatial index lookup for geo names
                region, district, parish, gp = get_geo_names(longitude, latitude)

                if (    (partner_item is not None)
                    and (   (postcode is None)
                        or  (latitude is None)
                        or  (longitude is None)
                        or  (region is None)
                        or  (district is None) 
                        or  (parish is None)
                        or  (gp is None)
                        )
                ):
                    # Extract partner location data using helper function
                    partner_loc_data = extract_location_data(partner_item_data)
                    partner_postcode = partner_loc_data['postcode']
                    partner_latitude = partner_loc_data['latitude']
                    partner_longitude = partner_loc_data['longitude']

                    # Use cached spatial index lookup for partner geo names
                    partner_region, partner_district, partner_parish, partner_gp = get_geo_names(
                        partner_longitude, partner_latitude
                    )

                    if (    (postcode is None)
                        and (partner_postcode is not None)
                    ):
                        postcode = partner_postcode
                    if (    (latitude is None)
                        and (partner_latitude is not None)
                    ):
                        latitude = partner_latitude
                    if (    (longitude is None)
                        and (partner_longitude is not None)
                    ):
                        longitude = partner_longitude
                    if (    (region is None)
                        and (partner_region is not None)
                    ):
                        region = partner_region
                    if (    (district is None)
                        and (partner_district is not None)
                    ):
                        district = partner_district
                    if (    (parish is None)
                        and (partner_parish is not None)
                    ):
                        parish = partner_parish
                    if (    (gp is None)
                        and (partner_gp is not None)
                    ):
                        gp = partner_gp

                # --------------------------------------------------------------------------------------------------

                # Regardless of classification of this item as a superevent or subevent, if there are embedded subevent
                # start dates then these are likely to be the ones we want for the individual sessions/slots which
                # are usually thought of as the individual "opportunities". If we don't have such start dates, then
                # we choose to accept root level start dates from subevents only, as those from superevents are (or
                # should be) for the start of a set of sessions/slots, which, as just indicated, are not usually thought
                # of as the individual "opportunities". We therefore have a distinction between:
                #     1) Item - any item of any superevent/subevent classification and any content
                #     2) Future item - an item with at least one future start date, either at the root level or from
                #        embedded subevents
                #     3) Opportunity item - a superevent/subevent item with embedded subevent start dates, or a subevent
                #        with a root level start date
                #     4) Future opportunity item - an opportunity item with at least one future start date, either
                #        at the root level or from embedded subevents
                # Ultimately, it is the future opportunity items that we end up counting below. We also count the start
                # dates and future start dates, and it may be preferable to re-cast the sense of "an opportunity" from
                # an item to an instance of a start date within an item. TODO: Consider this and adjust accordingly.

                if (len(subevent_start_dates) > 0):
                    opportunity_start_dates = subevent_start_dates
                elif (  (event_type_pair[opportunity_idx] == 'subevent')
                    and (start_date is not None)
                ):
                    opportunity_start_dates = [start_date]
                else:
                    opportunity_start_dates = None

                if (opportunity_start_dates is not None):
                    num_opportunity_start_dates = len(opportunity_start_dates)
                    num_future_opportunity_start_dates = len([
                        opportunity_start_date
                        for opportunity_start_date in opportunity_start_dates
                        if (opportunity_start_date >= todays_date)
                    ])
                    num_future_week_opportunity_start_dates = len([
                        opportunity_start_date
                        for opportunity_start_date in opportunity_start_dates
                        if (    (opportunity_start_date >= todays_date)
                            and (opportunity_start_date < next_weeks_date) )
                    ])
                else:
                    num_opportunity_start_dates = 0
                    num_future_opportunity_start_dates = 0
                    num_future_week_opportunity_start_dates = 0

                feed_num_opportunity_start_dates += num_opportunity_start_dates
                feed_num_future_opportunity_start_dates += num_future_opportunity_start_dates
                feed_num_future_week_opportunity_start_dates += num_future_week_opportunity_start_dates

                if (num_opportunity_start_dates > 0):
                    feed_num_opportunity_items += 1
                if (num_future_opportunity_start_dates > 0):
                    feed_num_future_opportunity_items += 1
                if (num_future_week_opportunity_start_dates > 0):
                    feed_num_future_week_opportunity_items += 1
                    future_week_opportunity_item_ids.append(item['id'])

                # --------------------------------------------------------------------------------------------------

                update_values_counts(merged_item_kinds_counts, item_kind)
                update_values_counts(merged_item_types_counts, item_type)

                update_values_counts(organizer_names_counts, organizer_name)

                for activity in activities:
                    update_values_counts(activities_counts, activity)

                for facility in facilities:
                    update_values_counts(facilities_counts, facility)

                for accessibility in accessibilities:
                    update_values_counts(accessibilities_counts, accessibility)

                update_values_counts(regions_counts, region)
                update_values_counts(districts_counts, district)
                update_values_counts(parishes_counts, parish)
                update_values_counts(gps_counts, gp)

            # --------------------------------------------------------------------------------------------------

            if (opportunities_pair[1-opportunity_idx] is not None):
                partner_feed_id = opportunities_pair[1-opportunity_idx]['feed']['id']
            else:
                partner_feed_id = None

            if (feed_num_future_week_opportunity_items > 0):
                filenames_sampleitems[filename_pair[opportunity_idx]] = {
                    item_id: opportunities['items'][item_id]
                    for item_id in random.sample(future_week_opportunity_item_ids, min(2, feed_num_future_week_opportunity_items))
                }

            feeds.loc[len(feeds)] = {
                'feed_id': opportunities['feed']['id'],
                'partner_feed_id': partner_feed_id,
                'file_name': filename_pair[opportunity_idx],
                'dataset_name': opportunities['feed']['dataset_name'],
                'publisher_name': opportunities['feed']['publisher_name'],

                'feed_url': opportunities['feed']['url'],
                'dataset_url': opportunities['feed']['dataset_url'],
                'discussion_url': opportunities['feed']['discussion_url'],
                'license_url': opportunities['feed']['license_url'],
                'logo_url': opportunities['feed']['logo_url'],

                'status': opportunities['status'],
                'is_regular': filename_pair[opportunity_idx].startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE),
                'event_type': event_type_pair[opportunity_idx],
                'feed_type': opportunities['feed']['type'],
                'item_kinds_counts': item_kinds_counts_pair[opportunity_idx],
                'item_types_counts': item_types_counts_pair[opportunity_idx],
                'merged_item_kinds_counts': merged_item_kinds_counts,
                'merged_item_types_counts': merged_item_types_counts,

                'organizer_names_counts': organizer_names_counts,
                'activities_counts': activities_counts,
                'facilities_counts': facilities_counts,
                'accessibilities_counts': accessibilities_counts,
                'regions_counts': regions_counts,
                'districts_counts': districts_counts,
                'parishes_counts': parishes_counts,
                'gps_counts': gps_counts,

                'num_items': feed_num_items,
                'num_analysis_items': feed_num_analysis_items,

                'num_partnered_items':
                    num_partnered_superevent_items if (event_type_pair[opportunity_idx] == 'superevent')
                    else num_partnered_subevent_items if (event_type_pair[opportunity_idx] == 'subevent')
                    else None,
                'num_unpartnered_items':
                    num_unpartnered_superevent_items if (event_type_pair[opportunity_idx] == 'superevent')
                    else num_unpartnered_subevent_items if (event_type_pair[opportunity_idx] == 'subevent')
                    else None,

                'num_opportunity_start_dates': feed_num_opportunity_start_dates,
                'num_future_opportunity_start_dates': feed_num_future_opportunity_start_dates,
                'num_future_week_opportunity_start_dates': feed_num_future_week_opportunity_start_dates,

                'num_opportunity_items': feed_num_opportunity_items,
                'num_future_opportunity_items': feed_num_future_opportunity_items,
                'num_future_week_opportunity_items': feed_num_future_week_opportunity_items,
            }

        # --------------------------------------------------------------------------------------------------

        t2 = datetime.now()
        process_times.append((t2 - t1).total_seconds())

        print(f'Time taken:')
        print(f'\tPrepare: {round(prepare_times[-1], 6)} seconds')
        print(f'\tProcess: {round(process_times[-1], 6)} seconds')
        print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    t2_overall = datetime.now()

    total_prepare_time = sum(prepare_times)
    total_process_time = sum(process_times)
    total_prepare_process_time = total_prepare_time + total_process_time

    print(f'Time taken for all file pairs:')
    print(f'\tPrepare:')
    print(f'\t\tsum({prepare_times})')
    print(f'\t\t= {round(total_prepare_time, 6)} seconds')
    print(f'\t\t= {round(total_prepare_time / 60, 2)} minutes')
    print(f'\t\t= {round(total_prepare_time / (60 * 60), 2)} hours') # ~??? on M1 8GB MacBook Air
    print(f'\tProcess:')
    print(f'\t\tsum({process_times})')
    print(f'\t\t= {round(total_process_time, 6)} seconds')
    print(f'\t\t= {round(total_process_time / 60, 2)} minutes')
    print(f'\t\t= {round(total_process_time / (60 * 60), 2)} hours') # ~??? on M1 8GB MacBook Air
    print(f'\tPrepare + Process (from summing individual times):')
    print(f'\t\t  {round(total_prepare_process_time, 6)} seconds')
    print(f'\t\t= {round(total_prepare_process_time / 60, 2)} minutes')
    print(f'\t\t= {round(total_prepare_process_time / (60 * 60), 2)} hours') # ~??? on M1 8GB MacBook Air
    print(f'\tPrepare + Process (from overall start and end times):')
    print(f'\t\t  {t2_overall - t1_overall}') # ~??? on M1 8GB MacBook Air
    print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    print('Writing out separate feed analysis ...')

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SEPARATE_ANALYSIS_FILENAME, 'wb') as file_out:
        pickle.dump(feeds, file_out)
    t2 = datetime.now()
    print(f'\tTime taken: {t2 - t1}') # ~??? (~???MB) on M1 8GB MacBook Air

    # --------------------------------------------------------------------------------------------------

    print('Writing out sample items ...')

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SAMPLE_ITEMS_FILENAME, 'wb') as file_out:
        pickle.dump(filenames_sampleitems, file_out)
    t2 = datetime.now()
    print(f'\tTime taken: {t2 - t1}') # ~??? (~???MB) on M1 8GB MacBook Air

# --------------------------------------------------------------------------------------------------

def get_values(data, sought_parent_keys, sought_child_keys=None, continue_to_next_layer=True):
    values = []

    # This function accepts sought_parent_keys and sought_child_keys as either a single key or a list of
    # key variants e.g. ['type', '@type']. We normalise to a list for standardised handling:
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
                    # If we are seeking a parent-child key pair and have found the parent key, then sought_child_keys becomes
                    # sought_parent_keys for the next layer search. We also only want to search the immediate next layer
                    # and not beyond, hence the keyword setting here:
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

def update_values_counts(values_counts, key):
    if (key not in values_counts.keys()):
        values_counts[key] = 1
    else:
        values_counts[key] += 1

# --------------------------------------------------------------------------------------------------

def strip(value):
    if (value is not None):
        return str(value).strip()
    else:
        return value

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        analyse_separate_opportunities()
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')