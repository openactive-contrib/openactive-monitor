import gzip
import json
# import openactive as oa
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import parser, tz

sys.path.append('../volume-1/common')
from fileutils import get_filename_pairs
from openactive_custom import get_item_kinds, get_item_data_types, get_event_type, get_merged_opportunities
from settings import *

# --------------------------------------------------------------------------------------------------

# Moving away from the former nominatum approach, which creates coords from postcodes.
# Moving towards creating a postcode for each record, from coords if necessary for NSPL matching.
# 4 positions:
# 1) Item has postcode, has coords - use postcode
# 2) Item has postcode, has no coords - use postcode
# 3) Item has no postcode, has coords - find nearest centroid and use that postcode
# 4) Item has no postcode, has no coords - if not online event, use an organiser postcode, otherwise flag as missing

# --------------------------------------------------------------------------------------------------

def analyse_opportunities_per_feed(**kwargs):
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
        raise Exception('At least one filename has been matched to more than one other filename. This should not occur and the filename pairing procedure needs to be investigated.')

    # --------------------------------------------------------------------------------------------------

    # List the items we want to collect for each feed. These column headers need to be specified here in
    # advance of row insertion into the DataFrame:
    separate_analysis = pd.DataFrame(columns=[
        'file_name',
        'file_name_partner',
        'event_type',
        'event_type_partner',
        'feed_name',
        'feed_type',
        'feed_url',
        'dataset_url',
        'discussion_url',
        'license_url',
        'logo_url',
        'publisher_name',
        'status',
        'is_regular',
        'is_merged_with_partner',
        'num_urls',
        'num_items',
        'num_future_items',
        'num_future_week_items',
        'num_matched_superevent_items',
        'num_matched_subevent_items',
        'num_unmatched_superevent_items',
        'num_unmatched_subevent_items',
        'item_kinds_counts',
        'item_data_types_counts',
        'activities_counts',
        'organisers_counts',
        'addresses_counts',
        'latlons_counts',
    ])

    filenames_sampleitems = {}

    # --------------------------------------------------------------------------------------------------

    for filename_pair_idx, filename_pair in enumerate(filename_pairs):

        print(f'Feed pair: {filename_pair_idx+1}/{num_filename_pairs}')
        print(f'Filenames: {filename_pair}')

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

        print(f'Loaded: {[opportunities is not None for opportunities in opportunities_pair]}')

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

        print(f'Item kinds: {item_kinds_counts_pair}')

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

        print(f'Item data types: {item_data_types_counts_pair}')

        # --------------------------------------------------------------------------------------------------

        event_type_pair = []
        for opportunities_idx, opportunities in enumerate(opportunities_pair):
            event_type = None
            if (opportunities is not None):
                try:
                    if (    (item_data_types_counts_pair[opportunities_idx] is not None)
                        and (len(item_data_types_counts_pair[opportunities_idx].keys()) == 1)
                    ):
                        event_type = get_event_type(list(item_data_types_counts_pair[opportunities_idx].keys())[0])
                    else:
                        event_type = get_event_type(opportunities['feed']['type'])
                except Exception as error:
                    print('ERROR:', error)
            event_type_pair.append(event_type)

        print(f'Event types: {event_type_pair}')

        # --------------------------------------------------------------------------------------------------

        num_matched_superevent_items = None
        num_matched_subevent_items = None
        num_unmatched_superevent_items = None
        num_unmatched_subevent_items = None
        is_merged_with_partner = False
        if (    ('superevent' in event_type_pair)
            and ('subevent' in event_type_pair)
        ):
            try:
                num_superevent_items = len(opportunities_pair[event_type_pair.index('superevent')]['items'].keys())
                num_subevent_items = len(opportunities_pair[event_type_pair.index('subevent')]['items'].keys())

                opportunities_pair[event_type_pair.index('superevent')], \
                opportunities_pair[event_type_pair.index('subevent')] = get_merged_opportunities(
                    opportunities_pair[event_type_pair.index('superevent')],
                    opportunities_pair[event_type_pair.index('subevent')]
                )

                num_unmatched_superevent_items = len(opportunities_pair[event_type_pair.index('superevent')]['items'].keys())
                num_unmatched_subevent_items = len([True for item in opportunities_pair[event_type_pair.index('subevent')]['items'].values() if 'superevent_item' not in item.keys()])
                num_matched_superevent_items = num_superevent_items - num_unmatched_superevent_items
                num_matched_subevent_items = num_subevent_items - num_unmatched_subevent_items

                print(f'num_superevent_items: {num_superevent_items}')
                print(f'num_subevent_items: {num_subevent_items}')
                print(f'num_matched_superevent_items: {num_matched_superevent_items}')
                print(f'num_matched_subevent_items: {num_matched_subevent_items}')
                print(f'num_unmatched_superevent_items: {num_unmatched_superevent_items}')
                print(f'num_unmatched_subevent_items: {num_unmatched_subevent_items}')

                if (    (num_matched_superevent_items > 0)
                    and (num_matched_subevent_items == 0)
                ):
                    raise('Matched superevents but no matched subevents ... should not be possible')
                elif (  (num_matched_superevent_items == 0)
                    and (num_matched_subevent_items > 0)
                ):
                    raise('No matched superevents but matched subevents ... should not be possible')
                elif (  (num_matched_superevent_items > 0)
                    and (num_matched_subevent_items > 0)
                ):
                    opportunities_pair[event_type_pair.index('superevent')] = None
                    is_merged_with_partner = True
            except Exception as error:
                print('ERROR:', error)

        print(f'Merged: {is_merged_with_partner}')

        # --------------------------------------------------------------------------------------------------

        print('Running counts and adding entry to dataframe ...')

        for idx in range(2):
            if (opportunities_pair[idx] is not None):
                try:
                    future_item_ids, \
                    future_week_item_ids = get_future_item_ids(opportunities_pair[idx])

                    num_future_items = len(future_item_ids)
                    num_future_week_items = len(future_week_item_ids)

                    if (num_future_week_items > 0):
                        filenames_sampleitems[filename_pair[idx]] = {
                            item_id: opportunities_pair[idx]['items'][item_id]
                            for item_id in random.sample(future_week_item_ids, min(2, num_future_week_items))
                        }

                    separate_analysis.loc[len(separate_analysis)] = {
                        'file_name': filename_pair[idx],
                        'file_name_partner': filename_pair[1-idx],
                        'event_type': event_type_pair[idx],
                        'event_type_partner': event_type_pair[1-idx],
                        'feed_name': opportunities_pair[idx]['feed']['name'],
                        'feed_type': opportunities_pair[idx]['feed']['type'],
                        'feed_url': opportunities_pair[idx]['feed']['url'],
                        'dataset_url': opportunities_pair[idx]['feed']['datasetUrl'],
                        'discussion_url': opportunities_pair[idx]['feed']['discussionUrl'],
                        'license_url': opportunities_pair[idx]['feed']['licenseUrl'],
                        'logo_url': opportunities_pair[idx]['feed']['logoUrl'],
                        'publisher_name': opportunities_pair[idx]['feed']['publisherName'],
                        'status': opportunities_pair[idx]['status'],
                        'is_regular': filename_pair[idx].startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE),
                        'is_merged_with_partner': is_merged_with_partner, # If this field is true, then this feed is the subevent feed and the partner feed is the superevent feed, which will not have an independent entry in this table. If a partner feed was identified but this field is false, this is because one or both of the feed event types were not unambiguously identified or merging was otherwise inhibited.
                        'num_urls': len(opportunities_pair[idx]['urls']),
                        'num_items': len(opportunities_pair[idx]['items'].keys()),
                        'num_future_items': num_future_items,
                        'num_future_week_items': num_future_week_items,
                        'num_matched_superevent_items': num_matched_superevent_items,
                        'num_matched_subevent_items': num_matched_subevent_items,
                        'num_unmatched_superevent_items': num_unmatched_superevent_items,
                        'num_unmatched_subevent_items': num_unmatched_subevent_items,
                        'item_kinds_counts': item_kinds_counts_pair[idx], # TODO: Consider what this means in the context of merging, as we drop the superevent opportunities dictionary
                        'item_data_types_counts': item_data_types_counts_pair[idx], # TODO: Consider what this means in the context of merging, as we drop the superevent opportunities dictionary
                        'activities_counts': get_values_counts(opportunities_pair[idx], ['activity', 'facilityType'], 'prefLabel'), # Note that this returns prefLabels from both 'activity' and 'facilityType' lists, which are somewhat similar in use
                        'organisers_counts': get_values_counts(opportunities_pair[idx], 'organizer', 'name'),
                        'addresses_counts': get_values_counts(opportunities_pair[idx], 'location'),
                        'latlons_counts': get_latlons_counts(opportunities_pair[idx]),
                    }

                except Exception as error:
                    print('ERROR:', error)

        # --------------------------------------------------------------------------------------------------

        print('--------------------------------------------------')

    # --------------------------------------------------------------------------------------------------

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + ANALYSIS_PER_FEED_FILENAME, 'wb') as file_out:
        pickle.dump(separate_analysis, file_out)

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SAMPLE_ITEMS_FILENAME, 'wb') as file_out:
        pickle.dump(filenames_sampleitems, file_out)

