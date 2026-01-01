import copy
import geopandas as gpd
import gzip
# import pandas as pd
import pickle
import sys

from datetime import datetime, timedelta
from dateutil import parser

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_item_kinds, get_item_types, get_event_type, get_superevent_id_v_subevent_ids
from settings import *

def analyse_opportunities(**kwargs):
    verbose = kwargs.get('verbose', False)

    # --------------------------------------------------------------------------------------------------

    gdf_regions = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_REGIONS_FILENAME)
    gdf_regions = gdf_regions.to_crs(4326)

    gdf_districts = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_DISTRICTS_FILENAME)
    gdf_districts = gdf_districts.to_crs(4326)

    todays_date = datetime.now().date()
    # todays_date = datetime(2025,12,15).date() # TODO: Remove temporary adjustment:
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
    # (in order to e.g. pre-set container sizes such as lists or dataframes) then we can determine this
    # from the file name stamps as follows, which is much quicker than opening the files to count the
    # items:

    # total_num_items = 0
    # for filename in filenames:
    #     total_num_items += int(filename.split('numItems-')[1].split('--')[0])

    # --------------------------------------------------------------------------------------------------

    # The keys of these dictionaries are essentially column headings, and the values are lists of row entries,
    # one per feed in the case of feeds and one per item in the case of items. Inserting values into such
    # a dictionary is much faster than inserting rows into a dataframe, which makes a lot of difference
    # in the case of items where we are dealing with millions of rows.

    # The comments after each line show the data types. Note that some data types are themselves lists,
    # which occurs for attributes that may have multiple values for the same item e.g. activity, facility.

    # Entries which can't be determined are filled with None rather than the empty version of the type
    # they relate to e.g. an empty string for strings, or zero for integers etc.

    feeds = {
        'feed_id': [], # STR
        'partner_feed_id': [], # STR
        'file_name': [], # STR
        'feed_name': [], # STR
        'publisher_name': [], # STR

        'feed_url': [], # STR
        'dataset_url': [], # STR
        'discussion_url': [], # STR
        'license_url': [], # STR
        'logo_url': [], # STR

        'status': [], # STR
        'is_regular': [], # BOOL
        'feed_type': [], # STR
        'item_kinds_counts': [], # {STR: INT}
        'item_types_counts': [], # {STR: INT}
        'event_type': [], # STR

        'num_items': [], # INT

        'num_partnered_items': [], # INT
        'num_unpartnered_items': [], # INT

        'num_opportunity_start_dates': [], # INT
        'num_future_opportunity_start_dates': [], # INT
        'num_future_week_opportunity_start_dates': [], # INT

        'num_opportunity_items': [], # INT
        'num_future_opportunity_items': [], # INT
        'num_future_week_opportunity_items': [], # INT
    }

    items = {
        # Identifiers
        'unique_item_id': [], # STR
        'feed_id': [], # STR
        'item_id': [], # STR/INT
        'data_id': [], # STR/INT
        'partner_feed_id': [], # STR
        'partner_item_ids': [], # [STR/INT]

        # Who
        'organizer_name': [], # STR

        # What
        'is_regular': [], # BOOL
        'item_name': [], # STR
        'item_kind': [], # STR
        'item_type': [], # STR
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
        'start_date': [], # DATE
        'subevent_start_dates': [], # [DATE]
    }

    # --------------------------------------------------------------------------------------------------

    prepare_times = []
    process_times = []

    t1_overall = datetime.now()

    for filename_pair_idx, filename_pair in enumerate(filename_pairs):

    #    if (filename_pair_idx == 10):
    #        break

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
        print(f'\t\tFeed type: {feed_type_pair[0]}')
        print(f'\t\tItem kinds: {item_kinds_counts_pair[0]}')
        print(f'\t\tItem types: {item_types_counts_pair[0]}')
        print(f'\t\tEvent type: {event_type_pair[0]}')

        print(f'\tFile-2:')
        print(f'\t\tName: {filename_pair[1]}')
        print(f'\t\tLoaded: {opportunities_pair[1] is not None}')
        print(f'\t\tFeed type: {feed_type_pair[1]}')
        print(f'\t\tItem kinds: {item_kinds_counts_pair[1]}')
        print(f'\t\tItem types: {item_types_counts_pair[1]}')
        print(f'\t\tEvent type: {event_type_pair[1]}')

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

            # Feed level data

            num_items = len(opportunities['items'].keys())

            feeds['feed_id'].append(opportunities['feed']['id'])
            if (opportunities_pair[1-opportunity_idx] is not None):
                feeds['partner_feed_id'].append(opportunities_pair[1-opportunity_idx]['feed']['id'])
            else:
                feeds['partner_feed_id'].append(None)
            feeds['file_name'].append(filename_pair[opportunity_idx])
            feeds['feed_name'].append(opportunities['feed']['name'])
            feeds['publisher_name'].append(opportunities['feed']['publisher_name'])

            feeds['feed_url'].append(opportunities['feed']['url'])
            feeds['dataset_url'].append(opportunities['feed']['dataset_url'])
            feeds['discussion_url'].append(opportunities['feed']['discussion_url'])
            feeds['license_url'].append(opportunities['feed']['license_url'])
            feeds['logo_url'].append(opportunities['feed']['logo_url'])

            feeds['status'].append(opportunities['status'])
            feeds['is_regular'].append(filename_pair[opportunity_idx].startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE))
            feeds['feed_type'].append(opportunities['feed']['type'])
            feeds['item_kinds_counts'].append(item_kinds_counts_pair[opportunity_idx])
            feeds['item_types_counts'].append(item_types_counts_pair[opportunity_idx])
            feeds['event_type'].append(event_type_pair[opportunity_idx]),

            feeds['num_items'].append(num_items)

            if (event_type_pair[opportunity_idx] == 'superevent'):
                feeds['num_partnered_items'].append(num_partnered_superevent_items)
            elif (event_type_pair[opportunity_idx] == 'subevent'):
                feeds['num_partnered_items'].append(num_partnered_subevent_items)
            else:
                feeds['num_partnered_items'].append(None)

            if (event_type_pair[opportunity_idx] == 'superevent'):
                feeds['num_unpartnered_items'].append(num_unpartnered_superevent_items)
            elif (event_type_pair[opportunity_idx] == 'subevent'):
                feeds['num_unpartnered_items'].append(num_unpartnered_subevent_items)
            else:
                feeds['num_unpartnered_items'].append(None)

            feeds['num_opportunity_start_dates'].append(0)
            feeds['num_future_opportunity_start_dates'].append(0)
            feeds['num_future_week_opportunity_start_dates'].append(0)

            feeds['num_opportunity_items'].append(0)
            feeds['num_future_opportunity_items'].append(0)
            feeds['num_future_week_opportunity_items'].append(0)

            # --------------------------------------------------------------------------------------------------

            # Item level data

            for item_idx, item in enumerate(opportunities['items'].values()):
                # TODO: Disable this count if running live on GCloud, as the logs there don't do carriage return, so
                # you'll just end up with a long list of numbers if this is enabled:
                if (   ((item_idx + 1) % 10 == 0)
                    or ((item_idx + 1) == num_items)
                ):
                    print(f'\t\tItem: {item_idx + 1}/{num_items}', end=('\n' if ((item_idx + 1) == num_items) else '\r'))

                item_data = item.get('data', {})

                # --------------------------------------------------------------------------------------------------

                # Identifiers

                # An item ID in a given feed should be unique within that feed, but the same item ID may be found in
                # different feeds. We therefore make an absolutely unique item ID here for use in the full set of items
                # from across all feeds, using the combination of feed ID and item ID as it is within the feed. This
                # may be a bit long, but it should be absolutely unique:

                items['unique_item_id'].append('-'.join([feeds['feed_id'][-1], str(item['id']).strip()]))
                items['feed_id'].append(feeds['feed_id'][-1])
                items['item_id'].append(item['id'])
                items['data_id'].append(item_data.get('id', None) or item_data.get('@id', None))
                items['partner_feed_id'].append(feeds['partner_feed_id'][-1])

                partner_item_ids = None
                if (event_type_pair[opportunity_idx] == 'superevent'):
                    if (items['item_id'][-1] in superevent_id_v_subevent_ids.keys()):
                        partner_item_ids = superevent_id_v_subevent_ids[items['item_id'][-1]]
                elif (event_type_pair[opportunity_idx] == 'subevent'):
                    if (items['item_id'][-1] in subevent_id_v_superevent_id.keys()):
                        partner_item_ids = [subevent_id_v_superevent_id[items['item_id'][-1]]]
                items['partner_item_ids'].append(partner_item_ids)

                # --------------------------------------------------------------------------------------------------

                # Who

                # If we get multiple values back (not expected but possible), use the first only i.e. zeroth index:

                organizer_names = get_values(item_data, 'organizer', 'name')
                try:
                    items['organizer_name'].append(strip(organizer_names[0]))
                except:
                    items['organizer_name'].append(None)

                # --------------------------------------------------------------------------------------------------

                # What

                items['is_regular'].append(feeds['is_regular'][-1])
                items['item_name'].append(strip(item_data.get('name', None)))
                items['item_kind'].append(strip(item.get('kind', None)))
                items['item_type'].append(strip(item_data.get('type', None) or item_data.get('@type', None)))
                items['event_type'].append(event_type_pair[opportunity_idx])

                activities = list(set([strip(value) for value in get_values(item_data, 'activity', 'prefLabel')]))
                if (len(activities) > 0):
                    items['activities'].append(activities)
                else:
                    items['activities'].append(None)

                facilities = list(set([strip(value) for value in get_values(item_data, 'facilityType', 'prefLabel')]))
                if (len(facilities) > 0):
                    items['facilities'].append(facilities)
                else:
                    items['facilities'].append(None)

                accessibilities = list(set([strip(value) for value in get_values(item_data, 'accessibilitySupport', 'prefLabel')]))
                if (len(accessibilities) > 0):
                    items['accessibilities'].append(accessibilities)
                else:
                    items['accessibilities'].append(None)

                # --------------------------------------------------------------------------------------------------

                # Where

                # If we get multiple values back (not expected but possible), use the first only i.e. zeroth index:

                locations = get_values(item_data, 'location')
                try:
                    items['postcode'].append(strip(locations[0]['address']['postalCode']))
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

                # Note that this point-by-point region/district mapping is slower than the bulk sjoin approach on GeoPandas
                # dataframe input but much more accurate. The more data given to the bulk sjoin approach, the fewer
                # entries are matched. If there is a future need to use the bulk sjoin approach, it may be possible
                # to improve performance by twiddling gpd settings. Search for gpd.sjoin inaccuracies for info.
                region = None
                district = None
                if (    (items['longitude'][-1] is not None)
                    and (items['latitude'][-1] is not None)
                ):
                    point = None
                    try:
                        point = gpd.points_from_xy(
                            [items['longitude'][-1]],
                            [items['latitude'][-1]]
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

                # --------------------------------------------------------------------------------------------------

                # When

                # Don't use .astimezone(tz.UTC) here - if there is a date but no time then it defaults to midnight,
                # so giving e.g. '2025-06-18' would then be converted to '2025-06-17' by the tz.UTC conversion.

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

                if (len(start_dates) > 0):
                    items['start_date'].append(start_dates[0]) # There should only be one i.e. zeroth index
                else:
                    items['start_date'].append(None)

                if (len(subevent_start_dates) > 0):
                    items['subevent_start_dates'].append(subevent_start_dates)
                else:
                    items['subevent_start_dates'].append(None)

                # Note that a superevent feed with a partnered subevent feed may nonetheless also have some embedded
                # subevent items e.g. https://bookwhen.com/api/openactive/sessionseries. Not sure if this is totally
                # kosher, but it is done.

                # If looking for eventSchedule in further iterations of this code, take care that subEvent with startDate
                # is not also present e.g. https://api.clubspark.uk/odi/public/courses

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
    print(f'\t\t= {round(total_prepare_time / (60 * 60), 2)} hours') # ~4hr52min on M1 8GB MacBook Air
    print(f'\tProcess:')
    print(f'\t\tsum({process_times})')
    print(f'\t\t= {round(total_process_time, 6)} seconds')
    print(f'\t\t= {round(total_process_time / 60, 2)} minutes')
    print(f'\t\t= {round(total_process_time / (60 * 60), 2)} hours') # ~1hr14min on M1 8GB MacBook Air
    print(f'\tPrepare + Process (from summing individual times):')
    print(f'\t\t  {round(total_prepare_process_time, 6)} seconds')
    print(f'\t\t= {round(total_prepare_process_time / 60, 2)} minutes')
    print(f'\t\t= {round(total_prepare_process_time / (60 * 60), 2)} hours') # ~6hr6min on M1 8GB MacBook Air
    print(f'\tPrepare + Process (from overall start and end times):')
    print(f'\t\t  {t2_overall - t1_overall}') # ~6hr6min on M1 8GB MacBook Air
    print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    print('Analysing ...')

    # We have now extracted all values of interest from the raw data, and inserted into a dictionary. Now
    # for some analysis. We could convert the items dictionary to a dataframe at this point and use dataframe
    # operations, but with ~13 million rows this conversion takes ~2hr (at least on an M1 8GB Macbook Air),
    # and, if a saved version is needed, then writing out the dictionary takes ~1hr whereas writing out
    # the dataframe takes ~3hr. So, choosing to stick with the dictionary version and use native Python
    # data types for speed and efficiency.

    # t1 = datetime.now()
    # df_feeds = pd.DataFrame(feeds, columns=feeds.keys())
    # t2 = datetime.now()
    # print(f'Converting dictionary feeds to dataframe feeds: {t2 - t1}') # ??? on M1 8GB MacBook Air

    # t1 = datetime.now()
    # df_items = pd.DataFrame(items, columns=items.keys())
    # t2 = datetime.now()
    # print(f'Converting dictionary items to dataframe items: {t2 - t1}') # ~2.25hr on M1 8GB MacBook Air

    t1 = datetime.now()

    # TODO: Remove this if using total_num_items from filenames above. They should be the same anyway.
    total_num_items = len(items['unique_item_id'])

    total_num_opportunity_start_dates = 0
    total_num_future_opportunity_start_dates = 0
    total_num_future_week_opportunity_start_dates = 0

    total_num_opportunity_items = 0
    total_num_future_opportunity_items = 0
    total_num_future_week_opportunity_items = 0

    organizer_names_counts = {}
    item_kinds_counts = {}
    item_types_counts = {}
    activities_counts = {}
    facilities_counts = {}
    accessibilities_counts = {}
    regions_counts = {}
    districts_counts = {}

    item_kinds_item_types_counts = {}
    item_types_item_kinds_counts = {}

    regions_values_counts = {
        region: {}
        for region in [None] + list(gdf_regions['eer18nm'])
    }
    regions_organizer_names_counts = copy.deepcopy(regions_values_counts)
    regions_item_kinds_counts = copy.deepcopy(regions_values_counts)
    regions_item_types_counts = copy.deepcopy(regions_values_counts)
    regions_activities_counts = copy.deepcopy(regions_values_counts)
    regions_facilities_counts = copy.deepcopy(regions_values_counts)
    regions_accessibilities_counts = copy.deepcopy(regions_values_counts)
    regions_districts_counts = copy.deepcopy(regions_values_counts) # Should be one-to-many

    districts_values_counts = {
        district: {}
        for district in [None] + list(gdf_districts['LAD24NM'])
    }
    districts_organizer_names_counts = copy.deepcopy(districts_values_counts)
    districts_item_kinds_counts = copy.deepcopy(districts_values_counts)
    districts_item_types_counts = copy.deepcopy(districts_values_counts)
    districts_activities_counts = copy.deepcopy(districts_values_counts)
    districts_facilities_counts = copy.deepcopy(districts_values_counts)
    districts_accessibilities_counts = copy.deepcopy(districts_values_counts)
    districts_regions_counts = copy.deepcopy(districts_values_counts) # Should be one-to-one

    partner_id_to_all_item_idx = {}
    for all_item_idx in range(total_num_items):
        if (    (items['event_type'][all_item_idx] == 'superevent')
            and (items['partner_feed_id'][all_item_idx] is not None)
            and (items['partner_item_ids'][all_item_idx] is not None)
        ):
            if (items['feed_id'][all_item_idx] not in partner_id_to_all_item_idx.keys()):
                partner_id_to_all_item_idx \
                    [items['feed_id'][all_item_idx]] = {}
            partner_id_to_all_item_idx \
                [items['feed_id'][all_item_idx]] \
                [items['item_id'][all_item_idx]] = all_item_idx

    feed_id_to_feed_idx = {
        feed_id: feed_idx
        for feed_idx, feed_id in enumerate(feeds['feed_id'])
    }

    for all_item_idx in range(total_num_items):
        # TODO: Disable this count if running live on GCloud, as the logs there don't do carriage return, so
        # you'll just end up with a long list of numbers if this is enabled:
        if (   ((all_item_idx + 1) % 10 == 0)
            or ((all_item_idx + 1) == total_num_items)
        ):
            print(f'\tItem: {all_item_idx + 1}/{total_num_items}', end=('\n' if ((all_item_idx + 1) == total_num_items) else '\r'))

        # --------------------------------------------------------------------------------------------------

        item = {
            key: val[all_item_idx]
            for key, val in items.items()
        }

        # --------------------------------------------------------------------------------------------------

        # If this is a superevent item with subevents via ID and no subevents via embedding, then it will be
        # wholly used and referred to by the subevents via ID, so we skip over it here as it is not something
        # to separately analyse by itself:

        if (    (item['event_type'] == 'superevent')
            and (item['partner_item_ids'] is not None)
            and (item['subevent_start_dates'] is None)
        ):
            continue

        # --------------------------------------------------------------------------------------------------

        # If this is a subevent item with a superevent partner, then modify the subevent content with the contextual
        # superevent info:

        partner_item_all_item_idx = None
        if (    (item['event_type'] == 'subevent')
            and (item['partner_feed_id'] is not None)
            and (item['partner_item_ids'] is not None)
            and (len(item['partner_item_ids']) == 1)
        ):
            partner_item_all_item_idx = \
                partner_id_to_all_item_idx \
                    [item['partner_feed_id']] \
                    [item['partner_item_ids'][0]]

        partner_item = None
        if (partner_item_all_item_idx is not None):
            partner_item = {
                key: val[partner_item_all_item_idx]
                for key, val in items.items()
            }

        if (partner_item is not None):
            # Define a new item kind and item type for these partnered items:
            item['item_kind'] = '_x_'.join([str(item['item_kind']), str(partner_item['item_kind'])])
            item['item_type'] = '_x_'.join([str(item['item_type']), str(partner_item['item_type'])])

            # Merge the subevent and superevent activities, facilities and accessibilities:
            for key in [
                'activities',
                'facilities',
                'accessibilities',
            ]:
                if (    (item[key] is None)
                    and (partner_item[key] is not None)
                ):
                    item[key] = partner_item[key]
                elif (  (item[key] is not None)
                    and (partner_item[key] is not None)
                ):
                    item[key] += partner_item[key]
                    item[key] = list(set(item[key]))

            # Overwrite the subevent location info with that from the superevent if the former are None:
            for key in [
                'organizer_name',
                'postcode',
                'latitude',
                'longitude',
                'region',
                'district',
            ]:
                if (    (item[key] is None)
                    and (partner_item[key] is not None)
                ):
                    item[key] = partner_item[key]

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

        opportunity_start_dates = None
        if (item['subevent_start_dates'] is not None):
            opportunity_start_dates = item['subevent_start_dates']
        elif (  (item['event_type'] == 'subevent')
            and (item['start_date'] is not None)
        ):
            opportunity_start_dates = [item['start_date']]

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

        feed_idx = feed_id_to_feed_idx[item['feed_id']]

        feeds['num_opportunity_start_dates'][feed_idx] += num_opportunity_start_dates
        total_num_opportunity_start_dates += num_opportunity_start_dates
        feeds['num_future_opportunity_start_dates'][feed_idx] += num_future_opportunity_start_dates
        total_num_future_opportunity_start_dates += num_future_opportunity_start_dates
        feeds['num_future_week_opportunity_start_dates'][feed_idx] += num_future_week_opportunity_start_dates
        total_num_future_week_opportunity_start_dates += num_future_week_opportunity_start_dates

        if (num_opportunity_start_dates > 0):
            feeds['num_opportunity_items'][feed_idx] += 1
            total_num_opportunity_items += 1
        if (num_future_opportunity_start_dates > 0):
            feeds['num_future_opportunity_items'][feed_idx] += 1
            total_num_future_opportunity_items += 1
        if (num_future_week_opportunity_start_dates > 0):
            feeds['num_future_week_opportunity_items'][feed_idx] += 1
            total_num_future_week_opportunity_items += 1

        # --------------------------------------------------------------------------------------------------

        # Remember that these counts do not separately include superevent items with subevents via ID and no
        # subevents via embedding, due to skipping over such items above. The information from such items is
        # contained within their partnered subevent items:

        presence = [1, num_opportunity_start_dates, num_future_opportunity_start_dates, num_future_week_opportunity_start_dates]

        update_values_counts(organizer_names_counts, item['organizer_name'], presence)
        update_values_counts(regions_organizer_names_counts[item['region']], item['organizer_name'], presence)
        update_values_counts(districts_organizer_names_counts[item['district']], item['organizer_name'], presence)

        update_values_counts(item_kinds_counts, item['item_kind'], presence)
        update_values_counts(regions_item_kinds_counts[item['region']], item['item_kind'], presence)
        update_values_counts(districts_item_kinds_counts[item['district']], item['item_kind'], presence)

        update_values_counts(item_types_counts, item['item_type'], presence)
        update_values_counts(regions_item_types_counts[item['region']], item['item_type'], presence)
        update_values_counts(districts_item_types_counts[item['district']], item['item_type'], presence)

        update_values_counts(regions_counts, item['region'], presence)
        update_values_counts(districts_regions_counts[item['district']], item['region'], presence)

        update_values_counts(districts_counts, item['district'], presence)
        update_values_counts(regions_districts_counts[item['region']], item['district'], presence)

        if (item['item_kind'] not in item_kinds_item_types_counts.keys()):
            item_kinds_item_types_counts[item['item_kind']] = {}
        if (item['item_type'] not in item_types_item_kinds_counts.keys()):
            item_types_item_kinds_counts[item['item_type']] = {}

        update_values_counts(item_kinds_item_types_counts[item['item_kind']], item['item_type'], presence)
        update_values_counts(item_types_item_kinds_counts[item['item_type']], item['item_kind'], presence)

        if (item['activities'] is not None):
            activities = item['activities']
        else:
            activities = [None]
        for activity in activities:
            update_values_counts(activities_counts, activity, presence)
            update_values_counts(regions_activities_counts[item['region']], activity, presence)
            update_values_counts(districts_activities_counts[item['district']], activity, presence)

        if (item['facilities'] is not None):
            facilities = item['facilities']
        else:
            facilities = [None]
        for facility in facilities:
            update_values_counts(facilities_counts, facility, presence)
            update_values_counts(regions_facilities_counts[item['region']], facility, presence)
            update_values_counts(districts_facilities_counts[item['district']], facility, presence)

        if (item['accessibilities'] is not None):
            accessibilities = item['accessibilities']
        else:
            accessibilities = [None]
        for accessibility in accessibilities:
            update_values_counts(accessibilities_counts, accessibility, presence)
            update_values_counts(regions_accessibilities_counts[item['region']], accessibility, presence)
            update_values_counts(districts_accessibilities_counts[item['district']], accessibility, presence)

    analysis = {
        'organizer_names_counts': organizer_names_counts,
        'item_kinds_counts': item_kinds_counts,
        'item_types_counts': item_types_counts,
        'activities_counts': activities_counts,
        'facilities_counts': facilities_counts,
        'accessibilities_counts': accessibilities_counts,
        'regions_counts': regions_counts,
        'districts_counts': districts_counts,

        'item_kinds_item_types_counts': item_kinds_item_types_counts,
        'item_types_item_kinds_counts': item_types_item_kinds_counts,

        'regions_organizer_names_counts': regions_organizer_names_counts,
        'regions_item_kinds_counts': regions_item_kinds_counts,
        'regions_item_types_counts': regions_item_types_counts,
        'regions_activities_counts': regions_activities_counts,
        'regions_facilities_counts': regions_facilities_counts,
        'regions_accessibilities_counts': regions_accessibilities_counts,
        'regions_districts_counts': regions_districts_counts,

        'districts_organizer_names_counts': districts_organizer_names_counts,
        'districts_item_kinds_counts': districts_item_kinds_counts,
        'districts_item_types_counts': districts_item_types_counts,
        'districts_activities_counts': districts_activities_counts,
        'districts_facilities_counts': districts_facilities_counts,
        'districts_accessibilities_counts': districts_accessibilities_counts,
        'districts_regions_counts': districts_regions_counts,

        'total_num_items': total_num_items,

        'total_num_opportunity_start_dates': total_num_opportunity_start_dates,
        'total_num_future_opportunity_start_dates': total_num_future_opportunity_start_dates,
        'total_num_future_week_opportunity_start_dates': total_num_future_week_opportunity_start_dates,

        'total_num_opportunity_items': total_num_opportunity_items,
        'total_num_future_opportunity_items': total_num_future_opportunity_items,
        'total_num_future_week_opportunity_items': total_num_future_week_opportunity_items,
    }

    t2 = datetime.now()
    print(f'\tTime taken: {t2 - t1}') # ~12min on M1 8GB MacBook Air
    print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    print('Writing out analysis ...')

    # We write out the analysis before writing out items in case the latter bigger operation results in
    # a crash, so at least some useful output is given from this run:

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'analysis.pickle', 'wb') as file_out:
        pickle.dump(analysis, file_out)
    t2 = datetime.now()
    print(f'\tTime taken: {t2 - t1}') # ~4sec (~1.2MB) on M1 8GB MacBook Air

    # --------------------------------------------------------------------------------------------------

    print('Writing out feeds ...')

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'feeds.pickle', 'wb') as file_out:
        pickle.dump(feeds, file_out)
    t2 = datetime.now()
    print(f'\tTime taken: {t2 - t1}') # ~0.5sec (~0.3MB) on M1 8GB MacBook Air

    # --------------------------------------------------------------------------------------------------

    print('Writing out items ...')

    t1 = datetime.now()
    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + 'items.pickle', 'wb') as file_out:
        pickle.dump(items, file_out)
    t2 = datetime.now()
    print(f'\tTime taken: {t2 - t1}') # ~1hr4min (~4.25GB) on M1 8GB MacBook Air

# --------------------------------------------------------------------------------------------------

def strip(value):
    if (type(value) is not None):
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