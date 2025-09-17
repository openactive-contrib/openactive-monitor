import geopandas as gpd
import gzip
import json
# import openactive as oa
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import tz # For timezone handling
from os import getenv, listdir
from os.path import isfile

sys.path.append('../volume-1/common')
import openactive_custom as oa

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. This
# was done for each job as follows (note that the volume and its mount-path were given the same name,
# which didn't have to be so):
#   $ gcloud beta run jobs update <JOB NAME> \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
OPPORTUNITIES_RELATIVE_FILEPATH = getenv('OPPORTUNITIES_RELATIVE_FILEPATH', '../volume-1/data-opportunities')
ANALYSIS_RELATIVE_FILEPATH = getenv('ANALYSIS_RELATIVE_FILEPATH', '../volume-1/data-analysis')

REGULAR_OPPORTUNITIES_FILENAME_BASE = getenv('REGULAR_OPPORTUNITIES_FILENAME_BASE', 'regular-ops')
PREVIEW_OPPORTUNITIES_FILENAME_BASE = getenv('PREVIEW_OPPORTUNITIES_FILENAME_BASE', 'preview-ops')
OPPORTUNITIES_FILENAME_SUFFIX = '.pickle.gzip'
RUNNING_FEEDS_FILENAME = '000-running-feeds.pickle' # Located in OPPORTUNITIES_RELATIVE_FILEPATH
RUNNING_FEED_FILENAME = '000-running-feed.txt' # Located in OPPORTUNITIES_RELATIVE_FILEPATH
CRASHED_FEEDS_FILENAME = '000-crashed-feeds.txt' # Located in OPPORTUNITIES_RELATIVE_FILEPATH
SKIP_FILENAMES = [
    RUNNING_FEEDS_FILENAME,
    RUNNING_FEED_FILENAME,
    CRASHED_FEEDS_FILENAME,
] # Filenames to skip when checking for files in storage
ANALYSIS_PER_FEED_FILENAME = getenv('ANALYSIS_PER_FEED_FILENAME', 'analysis-data.pickle') # Located in ANALYSIS_RELATIVE_FILEPATH TODO: Change to 'analysis-per-feed.pickle' when accommodated elsewhere
SAMPLE_ITEMS_FILENAME = getenv('SAMPLE_ITEMS_FILENAME', 'sample_data.pickle')