# --------------------------------------------------------------------------------------------------

def get_future_item_ids(opportunities):
    future_item_ids = []
    future_week_item_ids = []

    todays_date = datetime.now(tz=tz.UTC).date()
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
            if start_date <= next_weeks_date
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

        if ('startDate' in item['data'].keys()):
            start_datetimes.append(item['data']['startDate'])
        elif ('dateStart' in item['data'].keys()):
            start_datetimes.append(item['data']['dateStart'])
        elif (  ('subEvent' in item['data'].keys())
            and (isinstance(item['data']['subEvent'], list))
        ):
            for subevent in item['data']['subEvent']:
                if (isinstance(subevent, dict)):
                    if ('startDate' in subevent.keys()):
                        start_datetimes.append(subevent['startDate'])
                    elif ('dateStart' in subevent.keys()):
                        start_datetimes.append(subevent['dateStart'])

        for start_datetime in start_datetimes:
            try:
                start_dates.append(parser.parse(start_datetime).astimezone(tz.UTC).date())
            except:
                pass

    return start_dates

# --------------------------------------------------------------------------------------------------

def get_values_counts(opportunities, sought_parent_keys, sought_child_keys=None):
    values_counts = {}

    for item in opportunities['items'].values():
        values = get_values(item, sought_parent_keys, sought_child_keys)
        for value in values:
            if (isinstance(value, dict)):
                value = json.dumps(value)
            elif (not isinstance(value, str)):
                value = str(value)
            value = value.strip()
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
                    if (val is not None):
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