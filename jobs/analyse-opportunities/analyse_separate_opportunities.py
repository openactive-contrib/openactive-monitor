import gzip
import json
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import parser

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_item_kinds, get_item_types, get_event_type, get_superevent_id_v_subevent_ids
from settings import *

# --------------------------------------------------------------------------------------------------

def analyse_separate_opportunities(**kwargs):
    verbose = kwargs.get('verbose', False)

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

    # --------------------------------------------------------------------------------------------------

    # List the items we want to collect for each feed. These column headers need to be specified here in
    # advance of row insertion into the DataFrame:

    separate_analysis = pd.DataFrame(columns=[
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
        'is_merged_with_partner', # BOOL
        'feed_type', # STR
        'item_kinds_counts', # {STR: INT}
        'item_types_counts', # {STR: INT}
        'event_type', # STR

        'num_items', # INT

        'num_partnered_items', # INT
        'num_unpartnered_items', # INT

        'num_future_items', # INT
        'num_future_week_items', # INT

        'organisers_counts', # {STR: INT}
        'activities_counts', # {STR: INT}
        'postcodes_counts', # {STR: INT}
        'latlons_counts', # {STR: INT}
    ])

    filenames_sampleitems = {}

    # --------------------------------------------------------------------------------------------------

    prepare_times = []
    process_times = []

    t1_overall = datetime.now()

    for filename_pair_idx, filename_pair in enumerate(filename_pairs):

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

        # Merging happens if:
        #   we have a pair of feeds ...
        #   the event type (superevent/subevent) for each feed has been unambiguously identified ...
        #   the subevent items refer to existing superevent items.

        # If merging does happen, then superevent items are inserted into related subevent items, and the superevent
        # opportunities object is completely removed from play. We therefore discard any potential counts from
        # superevent items that weren't associated with subevent items.

        # If merging doesn't happen (due to the above conditions not being fulfilled, and usually because of
        # at least one of the feeds having no items), then both opportunities files (if present) go on for
        # independent item content counting. Nothing is discarded. This retention of all such items may not
        # in fact be desirable, and yield superfluous counts of e.g. activities. However, this should be a
        # relative minority. If concerned, then check for cases where we do indeed have both opportunities
        # objects in an unmerged pair, and discard at least the superevent object before running counts.

        premerge_num_items_pair = []
        for opportunity_idx, opportunities in enumerate(opportunities_pair):
            num_items = None
            if (opportunities is not None):
                num_items = len(opportunities['items'].keys())
            premerge_num_items_pair.append(num_items)

        is_merged_with_partner = False
        if (len(superevent_id_v_subevent_ids.keys()) > 0):
            try:
                # Merge superevent items into associated subevent items under a new key called 'superevent_item', and
                # remove the superevent item from its original opportunities dictionary. Both superevent and subevent
                # opportunities dictionaries are therefore changed by this procedure.
                for superevent_id, subevent_ids in superevent_id_v_subevent_ids.items():
                    for subevent_id in subevent_ids:
                        opportunities_pair[event_type_pair.index('subevent')]['items'][subevent_id]['superevent_item'] = opportunities_pair[event_type_pair.index('superevent')]['items'][superevent_id]
                    del(opportunities_pair[event_type_pair.index('superevent')]['items'][superevent_id])

                is_merged_with_partner = True
            except Exception as error:
                print('ERROR:', error)

        print(f'Feeds merged: {is_merged_with_partner}')

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

            try:
                # Note that a future item is one for which there is at least one future start date. A given item could
                # have more than one future start date in certain cases e.g. a superevent item with embedded future
                # subevents, but such items are still classed as one future item. These numbers ultimately contribute
                # to the future opportunities count on the front-end with this style of analysis i.e. we are in effect
                # defining a future opportunity as an item with at least one future start date. A future opportunity
                # could instead be defined as an occurrence of a future start date, in which case the analysis would
                # need to be adjusted to suit. The embedded style to which this applies is not the dominant form of
                # feed type, and so adjusting to accommodate this point may not alter the final numbers by a significant
                # fraction, but there will be some effect.
                future_item_ids, \
                future_week_item_ids = get_future_item_ids(opportunities)

                num_future_items = len(future_item_ids)
                num_future_week_items = len(future_week_item_ids)

                if (num_future_week_items > 0):
                    filenames_sampleitems[filename_pair[opportunity_idx]] = {
                        item_id: opportunities['items'][item_id]
                        for item_id in random.sample(future_week_item_ids, min(2, num_future_week_items))
                    }

                separate_analysis.loc[len(separate_analysis)] = {
                    'feed_id': opportunities['feed']['id'],
                    'partner_feed_id': opportunities_pair[1-opportunity_idx]['feed']['id'] if (opportunities_pair[1-opportunity_idx] is not None) else None,
                    'file_name': filename_pair[opportunity_idx],
                    'dataset_name': opportunities['feed']['name'], # TODO: Change to 'dataset_name' to accommodate changed openactive_custom
                    'publisher_name': opportunities['feed']['publisher_name'],

                    'feed_url': opportunities['feed']['url'],
                    'dataset_url': opportunities['feed']['dataset_url'],
                    'discussion_url': opportunities['feed']['discussion_url'],
                    'license_url': opportunities['feed']['license_url'],
                    'logo_url': opportunities['feed']['logo_url'],

                    'status': opportunities['status'],
                    'is_regular': filename_pair[opportunity_idx].startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE),
                    'is_merged_with_partner': is_merged_with_partner,
                    'feed_type': opportunities['feed']['type'],
                    'item_kinds_counts': item_kinds_counts_pair[opportunity_idx],
                    'item_types_counts': item_types_counts_pair[opportunity_idx],
                    'event_type': event_type_pair[opportunity_idx],

                    'num_items': premerge_num_items_pair[opportunity_idx],

                    'num_partnered_items':
                        num_partnered_superevent_items if (event_type_pair[opportunity_idx] == 'superevent')
                        else num_partnered_subevent_items if (event_type_pair[opportunity_idx] == 'subevent')
                        else None,
                    'num_unpartnered_items':
                        num_unpartnered_superevent_items if (event_type_pair[opportunity_idx] == 'superevent')
                        else num_unpartnered_subevent_items if (event_type_pair[opportunity_idx] == 'subevent')
                        else None,


                    'num_future_items': num_future_items,
                    'num_future_week_items': num_future_week_items,

                    # TODO: The counts obtained here are regardless of whether or not they're for future dates. May want to cater for this depending on how the data are to be displayed and interpreted:
                    'organisers_counts': get_values_counts(opportunities, 'organizer', 'name'),
                    'activities_counts': get_values_counts(opportunities, ['activity', 'facilityType'], 'prefLabel'), # Note that this returns prefLabels from both 'activity' and 'facilityType' lists, which are somewhat similar in use.
                    'postcodes_counts': get_values_counts(opportunities, 'address', 'postalCode'),
                    'latlons_counts': get_latlons_counts(opportunities),
                }

            except Exception as error:
                print('ERROR:', error)

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

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SEPARATE_ANALYSIS_FILENAME, 'wb') as file_out:
        pickle.dump(separate_analysis, file_out)

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SAMPLE_ITEMS_FILENAME, 'wb') as file_out:
        pickle.dump(filenames_sampleitems, file_out)