print('Environment variables:')
print('OPPORTUNITIES_RELATIVE_FILEPATH:', OPPORTUNITIES_RELATIVE_FILEPATH)
print('ANALYSIS_RELATIVE_FILEPATH:', ANALYSIS_RELATIVE_FILEPATH)
print('REGULAR_OPPORTUNITIES_FILENAME_BASE:', REGULAR_OPPORTUNITIES_FILENAME_BASE)
print('PREVIEW_OPPORTUNITIES_FILENAME_BASE:', PREVIEW_OPPORTUNITIES_FILENAME_BASE)
print('ANALYSIS_PER_FEED_FILENAME:', ANALYSIS_PER_FEED_FILENAME)
print('SAMPLE_ITEMS_FILENAME:', SAMPLE_ITEMS_FILENAME)

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
            and (i not in SKIP_FILENAMES)
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
            partner_filename_prestamp = oa.get_partner_feed_url(filename_prestamp, filename_prestamps)
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

    filenames = get_filenames()
    filename_prestamps = get_filename_prestamps(filenames)
    filename_prestamp_pairs = get_filename_prestamp_pairs(filename_prestamps)
    filename_pairs = get_filename_pairs(filename_prestamp_pairs, filenames)

    # --------------------------------------------------------------------------------------------------

    # List the items we want to collect for each feed. These column headers need to be specified here in
    # advance of row insertion into the DataFrame:
    df_analysis_data = pd.DataFrame(columns=[
        'file_name',
        'file_name_partner',
        'feed_name',
        'feed_type',
        'feed_url',
        'dataset_url',
        'discussion_url',
        'license_url',
        'logo_url',
        'publisher_name',
        'status',
        'event_type',
        'event_type_partner',
        'is_merged_with_partner',
        'is_regular',
        'num_items',
        'num_items_future',
        'num_items_future_week',
        'num_urls',
        'kinds_counts',
        'types_counts',
        'activities_counts',
        'organisers_counts',
        'address_counts',
        'coords_counts',
        'orphaned_superevents',
        'orphaned_subevents',
    ])

    filenames_sampleitems = {}

    # --------------------------------------------------------------------------------------------------

    for filename_pair_idx, filename_pair in enumerate(filename_pairs):

        if (verbose):
            print(filename_pair_idx, filename_pair)

        # --------------------------------------------------------------------------------------------------

        opportunities_pair = []
        for filename in filename_pair:
            opportunities = None
            if (filename is not None):
                try:
                    with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + filename, 'rb') as file_in:
                        opportunities = pickle.load(file_in)
                    if (verbose):
                        print(f'Loaded {filename}')
                except Exception as error:
                    print('ERROR:', error)
            opportunities_pair.append(opportunities)

        # --------------------------------------------------------------------------------------------------

        event_type_pair = []
        for opportunities in opportunities_pair:
            event_type = None
            if (opportunities is not None):
                try:
                    item_data_types = oa.get_item_data_types(opportunities)
                    if (len(item_data_types.keys()) == 1):
                        event_type = oa.get_event_type(list(item_data_types.keys())[0])
                    else:
                        event_type = oa.get_event_type(opportunities.get('feed', {}).get('type'))
                except Exception as error:
                    print('ERROR:', error)
            event_type_pair.append(event_type)

        if (verbose):
            print(f'Event types: {event_type_pair}')

        # --------------------------------------------------------------------------------------------------

        is_merged_with_partner = False
        if (    ('superevent' in event_type_pair)
            and ('subevent' in event_type_pair)
        ):
            try:
                orphaned_superevents, \
                orphaned_subevents, \
                opportunities_pair[event_type_pair.index('subevent')] = oa.get_merged_opportunities(
                    opportunities_pair[event_type_pair.index('subevent')],
                    opportunities_pair[event_type_pair.index('superevent')],
                    **kwargs
                )
                opportunities_pair[event_type_pair.index('superevent')] = None
                is_merged_with_partner = True
            except Exception as error:
                print('ERROR:', error)

        # --------------------------------------------------------------------------------------------------

        for idx in range(2):
            if (opportunities_pair[idx] is not None):
                try:
                    items_future_week, \
                    num_items_future_week, \
                    num_items_future = get_items_future_week(opportunities_pair[idx])

                    df_analysis_data.loc[len(df_analysis_data)] = {
                        'file_name': filename_pair[idx],
                        'file_name_partner': filename_pair[1-idx],
                        'feed_name': opportunities_pair[idx].get('feed', {}).get('name'),
                        'feed_type': opportunities_pair[idx].get('feed', {}).get('type'),
                        'feed_url': opportunities_pair[idx].get('feed', {}).get('url'),
                        'dataset_url': opportunities_pair[idx].get('feed', {}).get('datasetUrl'),
                        'discussion_url': opportunities_pair[idx].get('feed', {}).get('discussionUrl'),
                        'license_url': opportunities_pair[idx].get('feed', {}).get('licenseUrl'),
                        'logo_url': opportunities_pair[idx].get('feed', {}).get('logoUrl'),
                        'publisher_name': opportunities_pair[idx].get('feed', {}).get('publisherName'),
                        'status': opportunities_pair[idx]['status'],
                        'event_type': event_type_pair[idx],
                        'event_type_partner': event_type_pair[idx-1],
                        'is_merged_with_partner': is_merged_with_partner, # If this field is true, then this feed is the subevent feed and the partner feed is the superevent feed, which will not have an independent entry in this table. If a partner feed was identified but this field is false, this is because one or both of the feed event types were not unambiguously identified or merging was inhibited via keyword setting.
                        'is_regular': '000-preview' not in filename_pair[idx],
                        'num_items': len(opportunities_pair[idx]['items'].keys()),
                        'num_items_future': num_items_future,
                        'num_items_future_week': num_items_future_week,
                        'num_urls': len(opportunities_pair[idx]['urls']),
                        'kinds_counts': oa.get_item_kinds(opportunities_pair[idx]),
                        'types_counts': oa.get_item_data_types(opportunities_pair[idx]),
                        'activities_counts': get_values_counts(opportunities_pair[idx], ['activity', 'facilityType'], 'prefLabel'), # Note that this returns prefLabels from both 'activity' and 'facilityType' lists, which are somewhat similar in use
                        'organisers_counts': get_values_counts(opportunities_pair[idx], 'organizer', 'name'),
                        'address_counts': get_values_counts(opportunities_pair[idx], 'location'),
                        'coords_counts': get_coords_counts(opportunities_pair[idx]), #, filenames_with_infostamp_current[-1]), # TEMPORARY: For checking geographically localised high opportunity count spikes
                        'orphaned_superevents': orphaned_superevents,
                        'orphaned_subevents': orphaned_subevents,
                    }

                    if (num_items_future_week > 0):
                        filenames_sampleitems[filename_pair[idx]] = dict(
                            random.sample(
                                list(items_future_week.items()),
                                min(2, num_items_future_week)
                            )
                        )

                except Exception as error:
                    print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + ANALYSIS_PER_FEED_FILENAME, 'wb') as file_out:
        pickle.dump(df_analysis_data, file_out)

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SAMPLE_ITEMS_FILENAME, 'wb') as file_out:
        pickle.dump(filenames_sampleitems, file_out)

# --------------------------------------------------------------------------------------------------

