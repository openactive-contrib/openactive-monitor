import geopandas as gpd
import gzip
# import openactive as oa
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import tz # For timezone handling
from numpy import nan
from os import getenv, listdir
from os.path import isfile
from time import sleep
import json

sys.path.append('../volume-1/common')
import openactive_custom as oa

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'analyse-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update analyse-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_FEEDS = getenv('RELATIVE_FILEPATH_FEEDS', '../volume-1/data-feeds')
RELATIVE_FILEPATH_OPPORTUNITIES = getenv('RELATIVE_FILEPATH_OPPORTUNITIES', '../volume-1/data-opportunities')
RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')

FILENAME_FEEDS = getenv('FILENAME_FEEDS', 'feeds.pickle') # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_PREVIEW = getenv('FILENAME_FEEDS_PREVIEW', 'feeds-preview.pickle') # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_SEEN = '000-feeds-seen.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAME_FEEDS_CRASHED = '000-feeds-crashed.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAMES_SKIP = [FILENAME_FEEDS_SEEN, FILENAME_FEEDS_CRASHED] # Filenames to skip when checking for opportunity files in RELATIVE_FILEPATH_OPPORTUNITIES
SUFFIX_FILENAME_OPPORTUNITIES = 'pickle.gzip'
LEN_SUFFIX_FILENAME_OPPORTUNITIES = len(SUFFIX_FILENAME_OPPORTUNITIES)
FILENAME_ANALYSIS_DATA = getenv('FILENAME_ANALYSIS_DATA', 'analysis-data.pickle')
FILENAME_SAMPLE_DATA = getenv('FILENAME_SAMPLE_DATA', 'sample_data.pickle')
FILENAME_ANALYSIS = getenv('FILENAME_ANALYSIS', 'analysis.pickle')
FILENAME_REGIONS = getenv('FILENAME_REGIONS', 'regions.geojson')
FILENAME_LADS = getenv('FILENAME_LADS', 'lads.geojson')
FILENAME_SE_SPORT_AND_DISCIPLINE = getenv('FILENAME_SE_SPORT_AND_DISCIPLINE', 'SE-sport-and-discipline.csv')
FILENAME_OA_SE_MAPPING = getenv('FILENAME_OA_SE_MAPPING', 'OA-SE-mapping.csv')
VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False
VERBOSE = True

print('Environment variables:')
print('RELATIVE_FILEPATH_FEEDS:', RELATIVE_FILEPATH_FEEDS)
print('RELATIVE_FILEPATH_OPPORTUNITIES:', RELATIVE_FILEPATH_OPPORTUNITIES)
print('RELATIVE_FILEPATH_ANALYSIS:', RELATIVE_FILEPATH_ANALYSIS)
print('FILENAME_FEEDS:', FILENAME_FEEDS)
print('FILENAME_FEEDS_PREVIEW:', FILENAME_FEEDS_PREVIEW)
print('FILENAME_ANALYSIS_DATA:', FILENAME_ANALYSIS_DATA)
print('FILENAME_ANALYSIS:', FILENAME_ANALYSIS)
print('FILENAME_REGIONS:', FILENAME_REGIONS)
print('FILENAME_LADS:', FILENAME_LADS)
print('FILENAME_SE_SPORT_AND_DISCIPLINE:', FILENAME_SE_SPORT_AND_DISCIPLINE)
print('FILENAME_OA_SE_MAPPING:', FILENAME_OA_SE_MAPPING)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

#Moving away from this nominatum approach, which creates coords from postcodes
#Moving towards creating a postcode for each record, from coords if necessary for nspl matching
#4 positions:
#1) Item has postcode and coords - use postcode
#2) Item has postcode no coords - use postcode
#3) Item has coords no postcode - find nearest centroid and use that postcode
#4) Item has no postcode no coords - if not online event, use an organiser postcode, otherwise flag as missing

# --------------------------------------------------------------------------------------------------

class Infostamp:
    # Files of the same filename prefix are later grouped and alphabetically sorted to determine the order
    # in which they were made, and to then delete earlier ones. It's therefore important that 'timeFinish'
    # is the first part of the filename infostamp suffix. Other parts can appear in any order. The alternative
    # would be to break down the infostamp and seek the 'timeFinish' part when sorting, which is a bit
    # more work and not necessary at the time of writing (2024-06-20):
    parts = [
        'timeFinish',
        'timeTaken',
        'numItems',
        'numUrls',
        'status',
    ]

    # This is important to know outside of this class for when the filename is broken into parts, in order
    # to know how many of the parts form the infostamp suffix:
    num_parts = len(parts)

    def __init__(self, opportunities, t1, t2):
        time_delta = t2 - t1
        self.value = ''
        for part in Infostamp.parts:
            if (part == 'numItems'):
                self.value += f"--{part}-{len(opportunities['items'].keys())}"
            elif (part == 'numUrls'):
                self.value += f"--{part}-{len(opportunities['urls'])}"
            elif (part == 'status'):
                self.value += f"--{part}-{opportunities['status']}"
            elif (part == 'timeFinish'):
                self.value += f"--{part}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}-UTC"
            elif (part == 'timeTaken'):
                self.value += f"--{part}-{time_delta.seconds}-{time_delta.microseconds}"