# --------------------------------------------------------------------------------------------------

def get_future_item_ids(opportunities):
    future_item_ids = []
    future_week_item_ids = []

    todays_date = datetime.now().date()
    next_weeks_date = todays_date + timedelta(days=7)

    for item_id, item in opportunities['items'].items():
        start_dates = get_start_dates(item)
        future_start_dates = [
            start_date
            for start_date in start_dates
            if start_date >= todays_date
        ]
        future_week_start_dates = [
            start_date
            for start_date in future_start_dates
            if start_date < next_weeks_date
        ]
        if (len(future_start_dates) > 0):
            future_item_ids.append(item_id)
        if (len(future_week_start_dates) > 0):
            future_week_item_ids.append(item_id)

    return future_item_ids, future_week_item_ids

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

def get_values_counts(opportunities, sought_parent_keys, sought_child_keys=None):
    values_counts = {}

    for item in opportunities['items'].values():
        values = list(set([
            json.dumps(value).strip() if (isinstance(value, dict))
            else str(value).strip()
            for value in get_values(item, sought_parent_keys, sought_child_keys)
        ]))
        for value in values:
            if (value not in values_counts.keys()):
                values_counts[value] = 1
            else:
                values_counts[value] += 1

    return values_counts

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

def get_latlons_counts(opportunities):
    latlons_counts = {}

    for item in opportunities['items'].values():
        latlon = get_latlon(item)
        if (latlon):
            if (latlon not in latlons_counts.keys()):
                latlons_counts[latlon] = 1
            else:
                latlons_counts[latlon] += 1

    return latlons_counts

# --------------------------------------------------------------------------------------------------

def get_latlon(data):
    latlon = ''

    for key, val in data.items():
        if (    (key == 'geo')
            and (isinstance(val, dict))
            and ('latitude' in val.keys())
            and ('longitude' in val.keys())
        ):
            try:
                latlon = ','.join([
                    str(round(float(val['latitude']), 6)),
                    str(round(float(val['longitude']), 6))
                ])
            except:
                pass
        elif (isinstance(val, dict)):
            latlon = get_latlon(val)
        if (latlon):
            break

    return latlon