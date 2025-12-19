import copy
import geopandas as gpd
import gzip
import pandas as pd
import pickle
import sys

from datetime import datetime, timedelta
from dateutil import parser, tz

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_item_kinds, get_item_data_types, get_event_type, get_superevent_id_v_subevent_ids
from settings import *

def analyse_opportunities(**kwargs):
    verbose = kwargs.get('verbose', False)
# xxx
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
        raise Exception('At least one filename has been matched to more than one other filename. This should not occur and the filename pairing procedure needs to be investigated.')

    total_num_items = 0
    for filename in filenames:
        total_num_items += int(filename.split('numItems-')[1].split('--')[0])

    # --------------------------------------------------------------------------------------------------

    # The keys of these dictionaries are essentially column headings, and the values are lists of row entries,
    # one per feed in the case of feeds and one per item in the case of items. Inserting values into such
    # a dictionary is much faster than inserting rows into a dataframe, which makes a lot of difference
    # in the case of items, where we are dealing with millions of rows.

    # The comments after each line show the data types. Note that some data types are themselves lists,
    # which occurs for attributes that may have multiple values for the same item e.g. activity, start date.

    # Entries which can't be determined are filled with None rather than the empty version of the type
    # they relate to e.g. an empty string for strings, or zero for integers etc.

    feeds = {
        'id': [], # STR
        'name': [], # STR
        'type': [], # STR
        'url': [], # STR
        'dataset_url': [], # STR
        'discussion_url': [], # STR
        'license_url': [], # STR
        'logo_url': [], # STR
        'publisher_name': [], # STR

        'file_name': [], # STR
        'file_name_partner': [], # STR

        'event_type': [], # STR
        'event_type_partner': [], # STR

        'status': [], # STR
        'is_regular': [], # BOOL

        'num_items': [], # INT

        'item_kinds_counts': [], # DICT
        'item_data_types_counts': [], # DICT
    }

    items = {
        # Identifiers
        'id': [], # STR
        'feed_id': [], # STR
        'item_id': [], # STR
        'data_id': [], # STR
        # 'parent_feed_id': [], # STR
        # 'parent_matching_id': [], # STR
        'partner_feed_id': [], # STR
        'partner_item_ids': [], # [STR]

        # Who
        'organiser': [], # STR

        # What
        'is_regular': [], # BOOL
        'name': [], # STR
        'kind': [], # STR
        'type': [], # STR
        'event_type': [], # STR
        'activities': [], # [STR]
        'facilities': [], # [STR]
        'accessibilities': [], # [STR]

        # Where
        'postcode': [], # STR
        'latitude': [], # FLT
        'longitude': [], # FLT
        'region': [], # STR
        'district': [], # STR

        # When
        'start_dates': [], # [DATE]
        'num_start_dates': [], # INT
        'num_future_start_dates': [], # INT
        'num_future_week_start_dates': [], # INT

        'alt_start_dates': [], # [DATE]
        'alt_num_start_dates': [], # INT
        'alt_num_future_start_dates': [], # INT
        'alt_num_future_week_start_dates': [], # INT
    }

    # --------------------------------------------------------------------------------------------------

    processing_times = []

    t1 = datetime.now()

    for filename_pair_idx, filename_pair in enumerate(filename_pairs):

        # if (filename_pair_idx == 100):
        #     break

        print(f'File pair: {filename_pair_idx + 1}/{num_filename_pairs}')

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

        item_data_types_counts_pair = []
        for opportunities in opportunities_pair:
            item_data_types_counts = None
            if (opportunities is not None):
                try:
                    item_data_types_counts = get_item_data_types(opportunities)
                except Exception as error:
                    print('ERROR:', error)
            item_data_types_counts_pair.append(item_data_types_counts)

        # --------------------------------------------------------------------------------------------------

        event_type_pair = []
        for opportunity_idx, opportunities in enumerate(opportunities_pair):
            event_type = None
            if (opportunities is not None):
                try:
                    if (    (item_data_types_counts_pair[opportunity_idx] is not None)
                        and (len(item_data_types_counts_pair[opportunity_idx].keys()) == 1)
                    ):
                        event_type = get_event_type(list(item_data_types_counts_pair[opportunity_idx].keys())[0])
                    else:
                        event_type = get_event_type(feed_type_pair[opportunity_idx])
                except Exception as error:
                    print('ERROR:', error)
            event_type_pair.append(event_type)

        is_superevent_subevent_pair = ('superevent' in event_type_pair) and ('subevent' in event_type_pair)

        # --------------------------------------------------------------------------------------------------

        superevent_id_v_subevent_ids = None
        subevent_id_v_superevent_id = None
        if (is_superevent_subevent_pair):
            try:
                superevent_id_v_subevent_ids = get_superevent_id_v_subevent_ids(
                    opportunities_pair[event_type_pair.index('superevent')],
                    opportunities_pair[event_type_pair.index('subevent')]
                )
                subevent_id_v_superevent_id = {}
                for superevent_id, subevent_ids in superevent_id_v_subevent_ids.items():
                    for subevent_id in subevent_ids:
                        subevent_id_v_superevent_id[subevent_id] = superevent_id
            except Exception as error:
                print('ERROR:', error)

        # --------------------------------------------------------------------------------------------------

        print(f'File-1')
        print(f'\tName: {filename_pair[0]}')
        print(f'\tLoaded: {opportunities_pair[0] is not None}')
        print(f'\tFeed type: {feed_type_pair[0]}')
        print(f'\tItem kinds: {item_kinds_counts_pair[0]}')
        print(f'\tItem data types: {item_data_types_counts_pair[0]}')
        print(f'\tEvent type: {event_type_pair[0]}')

        print(f'File-2')
        print(f'\tName: {filename_pair[1]}')
        print(f'\tLoaded: {opportunities_pair[1] is not None}')
        print(f'\tFeed type: {feed_type_pair[1]}')
        print(f'\tItem kinds: {item_kinds_counts_pair[1]}')
        print(f'\tItem data types: {item_data_types_counts_pair[1]}')
        print(f'\tEvent type: {event_type_pair[1]}')

        # --------------------------------------------------------------------------------------------------

        for opportunity_idx, opportunities in enumerate(opportunities_pair):
            if (opportunities is None):
                continue

            print(f'Processing File-{opportunity_idx + 1} ...')
            t1a = datetime.now()

            # --------------------------------------------------------------------------------------------------

            feeds['id'].append(opportunities['feed']['id'])
            feeds['name'].append(opportunities['feed']['name'])
            feeds['type'].append(opportunities['feed']['type'])
            feeds['url'].append(opportunities['feed']['url'])
            feeds['dataset_url'].append(opportunities['feed']['dataset_url'])
            feeds['discussion_url'].append(opportunities['feed']['discussion_url'])
            feeds['license_url'].append(opportunities['feed']['license_url'])
            feeds['logo_url'].append(opportunities['feed']['logo_url'])
            feeds['publisher_name'].append(opportunities['feed']['publisher_name'])

            feeds['file_name'].append(filename_pair[opportunity_idx])
            feeds['file_name_partner'].append(filename_pair[1-opportunity_idx])

            feeds['event_type'].append(event_type_pair[opportunity_idx]),
            feeds['event_type_partner'].append(event_type_pair[1-opportunity_idx]),

            feeds['status'].append(opportunities['status'])
            feeds['is_regular'].append(filename_pair[opportunity_idx].startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE))

            feeds['num_items'].append(len(opportunities['items']))

            feeds['item_kinds_counts'].append(item_kinds_counts_pair[opportunity_idx])
            feeds['item_data_types_counts'].append(item_data_types_counts_pair[opportunity_idx])

            num_items = len(opportunities['items'].keys())

            for item_idx, item in enumerate(opportunities['items'].values()):
                # TODO: Disable this count if running live on GCloud, as the logs there don't do carriage return, so
                # you'll just end up with a long list of numbers if this is enabled:
                if (   ((item_idx + 1) % 10 == 0)
                    or ((item_idx + 1) == num_items)
                ):
                    print(f'\tItem: {item_idx + 1}/{num_items}', end=('\n' if ((item_idx + 1) == num_items) else '\r'))

                item_data = item.get('data', {})

                # --------------------------------------------------------------------------------------------------

                # Identifiers

                # We convert IDs to strings if they aren't already, to ensure consistency of matching. If, for example,
                # an ID was originally an integer, then it could be automatically converted to a float by a dataframe
                # operation at some point, which in that case happens when there is at least one NaN value in the same
                # column which hasn't been set to Int64. If we then try to match the original integer version to the
                # float version, there could be issues. So just standardise to strings at the start and we avoid such
                # potential problems:

                items['feed_id'].append(feeds['id'][-1])
                items['item_id'].append(item['id'])
                items['data_id'].append(strip(item_data.get('id', None) or item_data.get('@id', None)))

                # An item ID in a given feed should be unique within that feed, but the same item ID may be found in
                # different feeds. We therefore make an absolutely unique item ID here for use in the full set of items
                # from across all feeds, using the combination of feed ID and item ID as it is within the feed. This
                # may be a bit long, but it should be absolutely unique:

                items['id'].append('-'.join([items['feed_id'][-1], str(items['item_id'][-1])]))

                # parent_feed_id = None
                # parent_matching_id = None
                # for key in ['superEvent', 'facilityUse']:
                #     if (    (key in item_data.keys())
                #         and (type(item_data[key]) in [str, int])
                #     ):
                #         # If the 'superEvent' or 'facilityUse' key is present as a string or integer, then this is a child
                #         # event (subevent) item, which probably holds true for all other items in this opportunities object,
                #         # with the partner opportunities object then being for parent events (superevents). However, if the
                #         # partner opportunities object is None, due to it not being available or readable, then we won't be
                #         # processing it and won't have a feed_id for it. Note that we may have what a superevent item which
                #         # itself has supersuperevent info under a 'superEvent' key, but that won't be a string or integer
                #         # identifier in that case, but rather a dictionary.
                #         if (opportunities_pair[1-opportunity_idx] is not None):
                #             parent_feed_id = opportunities_pair[1-opportunity_idx]['feed']['id']
                #         parent_matching_id = strip(item_data[key]) # This should be either the exact or the partial parent item ID or data ID. By 'partial' we mean the part after the final slash, if present.
                #         break
                # items['parent_feed_id'].append(parent_feed_id)
                # items['parent_matching_id'].append(parent_matching_id)

                partner_item_ids = None
                if (is_superevent_subevent_pair):
                    items['partner_feed_id'].append(opportunities_pair[1-opportunity_idx]['feed']['id'])
                    if (event_type_pair[opportunity_idx] == 'superevent'):
                        if (    (superevent_id_v_subevent_ids is not None)
                            and (items['id'][-1] in superevent_id_v_subevent_ids.keys())
                        ):
                            partner_item_ids = superevent_id_v_subevent_ids[items['id'][-1]]
                    elif (event_type_pair[opportunity_idx] == 'subevent'):
                        if (    (subevent_id_v_superevent_id is not None)
                            and (items['id'][-1] in subevent_id_v_superevent_id.keys())
                        ):
                            partner_item_ids = [subevent_id_v_superevent_id[items['id'][-1]]]
                items['partner_item_ids'].append(partner_item_ids)

                # --------------------------------------------------------------------------------------------------

                # Who

                organisers = get_values(item_data, 'organizer', 'name') # If we get multiple values back (not expected but possible), use the first only i.e. zeroth index
                try:
                    items['organiser'].append(organisers[0].strip())
                except:
                    items['organiser'].append(None)

                # --------------------------------------------------------------------------------------------------

                # What

                items['is_regular'].append(feeds['is_regular'][-1])
                items['name'].append(strip(item_data.get('name', None)))
                items['kind'].append(strip(item.get('kind', None)))
                items['type'].append(strip(item_data.get('type', None) or item_data.get('@type', None)))
                items['event_type'].append(event_type_pair[opportunity_idx])

                activities = [strip(value) for value in get_values(item_data, 'activity', 'prefLabel')]
                if (len(activities)> 0):
                    items['activities'].append(activities)
                else:
                    items['activities'].append(None)

                facilities = [strip(value) for value in get_values(item_data, 'facilityType', 'prefLabel')]
                if (len(facilities)> 0):
                    items['facilities'].append(facilities)
                else:
                    items['facilities'].append(None)

                accessibilities = [strip(value) for value in get_values(item_data, 'accessibilitySupport', 'prefLabel')]
                if (len(accessibilities)> 0):
                    items['accessibilities'].append(accessibilities)
                else:
                    items['accessibilities'].append(None)

                # --------------------------------------------------------------------------------------------------

                # Where

                locations = get_values(item_data, 'location') # If we get multiple values back (not expected but possible), then below we use the first only i.e. zeroth index
                try:
                    items['postcode'].append(locations[0]['address']['postalCode'].strip())
                except:
                    items['postcode'].append(None)
                try:
                    items['latitude'].append(round(float(locations[0]['geo']['latitude']), 6))
                except:
                    items['latitude'].append(None)
                try:
                    items['longitude'].append(round(float(locations[0]['geo']['longitude']), 6))
                except:
                    items['longitude'].append(None)

                # --------------------------------------------------------------------------------------------------

                # When

                start_dates = []
                start_datetimes = get_values(item_data, 'subEvent', ['startDate', 'dateStart'], continue_to_next_layer=False)
                if (len(start_datetimes) == 0):
                    start_datetimes = get_values(item_data, ['startDate', 'dateStart'], continue_to_next_layer=False)
                for start_datetime in start_datetimes:
                    try:
                        # Don't use .astimezone(tz.UTC) here - if there is a date but no time then it defaults to midnight,
                        # so giving e.g. '2025-06-18' would then be converted to '2025-06-17' by the tz.UTC conversion:
                        start_dates.append(parser.parse(start_datetime).date())
                    except:
                        pass

                if (len(start_dates) > 0):
                    items['start_dates'].append(start_dates)
                else:
                    items['start_dates'].append(None)

                alt_start_dates = get_start_dates(item)
                if (len(alt_start_dates) > 0):
                    items['alt_start_dates'].append(alt_start_dates)
                else:
                    items['alt_start_dates'].append(None)

            # --------------------------------------------------------------------------------------------------

            t2a = datetime.now()
            processing_times.append((t2a - t1a).total_seconds())
            print(f'\tTime taken: {processing_times[-1]} seconds')

        # --------------------------------------------------------------------------------------------------

        print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    t2 = datetime.now()

    sum_processing_times = sum(processing_times)
    print(f'Time taken to process all files:')
    print(f'\tsum({processing_times})')
    print(f'\t= {round(sum_processing_times, 6)} seconds')
    print(f'\t= {round(sum_processing_times / 60, 2)} minutes')
    print(f'Time taken to process all files: {t2 - t1}') # ~3hr20min on M1 8GB MacBook Air

    print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    # We have now extracted all values of interest from the raw data, and inserted into a dictionary. Now
    # for some post-processing and derived values. We could convert the dictionary to a dataframe at this
    # point and use dataframe operations, but with ~13 million rows this conversion takes ~2hr (at least
    # on an M1 8GB Macbook Air), and, if a saved version is needed, then writing out the dictionary takes
    # ~1hr whereas writing out the dataframe takes ~3hr. So, choosing to stick with the dictionary version
    # and use native Python data types for speed and efficiency. Some dataframe equivalent operations are
    # commented out below for reference and potential future use.

    # --------------------------------------------------------------------------------------------------

    # t1 = datetime.now()
    # df_feeds = pd.DataFrame(feeds, columns=feeds.keys())
    # t2 = datetime.now()
    # print(f'Converting dictionary feeds to dataframe feeds: {t2 - t1}') # ??? on M1 8GB MacBook Air

    # t1 = datetime.now()
    # df_items = pd.DataFrame(items, columns=items.keys())
    # t2 = datetime.now()
    # print(f'Converting dictionary items to dataframe items: {t2 - t1}') # ~2.25hr on M1 8GB MacBook Air

    # --------------------------------------------------------------------------------------------------

    gdf_regions = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_REGIONS_FILENAME)
    gdf_regions = gdf_regions.to_crs(4326)

    gdf_districts = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_LADS_FILENAME)
    gdf_districts = gdf_districts.to_crs(4326)

    # --------------------------------------------------------------------------------------------------

    # TODO: Remove this when happy about using total_num_items from filenames, as calculated above
    total_num_items = len(items['id'])

    # Where

    print('Determining locations ...')

    # Dictionary approach

    # The following method is slow (~15min for regions and ~15min for districts when done separately) but
    # accurate, so we use it:

    for all_item_idx in range(total_num_items):
        region = None
        district = None
        if (    (items['longitude'][all_item_idx] is not None)
            and (items['latitude'][all_item_idx] is not None)
        ):
            point = None
            try:
                point = gpd.points_from_xy(
                    [items['longitude'][all_item_idx]],
                    [items['latitude'][all_item_idx]]
                )[0]
            except:
                pass
            if (point is not None):
                try:
                    region = gdf_regions['eer18nm'][list(gdf_regions.contains(point)).index(True)]
                except:
                    pass
                try:
                    district = gdf_districts['LAD24NM'][list(gdf_districts.contains(point)).index(True)]
                except:
                    pass
        items['region'].append(region)
        items['district'].append(district)

    # Dataframe approach

    # The following method is fast (~20sec for regions and ~50sec for districts) but inaccurate, lots of
    # missed matches. May be able to improve by twiddling gpd settings. Search for gpd.sjoin inaccuracies
    # for info. Another reason for not using the dataframe approach.

    # gdf_items = gpd.GeoDataFrame(
    #     # df_items[['longitude', 'latitude']],
    #     geometry=gpd.points_from_xy(df_items['longitude'], df_items['latitude']),
    #     crs='epsg:4326', # Set Coordinate Reference System (CRS) to World Geodetic System 1984 (WGS84). See https://epsg.io/4326.
    # )

    # df_items['region'] = gpd.sjoin(
    #     gdf_regions[['eer18nm', 'geometry']],
    #     gdf_items,
    #     how="right",
    #     predicate="contains"
    # )['eer18nm']
    # # Or:
    # df_items['region'] = gpd.sjoin(
    #     gdf_items,
    #     gdf_regions[['eer18nm', 'geometry']],
    #     how="left",
    #     predicate="within"
    # )['eer18nm']

    # df_items['district'] = gpd.sjoin(
    #     gdf_districts[['LAD24NM', 'geometry']],
    #     gdf_items,
    #     how="right",
    #     predicate="contains"
    # )['LAD24NM']
    # # Or:
    # df_items['district'] = gpd.sjoin(
    #     gdf_items,
    #     gdf_districts[['LAD24NM', 'geometry']],
    #     how="left",
    #     predicate="within"
    # )['LAD24NM']

    # --------------------------------------------------------------------------------------------------

    # When

    print('Determining dates ...')

    # todays_date = datetime.now().date()
    todays_date = datetime(2025,12,15).date() # TODO: Remove temporary adjustment
    next_weeks_date = todays_date + timedelta(days=7)
    print(todays_date) # TODO: Remove when temporary adjustment removed

    # Dictionary approach

    items['num_start_dates'] = [
        len(start_dates)
        if isinstance(start_dates, list)
        else 0
        for start_dates in items['start_dates']
    ]

    items['num_future_start_dates'] = [
        len([
            start_date
            for start_date in start_dates
            if (start_date >= todays_date)
        ])
        if isinstance(start_dates, list)
        else 0
        for start_dates in items['start_dates']
    ]

    items['num_future_week_start_dates'] = [
        len([
            start_date
            for start_date in start_dates
            if (    (start_date >= todays_date)
                and (start_date < next_weeks_date) )
        ])
        if isinstance(start_dates, list)
        else 0
        for start_dates in items['start_dates']
    ]

    items['alt_num_start_dates'] = [
        len(start_dates)
        if isinstance(start_dates, list)
        else 0
        for start_dates in items['alt_start_dates']
    ]

    items['alt_num_future_start_dates'] = [
        len([
            start_date
            for start_date in start_dates
            if (start_date >= todays_date)
        ])
        if isinstance(start_dates, list)
        else 0
        for start_dates in items['alt_start_dates']
    ]

    items['alt_num_future_week_start_dates'] = [
        len([
            start_date
            for start_date in start_dates
            if (    (start_date >= todays_date)
                and (start_date < next_weeks_date) )
        ])
        if isinstance(start_dates, list)
        else 0
        for start_dates in items['alt_start_dates']
    ]

    # Dataframe approach

    # astype('Int64') is needed to allow for columns with mixed integer and None entries, otherwise integers
    # are changed to floats by Pandas.

    # start_date_rows = df_items['start_dates'].notnull()

    # df_items['num_start_dates'] = df_items['start_dates'][start_date_rows].apply(len).astype('Int64')
    # df_items['num_future_start_dates'] = df_items['start_dates'][start_date_rows].apply(lambda start_dates: len([
    #     start_date
    #     for start_date in start_dates
    #     if (start_date >= todays_date)
    # ])).astype('Int64')
    # df_items['num_future_week_start_dates'] = df_items['start_dates'][start_date_rows].apply(lambda start_dates: len([
    #     start_date
    #     for start_date in start_dates
    #     if (    (start_date >= todays_date)
    #         and (start_date < next_weeks_date) )
    # ])).astype('Int64')

    # future_rows = df_items['num_future_start_dates'] > 0
    # future_week_rows = df_items['num_future_week_start_dates'] > 0

    # --------------------------------------------------------------------------------------------------

    # Counts