def get_values_counts(opportunities, key_to_find, child_key_to_find=None):
    values_counts = {}

    for item in opportunities['items'].values():
        values = get_value(item, key_to_find, child_key_to_find)
        if (values is None):
            continue
        if (not isinstance(values, list)):
            values = [values]
        for value in values:
            # If it's a dictionary then convert it to a string (e.g. to return a whole dictionary of location info to capture addresses in various formats)
            if (isinstance(value, dict)):
                value = json.dumps(value)
            elif (not isinstance(value, str)):
                continue
            value = value.strip()
            if (value not in values_counts.keys()):
                values_counts[value] = 1
            else:
                values_counts[value] += 1

    return values_counts

# --------------------------------------------------------------------------------------------------

def get_value(data, key_to_find, child_key_to_find=None, continue_to_next_layer=True):
    # This function accepts key_to_find as either a single string or a list of string variants e.g. ['type', '@type'],
    # so if we receive a string then convert to a list for standard internal handling:
    if (isinstance(key_to_find, str)):
        key_to_find = [key_to_find]

    if (isinstance(data, dict)):
        for key, val in data.items():
            if (key in key_to_find):
                if (child_key_to_find is None):
                    return val
                else:
                    # If we are seeking a parent-child key pair and have found the parent key, then child_key_to_find becomes
                    # key_to_find for the next layer search. We also only want to search the immediate next layer and not
                    # beyond, hence the keyword setting here:
                    return get_value(val, child_key_to_find, continue_to_next_layer=False)
            elif (continue_to_next_layer):
                value = get_value(val, key_to_find, child_key_to_find, continue_to_next_layer)
                if (value is not None):
                    return value

    if (isinstance(data, list)):
        values = [get_value(val, key_to_find, child_key_to_find, continue_to_next_layer) for val in data]
        if (any(values)):
            return values

    return None

# --------------------------------------------------------------------------------------------------

NUM_DECIMAL_PLACES_COORDS = 6

# TEMPORARY: For checking geographically localised high opportunity count spikes
# coords_check = {}

def get_coords_counts(opportunities): #, filename=None)
    coords_counts = {}

    # TEMPORARY: For checking geographically localised high opportunity count spikes
    # global coords_check

    for item in opportunities['items'].values():
        item_coords = get_item_coords_from_geo(item)
        if (item_coords):
            item_coords = ','.join([str(item_coord) for item_coord in item_coords])
            if (item_coords not in coords_counts.keys()):
                coords_counts[item_coords] = 1
            else:
                coords_counts[item_coords] += 1
            # TEMPORARY: For checking geographically localised high opportunity count spikes
            # if (    (filename is not None)
            #     and (item_coords == '52.069694,-2.722774')
            # ):
            #     if (filename not in coords_check.keys()):
            #         coords_check[filename] = 1
            #     else:
            #         coords_check[filename] += 1

    return coords_counts

# --------------------------------------------------------------------------------------------------

def get_item_coords_from_geo(data):
    item_coords = []

    for key, val in data.items():
        if (    (key == 'geo')
            and (isinstance(val, dict))
            and ('latitude' in val.keys())
            and ('longitude' in val.keys())
        ):
            item_coords = [
                round(float(val['latitude']), NUM_DECIMAL_PLACES_COORDS),
                round(float(val['longitude']), NUM_DECIMAL_PLACES_COORDS)
            ]
        elif (isinstance(val, dict)):
            item_coords = get_item_coords_from_geo(val)
        if (item_coords):
            break

    return item_coords

# --------------------------------------------------------------------------------------------------

def get_items_future_week(opportunities):
    items_future_week = {}
    num_items_future = 0

    today = datetime.now(tz=tz.UTC).date()

    for item_id, item in opportunities['items'].items():
        item_start_date = get_item_start_date(item)
        if (    (item_start_date is not None)
            and (item_start_date.date() >= today)
        ):
            num_items_future += 1
            if (item_start_date.date() <= today + timedelta(days=7)):
                items_future_week[item_id] = item

    return items_future_week, len(items_future_week.keys()), num_items_future

# --------------------------------------------------------------------------------------------------

def get_item_start_date(item):
    if ('data' not in item.keys()):
        return None

    if ('startDate' in item['data'].keys()):
        return parse_date(item['data']['startDate'])
    elif ('dateStart' in item['data'].keys()):
        return parse_date(item['data']['dateStart'])
    elif (  ('subEvent' in item['data'].keys())
        and (isinstance(item['data']['subEvent'], list))
    ):
        for subevent in item['data']['subEvent']:
            if (    (isinstance(subevent, dict))
                and ('startDate' in subevent.keys())
            ):
                return parse_date(subevent['startDate'])

    return None

# --------------------------------------------------------------------------------------------------

