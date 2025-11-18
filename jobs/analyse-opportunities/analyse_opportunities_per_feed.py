import gzip
import json
# import openactive as oa
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import parser, tz
from os import listdir
from os.path import isfile

sys.path.append('../volume-1/common')
from settings import *
from openactive_custom import get_partner_feed_url, get_item_kinds, get_item_data_types, get_event_type, get_merged_opportunities

# --------------------------------------------------------------------------------------------------

# Moving away from the former nominatum approach, which creates coords from postcodes.
# Moving towards creating a postcode for each record, from coords if necessary for NSPL matching.
# 4 positions:
# 1) Item has postcode, has coords - use postcode
# 2) Item has postcode, has no coords - use postcode
# 3) Item has no postcode, has coords - find nearest centroid and use that postcode
# 4) Item has no postcode, has no coords - if not online event, use an organiser postcode, otherwise flag as missing

# --------------------------------------------------------------------------------------------------

# An opportunities filename is formed of a base, a converted URL, a stamp, and a suffix.
# The base is like:
#   'regular-ops' or 'preview-ops'
# The converted URL is like:
#   '--actihire-bookteq-com-api-open-active-facility-uses'
# The stamp is like:
#   '--timeFinish-2024-11-28-02-17-30-651905-UTC--timeTaken-0-374038--numItems-4059--numUrls-39--status-COMPLETE'
# The suffix is like:
#   '.pickle.gzip'
class FilenameStamp:
    # Files of the same filename pre-stamp are later grouped and alphabetically sorted to find the order
    # in which they were made, via the filename stamp, so that earlier files can be deleted. It's important
    # that 'timeFinish' is the first part of the filename stamp for this to work as intended. Other parts
    # can appear in any order. The alternative would be to break down the stamp and seek the 'timeFinish'
    # part when sorting, which is a bit more work and not necessary at the time of writing (2024-06-20):
    parts = [
        'timeFinish',
        'timeTaken',
        'numItems',
        'numUrls',
        'status',
    ]

    # This is important to know outside of this class for when the filename is broken into parts, in order
    # to know how many of the parts form the stamp:
    num_parts = len(parts)

    def __init__(self, t1, t2, num_items, num_urls, status):
        time_delta = t2 - t1
        self.value = ''
        for part in self.parts:
            if (part == 'timeFinish'):
                self.value += f"--{part}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}-UTC"
            elif (part == 'timeTaken'):
                self.value += f"--{part}-{time_delta.seconds}-{time_delta.microseconds}"
            elif (part == 'numItems'):
                self.value += f"--{part}-{num_items}"
            elif (part == 'numUrls'):
                self.value += f"--{part}-{num_urls}"
            elif (part == 'status'):
                self.value += f"--{part}-{status}"

# --------------------------------------------------------------------------------------------------

def get_filenames():
    filenames = sorted([
        i
        for i in listdir(OPPORTUNITIES_RELATIVE_FILEPATH)
        if (    (isfile(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + i))
            and (i.startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE) or i.startswith(PREVIEW_OPPORTUNITIES_FILENAME_BASE))
            and (i.endswith(OPPORTUNITIES_FILENAME_SUFFIX))
            and (i not in OPPORTUNITIES_RELATIVE_FILEPATH_SKIP_FILENAMES)
        )
    ])

    return filenames

# --------------------------------------------------------------------------------------------------

def get_current_filenames(filename_prestamp, filenames):
    current_filenames = sorted([
        filename
        for filename in filenames
        if ('--'.join(filename.split('--')[:-FilenameStamp.num_parts]) == filename_prestamp) # We can't simply use filename.startswith(filename_prestamp), as filename_prestamp might be a substring of a filename with a longer pre-stamp, which would then also be gathered e.g. consider 'facility-uses' and 'facility-uses-events' within the pre-stamp
    ])

    return current_filenames

# --------------------------------------------------------------------------------------------------