# --------------------------------------------------------------------------------------------------

def get_filenames():
    filenames_with_infostamp = sorted([
        i[:-LEN_SUFFIX_FILENAME_OPPORTUNITIES]
        for i in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)
        if (    (isfile(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + i))
            and (i not in FILENAMES_SKIP)
            and (len(i) > LEN_SUFFIX_FILENAME_OPPORTUNITIES)
            and (i[-LEN_SUFFIX_FILENAME_OPPORTUNITIES:] == SUFFIX_FILENAME_OPPORTUNITIES)
        )
    ])

    filenames_without_infostamp = sorted(set([
        '--'.join(i.split('--')[:-Infostamp.num_parts])
        for i in filenames_with_infostamp
    ]))

    return filenames_with_infostamp, filenames_without_infostamp

# --------------------------------------------------------------------------------------------------

def get_pairs_filenames_without_infostamp(filenames_without_infostamp):
    pairs_filenames_without_infostamp = []
    found_filenames_without_infostamp = []

    for filename_without_infostamp in filenames_without_infostamp:
        if (filename_without_infostamp not in found_filenames_without_infostamp):
            partner_filename_without_infostamp = oa.get_partner_feed_url(filename_without_infostamp, filenames_without_infostamp)
            pair_filenames_without_infostamp = [filename_without_infostamp, partner_filename_without_infostamp]
            pairs_filenames_without_infostamp.append(pair_filenames_without_infostamp)
            if (partner_filename_without_infostamp is not None):
                found_filenames_without_infostamp.append(partner_filename_without_infostamp)

    return pairs_filenames_without_infostamp

# --------------------------------------------------------------------------------------------------

def get_pairs_filenames_with_infostamp(pairs_filenames_without_infostamp, filenames_with_infostamp):
    pairs_filenames_with_infostamp = []

    for pair_filenames_without_infostamp in pairs_filenames_without_infostamp:
        pair_filenames_with_infostamp = []
        for filename_without_infostamp in pair_filenames_without_infostamp:
            filename_with_infostamp = None
            if (filename_without_infostamp is not None):
                filename_with_infostamp = sorted([
                    filename_with_infostamp
                    for filename_with_infostamp in filenames_with_infostamp
                    if ('--'.join(filename_with_infostamp.split('--')[:-Infostamp.num_parts]) == filename_without_infostamp)
                ])[-1]
            pair_filenames_with_infostamp.append(filename_with_infostamp)
        pairs_filenames_with_infostamp.append(pair_filenames_with_infostamp)

    return pairs_filenames_with_infostamp

# --------------------------------------------------------------------------------------------------