# xxx

    # print('Opening files ...')
    # t1 = datetime.now()
    # gdf_regions = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_REGIONS_FILENAME)
    # gdf_regions.to_crs(4326)
    # gdf_districts = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_LADS_FILENAME)
    # gdf_districts.to_crs(4326)
    # with gzip.open('/Users/darrentemple/Documents/OpenActive/openactive-monitor/volume-1/data-analysis/dict_items_new.pickle.gzip', 'rb') as file_in:
    #     items = pickle.load(file_in)
    # total_num_items = len(items['id'])
    # t2 = datetime.now()
    # print(t2 - t1)

    print('Running counts ...')

    # Dictionary approach

    organisers_counts = {}
    kinds_counts = {}
    types_counts = {}
    activities_counts = {}
    facilities_counts = {}
    accessibilities_counts = {}
    regions_counts = {}
    districts_counts = {}

    kinds_types_counts = {
        kind: {}
        for kind in set(items['kind'])
    }
    types_kinds_counts = {
        kind: {}
        for kind in set(items['type'])
    }

    regions_values_counts = {
        region: {}
        for region in [None] + list(gdf_regions['eer18nm'])
    }
    regions_organisers_counts = copy.deepcopy(regions_values_counts)
    regions_kinds_counts = copy.deepcopy(regions_values_counts)
    regions_types_counts = copy.deepcopy(regions_values_counts)
    regions_activities_counts = copy.deepcopy(regions_values_counts)
    regions_facilities_counts = copy.deepcopy(regions_values_counts)
    regions_accessibilities_counts = copy.deepcopy(regions_values_counts)
    regions_districts_counts = copy.deepcopy(regions_values_counts) # Should be one-to-many

    districts_values_counts = {
        district: {}
        for district in [None] + list(gdf_districts['LAD24NM'])
    }
    districts_organisers_counts = copy.deepcopy(districts_values_counts)
    districts_kinds_counts = copy.deepcopy(districts_values_counts)
    districts_types_counts = copy.deepcopy(districts_values_counts)
    districts_activities_counts = copy.deepcopy(districts_values_counts)
    districts_facilities_counts = copy.deepcopy(districts_values_counts)
    districts_accessibilities_counts = copy.deepcopy(districts_values_counts)
    districts_regions_counts = copy.deepcopy(districts_values_counts) # Should be one-to-one

    for all_item_idx in range(total_num_items):
        presence = [1, items['num_start_dates'][all_item_idx], items['num_future_start_dates'][all_item_idx], items['num_future_week_start_dates'][all_item_idx]]

        update_values_counts(organisers_counts, items['organiser'][all_item_idx], presence)
        update_values_counts(regions_organisers_counts[items['region'][all_item_idx]], items['organiser'][all_item_idx], presence)
        update_values_counts(districts_organisers_counts[items['district'][all_item_idx]], items['organiser'][all_item_idx], presence)

        update_values_counts(kinds_counts, items['kind'][all_item_idx], presence)
        update_values_counts(regions_kinds_counts[items['region'][all_item_idx]], items['kind'][all_item_idx], presence)
        update_values_counts(districts_kinds_counts[items['district'][all_item_idx]], items['kind'][all_item_idx], presence)

        update_values_counts(types_counts, items['type'][all_item_idx], presence)
        update_values_counts(regions_types_counts[items['region'][all_item_idx]], items['type'][all_item_idx], presence)
        update_values_counts(districts_types_counts[items['district'][all_item_idx]], items['type'][all_item_idx], presence)

        update_values_counts(regions_counts, items['region'][all_item_idx], presence)
        update_values_counts(districts_regions_counts[items['district'][all_item_idx]], items['region'][all_item_idx], presence)

        update_values_counts(districts_counts, items['district'][all_item_idx], presence)
        update_values_counts(regions_districts_counts[items['region'][all_item_idx]], items['district'][all_item_idx], presence)

        update_values_counts(kinds_types_counts[items['kind'][all_item_idx]], items['type'][all_item_idx], presence)
        update_values_counts(types_kinds_counts[items['type'][all_item_idx]], items['kind'][all_item_idx], presence)

        if (items['activities'][all_item_idx] is not None):
            activities = items['activities'][all_item_idx]
        else:
            activities = [None]
        for activity in activities:
            update_values_counts(activities_counts, activity, presence)
            update_values_counts(regions_activities_counts[items['region'][all_item_idx]], activity, presence)
            update_values_counts(districts_activities_counts[items['district'][all_item_idx]], activity, presence)

        if (items['facilities'][all_item_idx] is not None):
            facilities = items['facilities'][all_item_idx]
        else:
            facilities = [None]
        for facility in facilities:
            update_values_counts(facilities_counts, facility, presence)
            update_values_counts(regions_facilities_counts[items['region'][all_item_idx]], facility, presence)
            update_values_counts(districts_facilities_counts[items['district'][all_item_idx]], facility, presence)

        if (items['accessibilities'][all_item_idx] is not None):
            accessibilities = items['accessibilities'][all_item_idx]
        else:
            accessibilities = [None]
        for accessibility in accessibilities:
            update_values_counts(accessibilities_counts, accessibility, presence)
            update_values_counts(regions_accessibilities_counts[items['region'][all_item_idx]], accessibility, presence)
            update_values_counts(districts_accessibilities_counts[items['district'][all_item_idx]], accessibility, presence)

    total_num_start_dates = sum(items['num_start_dates'])
    total_num_future_start_dates = sum(items['num_future_start_dates'])
    total_num_future_week_start_dates = sum(items['num_future_week_start_dates'])

    total_alt_num_start_dates = sum(items['alt_num_start_dates'])
    total_alt_num_future_start_dates = sum(items['alt_num_future_start_dates'])
    total_alt_num_future_week_start_dates = sum(items['alt_num_future_week_start_dates'])

    total_num_future_items = sum([1 for x in items['num_future_start_dates'] if x > 0]) # Measure of future by old analysis (once merging done)
    total_num_future_week_items = sum([1 for x in items['num_future_week_start_dates'] if x > 0]) # Measure of future week by old analysis (once merging done)

    total_alt_num_future_items = sum([1 for x in items['alt_num_future_start_dates'] if x > 0])
    total_alt_num_future_week_items = sum([1 for x in items['alt_num_future_week_start_dates'] if x > 0])

    analysis = {
        'organisers_counts': organisers_counts,
        'kinds_counts': kinds_counts,
        'types_counts': types_counts,
        'activities_counts': activities_counts,
        'facilities_counts': facilities_counts,
        'accessibilities_counts': accessibilities_counts,
        'regions_counts': regions_counts,
        'districts_counts': districts_counts,

        'kinds_types_counts': kinds_types_counts,
        'types_kinds_counts': types_kinds_counts,

        'regions_organisers_counts': regions_organisers_counts,
        'regions_kinds_counts': regions_kinds_counts,
        'regions_types_counts': regions_types_counts,
        'regions_activities_counts': regions_activities_counts,
        'regions_facilities_counts': regions_facilities_counts,
        'regions_accessibilities_counts': regions_accessibilities_counts,
        'regions_districts_counts': regions_districts_counts,

        'districts_organisers_counts': districts_organisers_counts,
        'districts_kinds_counts': districts_kinds_counts,
        'districts_types_counts': districts_types_counts,
        'districts_activities_counts': districts_activities_counts,
        'districts_facilities_counts': districts_facilities_counts,
        'districts_accessibilities_counts': districts_accessibilities_counts,
        'districts_regions_counts': districts_regions_counts,

        'total_num_start_dates': total_num_start_dates,
        'total_num_future_start_dates': total_num_future_start_dates,
        'total_num_future_week_start_dates': total_num_future_week_start_dates,

            'total_alt_num_start_dates': total_alt_num_start_dates,
            'total_alt_num_future_start_dates': total_alt_num_future_start_dates,
            'total_alt_num_future_week_start_dates': total_alt_num_future_week_start_dates,

        'total_num_items': total_num_items,
        'total_num_future_items': total_num_future_items,
        'total_num_future_week_items': total_num_future_week_items,

            'total_alt_num_future_items': total_alt_num_future_items,
            'total_alt_num_future_week_items': total_alt_num_future_week_items,
    }

    # Dataframe approach

    # Note that kind, type, region and district fields have one value per processed item, and as such the
    # dataframe value_counts() method can be directly applied as indicated below. However, the activities,
    # facilities and accessibilities fields are always lists, even if they have only one element, and as
    # such the value_counts() method will not give what we really want in cases with more than one element
    # per list. Some thought will need to be given to this if and when the dataframe approach is decided
    # to be used.

    # organisers_counts = df_items['organiser'].value_counts()
    # kinds_counts = df_items['kind'].value_counts()
    # types_counts = df_items['type'].value_counts()
    # activities_counts =
    # facilities_counts =
    # accessibilities_counts =
    # regions_counts = df_items['region'].value_counts()
    # districts_counts = df_items['district'].value_counts()

    # future_organisers_counts = df_items['organiser'][future_rows].value_counts()
    # future_kinds_counts = df_items['kind'][future_rows].value_counts()
    # future_types_counts = df_items['type'][future_rows].value_counts()
    # future_activities_counts =
    # future_facilities_counts =
    # future_accessibilities_counts =
    # future_regions_counts = df_items['region'][future_rows].value_counts()
    # future_districts_counts = df_items['district'][future_rows].value_counts()

    # future_week_organisers_counts = df_items['organiser'][future_week_rows].value_counts()
    # future_week_kinds_counts = df_items['kind'][future_week_rows].value_counts()
    # future_week_types_counts = df_items['type'][future_week_rows].value_counts()
    # future_week_activities_counts =
    # future_week_facilities_counts =
    # future_week_accessibilities_counts =
    # future_week_regions_counts = df_items['region'][future_week_rows].value_counts()
    # future_week_districts_counts = df_items['district'][future_week_rows].value_counts()

    # regions_organisers_counts = df_items[['region', 'organiser']].groupby('region').value_counts()
    # regions_kinds_counts = df_items[['region', 'kind']].groupby('region').value_counts()
    # regions_types_counts = df_items[['region', 'type']].groupby('region').value_counts()
    # regions_activities_counts =
    # regions_facilities_counts =
    # regions_accessibilities_counts =

    # future_regions_organisers_counts = df_items[['region', 'organiser']][future_rows].groupby('region').value_counts()
    # future_regions_kinds_counts = df_items[['region', 'kind']][future_rows].groupby('region').value_counts()
    # future_regions_types_counts = df_items[['region', 'type']][future_rows].groupby('region').value_counts()
    # future_regions_activities_counts =
    # future_regions_facilities_counts =
    # future_regions_accessibilities_counts =

    # future_week_regions_organisers_counts = df_items[['region', 'organiser']][future_week_rows].groupby('region').value_counts()
    # future_week_regions_kinds_counts = df_items[['region', 'kind']][future_week_rows].groupby('region').value_counts()
    # future_week_regions_types_counts = df_items[['region', 'type']][future_week_rows].groupby('region').value_counts()
    # future_week_regions_activities_counts =
    # future_week_regions_facilities_counts =
    # future_week_regions_accessibilities_counts =

    # districts_organisers_counts = df_items[['district', 'organiser']].groupby('district').value_counts()
    # districts_kinds_counts = df_items[['district', 'kind']].groupby('district').value_counts()
    # districts_types_counts = df_items[['district', 'type']].groupby('district').value_counts()
    # districts_activities_counts =
    # districts_facilities_counts =
    # districts_accessibilities_counts =

    # future_districts_organisers_counts = df_items[['district', 'organiser']][future_rows].groupby('district').value_counts()
    # future_districts_kinds_counts = df_items[['district', 'kind']][future_rows].groupby('district').value_counts()
    # future_districts_types_counts = df_items[['district', 'type']][future_rows].groupby('district').value_counts()
    # future_districts_activities_counts =
    # future_districts_facilities_counts =
    # future_districts_accessibilities_counts =

    # future_week_districts_organisers_counts = df_items[['district', 'organiser']][future_week_rows].groupby('district').value_counts()
    # future_week_districts_kinds_counts = df_items[['district', 'kind']][future_week_rows].groupby('district').value_counts()
    # future_week_districts_types_counts = df_items[['district', 'type']][future_week_rows].groupby('district').value_counts()
    # future_week_districts_activities_counts =
    # future_week_districts_facilities_counts =
    # future_week_districts_accessibilities_counts =

    # total_num_start_dates = df_items['num_start_dates'].sum()
    # total_num_future_start_dates = df_items['num_future_start_dates'].sum()
    # total_num_future_week_start_dates = df_items['num_future_week_start_dates'].sum()

    # --------------------------------------------------------------------------------------------------

    # Write out analysis (do this before writing out items in case that bigger operation results in a crash)

    print('Writing out analysis ...')

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'analysis.pickle', 'wb') as file_out:
        pickle.dump(analysis, file_out)
    t2 = datetime.now()
    print(f'Writing zipped dictionary analysis: {t2 - t1}') # ~??? on M1 8GB MacBook Air

    # --------------------------------------------------------------------------------------------------

    # Write out feeds (different styles for testing purposes)

    # print('Writing out feeds ...')

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'dict_feeds.pickle', 'wb') as file_out:
        pickle.dump(feeds, file_out)
    t2 = datetime.now()
    print(f'Writing dictionary feeds: {t2 - t1}') # ~0.4sec (~0.3MB) on M1 8GB MacBook Air

    # t1 = datetime.now()
    # with gzip.open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'dict_feeds.pickle.gzip', 'wb') as file_out:
    #     pickle.dump(feeds, file_out)
    # t2 = datetime.now()
    # print(f'Writing zipped dictionary feeds: {t2 - t1}') # ~??? on M1 8GB MacBook Air

    # t1 = datetime.now()
    # with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'df_feeds.pickle', 'wb') as file_out:
    #     pickle.dump(df_feeds, file_out)
    # t2 = datetime.now()
    # print(f'Writing dataframe feeds: {t2 - t1}') # ~??? on M1 8GB MacBook Air

    # t1 = datetime.now()
    # with gzip.open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'df_feeds.pickle.gzip', 'wb') as file_out:
    #     pickle.dump(df_feeds, file_out)
    # t2 = datetime.now()
    # print(f'Writing zipped dataframe feeds: {t2 - t1}') # ~??? on M1 8GB MacBook Air

    # --------------------------------------------------------------------------------------------------

    # Write out items (different styles for testing purposes)

    # print('Writing out items ...')

    # The following write times and file sizes were for tests involving storage of:
    #   id
    #   data_id
    #   feed_id
    #   parent_feed_id
    #   parent_matching_id
    #   kind
    #   type
    #   organiser
    #   name
    #   activities
    #   facilities
    #   region (from address content, not calculated from latlon)
    #   postcode
    #   latitude
    #   longitude
    #   start_dates

    # Also note that read times for these large files is ~10-40min, at least on M1 8GB MacBook Air

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'dict_items.pickle', 'wb') as file_out:
        pickle.dump(items, file_out)
    t2 = datetime.now()
    print(f'Writing dictionary items: {t2 - t1}') # ~1hr10min (~3.940GB) on M1 8GB MacBook Air

    # t1 = datetime.now()
    # with gzip.open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'dict_items.pickle.gzip', 'wb') as file_out:
    #     pickle.dump(items, file_out)
    # t2 = datetime.now()
    # print(f'Writing zipped dictionary items: {t2 - t1}') # ~1hr15min (~320MB) on M1 8GB MacBook Air

    # t1 = datetime.now()
    # with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'df_items.pickle', 'wb') as file_out:
    #     pickle.dump(df_items, file_out)
    # t2 = datetime.now()
    # print(f'Writing dataframe items: {t2 - t1}') # ~2hr50min (~4.250GB) on M1 8GB MacBook Air

    # t1 = datetime.now()
    # with gzip.open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'df_items.pickle.gzip', 'wb') as file_out:
    #     pickle.dump(df_items, file_out)
    # t2 = datetime.now()
    # print(f'Writing zipped dataframe items: {t2 - t1}') # ~2hr50min (~320MB) on M1 8GB MacBook Air