def get_filename_prestamps(filenames):
    # Here we split on '--' which is used as the filename stamp delimiter, then remove the number of parts
    # that we know exist in the filename stamp. If we are then left with multiple fragments from the split,
    # that's because there were other instances of '--' in the filename pre-stamp that we don't want to
    # lose, hence we rejoin these fragments with '--' again:

    filename_prestamps = sorted(set([
        '--'.join(filename.split('--')[:-FilenameStamp.num_parts])
        for filename in filenames
    ]))

    return filename_prestamps

# --------------------------------------------------------------------------------------------------

def get_filename_prestamp_pairs(filename_prestamps):
    filename_prestamp_pairs = []
    found_filename_prestamps = []

    for filename_prestamp in filename_prestamps:
        if (filename_prestamp not in found_filename_prestamps):
            partner_filename_prestamp = get_partner_feed_url(filename_prestamp, filename_prestamps)
            filename_prestamp_pairs.append([filename_prestamp, partner_filename_prestamp])
            if (partner_filename_prestamp is not None):
                found_filename_prestamps.append(partner_filename_prestamp)

    return filename_prestamp_pairs

# --------------------------------------------------------------------------------------------------

def get_filename_pairs(filename_prestamp_pairs, filenames):
    filename_pairs = []

    for filename_prestamp_pair in filename_prestamp_pairs:
        filename_pair = []
        for filename_prestamp in filename_prestamp_pair:
            if (filename_prestamp is not None):
                current_filenames = get_current_filenames(filename_prestamp, filenames)
                filename_pair.append(current_filenames[-1])
            else:
                filename_pair.append(None)
        filename_pairs.append(filename_pair)

    return filename_pairs

# --------------------------------------------------------------------------------------------------

def analyse_opportunities_per_feed(**kwargs):
    verbose = kwargs.get('verbose', False)

    # --------------------------------------------------------------------------------------------------

    filename_pairs = []
    try:
        filenames = get_filenames()
        filename_prestamps = get_filename_prestamps(filenames)
        filename_prestamp_pairs = get_filename_prestamp_pairs(filename_prestamps)
        filename_pairs = get_filename_pairs(filename_prestamp_pairs, filenames)
        num_filename_pairs = len(filename_pairs)

        analysis_filenames = [
            filename
            for filename_pair in filename_pairs
            for filename in filename_pair
            if filename is not None
        ]
        unique_analysis_filenames = list(set(analysis_filenames))

        num_analysis_filenames = len(analysis_filenames)
        num_unique_analysis_filenames = len(unique_analysis_filenames)

        if (num_analysis_filenames != num_unique_analysis_filenames):
            raise Exception('At least one filename has been matched to more than one other filename. This should not occur and the filename pairing procedure needs to be investigated.')

        # If something unusual seems to be going on with the filename pairing, then uncomment the following
        # and run to see exactly what is being paired:

        # print('\nfilenames:')
        # for filename in filenames:
        #     print(filename)

        # print('\nfilename_prestamps:')
        # for filename_prestamp in filename_prestamps:
        #     print(filename_prestamp)

        # print('\nfilename_prestamp_pairs:')
        # for filename_prestamp_pair in filename_prestamp_pairs:
        #     print(filename_prestamp_pair[0])
        #     print(filename_prestamp_pair[1])
        #     print()

        # print('filename_pairs:')
        # for filename_pair in filename_pairs:
        #     print(filename_pair[0])
        #     print(filename_pair[1])
        #     print()

        # sys.exit(1)
    except Exception as error:
        raise Exception(error)

    # --------------------------------------------------------------------------------------------------

    # List the items we want to collect for each feed. These column headers need to be specified here in
    # advance of row insertion into the DataFrame:
    df_analysis_data = pd.DataFrame(columns=[
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

                    df_analysis_data.loc[len(df_analysis_data)] = {
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
                        'item_kinds_counts': item_kinds_counts_pair[idx],
                        'item_data_types_counts': item_data_types_counts_pair[idx],
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
        pickle.dump(df_analysis_data, file_out)

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
            if (not isinstance(value, str)):
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
            latlon = ','.join([
                str(round(float(val['latitude']), 6)),
                str(round(float(val['longitude']), 6))
            ])
        elif (isinstance(val, dict)):
            latlon = get_latlon(val)
        if (latlon):
            break

    return latlon