def analyse_opportunities(pairs_filenames_with_infostamp, **kwargs):
    verbose = kwargs.get('verbose', False)

    #List the items we want to collect for each feed
    df_analysis_data = pd.DataFrame(columns=[
        'file_name',
        'file_name_partner',
        'feed_name',
        'feed_type',
        'feed_url',
        'dataset_url',
        'discussion_url',
        'license_url',
        'logo_Url',
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
        'coords_counts',
        'address_counts',
        'orphaned_superevents',
        'orphaned_subevents',
    ])

    filenames_sampleitems = {}

    # --------------------------------------------------------------------------------------------------

    for idx_pair_filenames_with_infostamp, pair_filenames_with_infostamp in enumerate(pairs_filenames_with_infostamp):

        if (verbose):
            print(idx_pair_filenames_with_infostamp, pair_filenames_with_infostamp)

        # --------------------------------------------------------------------------------------------------

        pair_opportunities_in = []
        for filename_with_infostamp in pair_filenames_with_infostamp:
            opportunities_in = None
            if (filename_with_infostamp is not None):
                try:
                    relative_filepath_opportunities_in = RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filename_with_infostamp + SUFFIX_FILENAME_OPPORTUNITIES
                    with gzip.open(relative_filepath_opportunities_in, 'rb') as file_in:
                        opportunities_in = pickle.load(file_in)
                    if (verbose):
                        print(f"Loaded {filename_with_infostamp}")
                except Exception as error:
                    print('ERROR:', error)
            pair_opportunities_in.append(opportunities_in)
            
        # --------------------------------------------------------------------------------------------------
        # Using event type from the items rather than the feed name causing issues if no items
        # Using event type from feed type if more than one type returned from items or type missing (e.g. no items)
        pair_event_types = []
        for opportunities_in in pair_opportunities_in:
            event_type = None
            if (opportunities_in is not None):
                try:
                    item_data_types = oa.get_item_data_types(opportunities_in)
                    if (len(item_data_types.keys()) == 1):
                        event_type = oa.get_event_type(list(item_data_types.keys())[0])
                    else:
                        event_type = oa.get_event_type(opportunities_in.get('feed', {}).get('type'))
                except Exception as error:
                    print('ERROR:', error)
            pair_event_types.append(event_type)
        if (verbose):
            print(f"Event types: {pair_event_types}")

        # --------------------------------------------------------------------------------------------------

        is_merged_with_partner = False
        if (('superevent' in pair_event_types)
            and ('subevent' in pair_event_types)
        ):
            try:
                orphaned_superevents, \
                orphaned_subevents, \
                pair_opportunities_in[pair_event_types.index('subevent')] = oa.get_merged_opportunities(
                    pair_opportunities_in[pair_event_types.index('subevent')],
                    pair_opportunities_in[pair_event_types.index('superevent')],
                    **kwargs
                )
                pair_opportunities_in[pair_event_types.index('superevent')] = None
                is_merged_with_partner = True
            except Exception as error:
                print('ERROR:', error)

        # --------------------------------------------------------------------------------------------------

        for idx in range(2):
            if (pair_opportunities_in[idx] is not None):
                try:
                    items_future_week, \
                    num_items_future_week, \
                    num_items_future = get_items_future_week(pair_opportunities_in[idx])

                    df_analysis_data.loc[len(df_analysis_data)] = {
                        'file_name': pair_filenames_with_infostamp[idx],
                        'file_name_partner': pair_filenames_with_infostamp[1-idx],
                        'feed_name': pair_opportunities_in[idx].get('feed', {}).get('name'),
                        'feed_type': pair_opportunities_in[idx].get('feed', {}).get('type'),
                        'feed_url': pair_opportunities_in[idx].get('feed', {}).get('url'),
                        'dataset_url': pair_opportunities_in[idx].get('feed', {}).get('datasetUrl'),
                        'discussion_url': pair_opportunities_in[idx].get('feed', {}).get('discussionUrl'),
                        'license_url': pair_opportunities_in[idx].get('feed', {}).get('licenseUrl'),
                        'logo_url': pair_opportunities_in[idx].get('feed', {}).get('logoUrl'),
                        'publisher_name': pair_opportunities_in[idx].get('feed', {}).get('publisherName'),
                        'status': pair_opportunities_in[idx]['status'],
                        'event_type': pair_event_types[idx],
                        'event_type_partner': pair_event_types[idx-1],
                        'is_merged_with_partner': is_merged_with_partner, # If this field is true, then this feed is the subevent feed and the partner feed is the superevent feed, which will not have an independent entry in this table. If a partner feed was identified but this field is false, this is because one or both of the feed event types were not unambiguously identified or merging was inhibited via keyword setting.
                        'is_regular': '000-preview' not in pair_filenames_with_infostamp[idx],
                        'num_items': len(pair_opportunities_in[idx]['items'].keys()),
                        'num_items_future': num_items_future,
                        'num_items_future_week': num_items_future_week,
                        'num_urls': len(pair_opportunities_in[idx]['urls']),
                        'kinds_counts': oa.get_item_kinds(pair_opportunities_in[idx]),
                        'types_counts': oa.get_item_data_types(pair_opportunities_in[idx]),
                        'activities_counts': get_values_counts(pair_opportunities_in[idx], ['activity', 'facilityType'], 'prefLabel'), # Note that this returns prefLabels from both 'activity' and 'facilityType' lists, which are somewhat similar in use
                        'organisers_counts': get_values_counts(pair_opportunities_in[idx], 'organizer', 'name'),
                        'coords_counts': get_coords_counts(pair_opportunities_in[idx]), #, filenames_with_infostamp_current[-1]), # TEMPORARY: For checking geographically localised high opportunity count spikes
                        'address_counts': get_values_counts(pair_opportunities_in[idx], 'location'),
                        'orphaned_superevents': orphaned_superevents,
                        'orphaned_subevents': orphaned_subevents,
                    }

                    if (num_items_future_week > 0):
                        filenames_sampleitems[pair_filenames_with_infostamp[idx]] = dict(
                            random.sample(
                                list(items_future_week.items()),
                                min(2, num_items_future_week)
                            )
                        )

                except Exception as error:
                    print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS_DATA, 'wb') as file_out:
        pickle.dump(df_analysis_data, file_out)
    
    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_SAMPLE_DATA, 'wb') as file_out:
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
            if (not isinstance(value, str)):
                # If it's a dictionary, convert it to a string (e.g. to return whole json dict of location to capture addresses in various formats)
                if isinstance(value, dict):
                    value = json.dumps(value)
                else:
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

# --------------------------------------------------------------------------------------------------