# --------------------------------------------------------------------------------------------------

def strip(value):
    if (type(value) != None):
        return str(value).strip()
    else:
        return value

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

def get_start_dates(item):
    start_dates = []

    if ('data' in item.keys()):
        start_datetimes = []

        if (    ('subEvent' in item['data'].keys())
            and (isinstance(item['data']['subEvent'], list))
        ):
            for subevent in item['data']['subEvent']:
                if (isinstance(subevent, dict)):
                    if ('startDate' in subevent.keys()):
                        start_datetimes.append(subevent['startDate'])
                    elif ('dateStart' in subevent.keys()):
                        start_datetimes.append(subevent['dateStart'])

        if (len(start_datetimes) == 0):
            if ('startDate' in item['data'].keys()):
                start_datetimes.append(item['data']['startDate'])
            elif ('dateStart' in item['data'].keys()):
                start_datetimes.append(item['data']['dateStart'])

        for start_datetime in start_datetimes:
            try:
                # Don't use .astimezone(tz.UTC) here - if there is a date but no time then it defaults to midnight,
                # so giving e.g. '2025-06-18' would then be converted to '2025-06-17' by the tz.UTC conversion:
                start_dates.append(parser.parse(start_datetime).date())
            except:
                pass

    return start_dates

# --------------------------------------------------------------------------------------------------

def update_values_counts(values_counts, key, presence):
    if (key not in values_counts.keys()):
        values_counts[key] = presence
    else:
        values_counts[key] = [x + y for x, y in zip(values_counts[key], presence)]

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        analyse_opportunities()
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')