def parse_date(date_string):
    date_formats = [
        '%Y-%m-%dT%H:%M:%SZ', # ISO 8601 format
        '%Y-%m-%d %H:%M:%S', # Common date/time format
        '%Y-%m-%d', # Date only format
        '%Y/%m/%d', # Another common date format
        '%Y-%m-%dT%H:%M:%S.%fZ', # ISO 8601 with milliseconds
        '%Y-%m-%dT%H:%M:%S.%f', # ISO 8601 with milliseconds (no Z)
        '%Y-%m-%dT%H:%M:%S%z', # ISO 8601 with timezone offset
        '%Y-%m-%dT%H:%M:%S%Z', # ISO 8601 with timezone name
    ]

    for date_format in date_formats:
        try:
            parsed_datetime = datetime.strptime(date_string, date_format)
            # If the date string has a timezone, use it:
            if (date_format in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S%Z']):
                return parsed_datetime.astimezone(tz.UTC)
            # Otherwise, assume UTC and set the timezone:
            else:
                return parsed_datetime.replace(tzinfo=tz.UTC)
        except:
            pass

    return None

# --------------------------------------------------------------------------------------------------

def get_df_total_values_counts(df_analysis_data, values_counts, feeds_to_include='all'):
    if (feeds_to_include == 'all'):
        df_total_values_counts = df_analysis_data
    elif (feeds_to_include == 'regular'):
        df_total_values_counts = df_analysis_data.loc[df_analysis_data['is_regular']]
    elif (feeds_to_include == 'preview'):
        df_total_values_counts = df_analysis_data.loc[~df_analysis_data['is_regular']]

    df_total_values_counts = \
        df_total_values_counts[values_counts] \
        .apply(pd.Series) \
        .sum() \
        .apply(int) \
        .sort_values(ascending=False) \
        .reset_index()

    if (values_counts == 'kinds_counts'):
        df_total_values_counts.columns = ['kind', 'count']
    elif (values_counts == 'types_counts'):
        df_total_values_counts.columns = ['type', 'count']
    elif (values_counts == 'activities_counts'):
        df_total_values_counts.columns = ['activity', 'count']
    elif (values_counts == 'organisers_counts'):
        df_total_values_counts.columns = ['organiser', 'count']
    elif (values_counts == 'coords_counts'):
        df_total_values_counts.columns = ['coords', 'count']

    total_num_keys = df_total_values_counts.shape[0]
    total_num_opportunities_with_keys = df_total_values_counts['count'].sum()

    df_total_values_counts['percentage'] = (df_total_values_counts['count'] / total_num_opportunities_with_keys) * 100

    return df_total_values_counts, total_num_keys, total_num_opportunities_with_keys

# --------------------------------------------------------------------------------------------------

def get_gdf_total_locations_counts(df_total_coords_counts, gdf_locations, gdf_locations_name_column):
    # Columns: ['latitude', 'longitude', 'count', 'percentage', 'geometry']
    gdf_total_coords_counts = gpd.GeoDataFrame(
            df_total_coords_counts,
            geometry=gpd.points_from_xy(
                df_total_coords_counts['longitude'],
                df_total_coords_counts['latitude'],
            ),
            crs='epsg:4326', # Set CRS to WGS84
        ) \
        .to_crs(gdf_locations.crs)

    # Columns: [<gdf_locations_name_column>, 'count']
    gdf_total_locations_counts = gpd.GeoDataFrame(
        gpd.sjoin(
            gdf_locations[['geometry', gdf_locations_name_column]],
            gdf_total_coords_counts[['geometry', 'count']],
            how='right',
            predicate='intersects',
        ) \
        .groupby(gdf_locations_name_column)['count'] \
        .sum()
    ) \
    .reset_index()

    # If gdf_locations is 'regions.geojson':
    #     Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count']
    # If gdf_locations is 'lads.geojson':
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count']
    gdf_total_locations_counts = \
        gdf_locations \
        .merge(gdf_total_locations_counts, on=gdf_locations_name_column, how='left') \
        .sort_values(by='count', ascending=False) \
        .fillna(0)

    # If we had any NaN count rows during the last manipulation, then the count column would have been
    # converted to float, so re-type back to int:
    gdf_total_locations_counts['count'] = gdf_total_locations_counts['count'].astype(int)

    total_num_locations = gdf_total_locations_counts.shape[0]
    total_num_opportunities_with_locations = gdf_total_locations_counts['count'].sum()

    # If gdf_locations is 'regions.geojson':
    #     Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
    # If gdf_locations is 'lads.geojson':
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_locations_counts['percentage'] = (gdf_total_locations_counts['count'] / total_num_opportunities_with_locations) * 100

    # print(f'gdf_total_locations_counts ({gdf_locations_name_column}):')
    # print(gdf_total_locations_counts)

    return gdf_total_locations_counts, total_num_locations, total_num_opportunities_with_locations