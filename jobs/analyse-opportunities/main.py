import geopandas as gpd
import gzip
import lzma
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import tz # For timezone handling
from geopy.geocoders import Nominatim
from numpy import nan
from openactive import get_item_kinds, get_item_data_types
from os import getenv, listdir
from os.path import isfile
from time import sleep

# --------------------------------------------------------------------------------------------------

# TODO: Consider using a non-infinite timeout here. See:
# https://gis.stackexchange.com/questions/173569/avoid-time-out-error-nominatim-geopy-openstreetmap
# https://geopy.readthedocs.io/en/latest/index.html#nominatim
geolocator = Nominatim(user_agent='OpenActive Monitor', timeout=None)

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'analyse-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update analyse-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_OPPORTUNITIES = getenv('RELATIVE_FILEPATH_OPPORTUNITIES', '../volume-1/data-opportunities')
RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')

FILENAME_FEEDS_SEEN = '000-feeds-seen.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAME_FEEDS_CRASHED = '000-feeds-crashed.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAMES_SKIP = [FILENAME_FEEDS_SEEN, FILENAME_FEEDS_CRASHED] # Filenames to skip when checking for opportunity files in RELATIVE_FILEPATH_OPPORTUNITIES
FORMAT_FILE_OPPORTUNITIES = 'pickle'
COMPRESSION_FILE_OPPORTUNITIES = getenv('COMPRESSION_FILE_OPPORTUNITIES', 'gzip').lower() # 'none' / 'gzip' / 'xz'
SUFFIX_FILENAME_OPPORTUNITIES = '.' + FORMAT_FILE_OPPORTUNITIES + (('.' + COMPRESSION_FILE_OPPORTUNITIES) if (COMPRESSION_FILE_OPPORTUNITIES != 'none') else '')
LEN_SUFFIX_FILENAME_OPPORTUNITIES = len(SUFFIX_FILENAME_OPPORTUNITIES)
FILENAME_ANALYSIS_DATA = getenv('FILENAME_ANALYSIS_DATA', 'analysis-data.pickle')
FILENAME_ANALYSIS = getenv('FILENAME_ANALYSIS', 'analysis.pickle')
FILENAME_REGIONS = getenv('FILENAME_REGIONS', 'regions.geojson')
FILENAME_LADS = getenv('FILENAME_LADS', 'lads.geojson')
FILENAME_SE_SPORT_AND_DISCIPLINE = getenv('FILENAME_SE_SPORT_AND_DISCIPLINE', 'SE-sport-and-discipline.csv')
FILENAME_OA_SE_MAPPING = getenv('FILENAME_OA_SE_MAPPING', 'OA-SE-mapping.csv')

print('Environment variables:')
print('RELATIVE_FILEPATH_OPPORTUNITIES:', RELATIVE_FILEPATH_OPPORTUNITIES)
print('RELATIVE_FILEPATH_ANALYSIS:', RELATIVE_FILEPATH_ANALYSIS)
print('COMPRESSION_FILE_OPPORTUNITIES:', COMPRESSION_FILE_OPPORTUNITIES)
print('FILENAME_ANALYSIS_DATA:', FILENAME_ANALYSIS_DATA)
print('FILENAME_ANALYSIS:', FILENAME_ANALYSIS)
print('FILENAME_REGIONS:', FILENAME_REGIONS)
print('FILENAME_LADS:', FILENAME_LADS)
print('FILENAME_SE_SPORT_AND_DISCIPLINE:', FILENAME_SE_SPORT_AND_DISCIPLINE)
print('FILENAME_OA_SE_MAPPING:', FILENAME_OA_SE_MAPPING)

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

filenames_with_infostamp = None
filenames_without_infostamp = None
def get_filenames():
    global filenames_with_infostamp
    global filenames_without_infostamp
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

# --------------------------------------------------------------------------------------------------

def analyse_opportunities():
    df_analysis_data = pd.DataFrame(columns=[
        'file_name',
        'feed_name',
        'feed_type',
        'feed_url',
        'dataset_url',
        'discussion_url',
        'license_url',
        'publisher_name',
        'status',
        'is_regular',
        'num_items',
        'num_items_future',
        'num_items_future_week',
        'num_urls',
        'item_kinds_counts',
        'item_data_types_counts',
        'activities_counts',
        'coords_counts',
    ])

    filenames_sampleitems = {}

    # --------------------------------------------------------------------------------------------------

    for idx_filename_without_infostamp_current, filename_without_infostamp_current in enumerate(filenames_without_infostamp):
        try:
            filenames_with_infostamp_current = sorted([
                filename_with_infostamp
                for filename_with_infostamp in filenames_with_infostamp
                if ('--'.join(filename_with_infostamp.split('--')[:-Infostamp.num_parts]) == filename_without_infostamp_current)
            ])

            print(idx_filename_without_infostamp_current, filenames_with_infostamp_current[-1])

            opportunities_in = None
            relative_filepath_opportunities_in = RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + SUFFIX_FILENAME_OPPORTUNITIES
            if (COMPRESSION_FILE_OPPORTUNITIES == 'none'):
                with open(relative_filepath_opportunities_in, 'rb') as file_in:
                    opportunities_in = pickle.load(file_in)
            elif (COMPRESSION_FILE_OPPORTUNITIES == 'gzip'):
                with gzip.open(relative_filepath_opportunities_in, 'rb') as file_in:
                    opportunities_in = pickle.load(file_in)
            elif (COMPRESSION_FILE_OPPORTUNITIES == 'xz'):
                with lzma.open(relative_filepath_opportunities_in, 'rb') as file_in:
                    opportunities_in = pickle.load(file_in)

            if (opportunities_in is not None):
                items_future_week, \
                num_items_future_week, \
                num_items_future = get_items_future_week(opportunities_in)

                df_analysis_data.loc[len(df_analysis_data)] = {
                    'file_name': filenames_with_infostamp_current[-1],
                    'feed_name': opportunities_in.get('feed', {}).get('name'),
                    'feed_type': opportunities_in.get('feed', {}).get('type'),
                    'feed_url': opportunities_in.get('feed', {}).get('url'),
                    'dataset_url': opportunities_in.get('feed', {}).get('datasetUrl'),
                    'discussion_url': opportunities_in.get('feed', {}).get('discussionUrl'),
                    'license_url': opportunities_in.get('feed', {}).get('licenseUrl'),
                    'publisher_name': opportunities_in.get('feed', {}).get('publisherName'),
                    'status': opportunities_in['status'],
                    'is_regular': '000-preview' not in filenames_with_infostamp_current[-1],
                    'num_items': len(opportunities_in['items'].keys()),
                    'num_items_future': num_items_future,
                    'num_items_future_week': num_items_future_week,
                    'num_urls': len(opportunities_in['urls']),
                    'item_kinds_counts': get_item_kinds(opportunities_in),
                    'item_data_types_counts': get_item_data_types(opportunities_in),
                    'activities_counts': get_activities_counts(opportunities_in),
                    'coords_counts': get_coords_counts(opportunities_in), #, filenames_with_infostamp_current[-1]), # TEMPORARY: For checking geographically localised high opportunity count spikes
                }

                if (num_items_future_week > 0):
                    filenames_sampleitems[filenames_with_infostamp_current[-1]] = dict(
                        random.sample(
                            list(items_future_week.items()),
                            min(2, num_items_future_week)
                        )
                    )

        except Exception as error:
            print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    # with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS_DATA, 'rb') as file_in:
    #     df_analysis_data = pickle.load(file_in)

    # For the 'Overview' tab

    num_publishers_regular = df_analysis_data['publisher_name'].loc[df_analysis_data['is_regular']].replace('', nan).nunique()
    num_publishers_preview = df_analysis_data['publisher_name'].loc[~df_analysis_data['is_regular']].replace('', nan).nunique()
    num_publishers = df_analysis_data['publisher_name'].replace('', nan).nunique()

    num_datasets_regular = df_analysis_data['dataset_url'].loc[df_analysis_data['is_regular']].replace('', nan).nunique()
    num_datasets_preview = df_analysis_data['dataset_url'].loc[~df_analysis_data['is_regular']].replace('', nan).nunique()
    num_datasets = df_analysis_data['dataset_url'].replace('', nan).nunique()

    num_feeds_regular = df_analysis_data.loc[df_analysis_data['is_regular']].shape[0]
    num_feeds_preview = df_analysis_data.loc[~df_analysis_data['is_regular']].shape[0]
    num_feeds = num_feeds_regular + num_feeds_preview

    total_num_opportunities_regular = df_analysis_data['num_items'].loc[df_analysis_data['is_regular']].sum()
    total_num_opportunities_preview = df_analysis_data['num_items'].loc[~df_analysis_data['is_regular']].sum()
    total_num_opportunities = total_num_opportunities_regular + total_num_opportunities_preview

    # --------------------------------------------------------------------------------------------------

    # For the 'This week' tab

    total_num_opportunities_future_regular = df_analysis_data['num_items_future'].loc[df_analysis_data['is_regular']].sum()
    total_num_opportunities_future_preview = df_analysis_data['num_items_future'].loc[~df_analysis_data['is_regular']].sum()
    total_num_opportunities_future = total_num_opportunities_future_regular + total_num_opportunities_future_preview

    total_num_opportunities_future_week_regular = df_analysis_data['num_items_future_week'].loc[df_analysis_data['is_regular']].sum()
    total_num_opportunities_future_week_preview = df_analysis_data['num_items_future_week'].loc[~df_analysis_data['is_regular']].sum()
    total_num_opportunities_future_week = total_num_opportunities_future_week_regular + total_num_opportunities_future_week_preview

    # --------------------------------------------------------------------------------------------------

    # For the 'Activities' tab

    # Columns: ['activity', 'count', 'percentage']
    df_total_activities_counts, \
    total_num_activities, \
    total_num_opportunities_with_activities = get_df_total_keys_counts(df_analysis_data, 'activities_counts', feeds_to_include='all')

    # --------------------------------------------------------------------------------------------------

    # For the 'Locations' tab

    # Columns: ['coords', 'count', 'percentage']
    df_total_coords_counts, \
    total_num_coords, \
    total_num_opportunities_with_coords = get_df_total_keys_counts(df_analysis_data, 'coords_counts', feeds_to_include='all')
    # Columns: ['coords', 'count', 'percentage', 'latitude', 'longitude']
    df_total_coords_counts[['latitude', 'longitude']] = pd.DataFrame(df_total_coords_counts['coords'].apply(lambda coords: coords.split(',')).tolist())
    # Columns: ['latitude', 'longitude', 'count', 'percentage']
    df_total_coords_counts = df_total_coords_counts[['latitude', 'longitude', 'count', 'percentage']]

    # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry']
    gdf_regions = gpd.read_file(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_REGIONS)
    # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry']
    gdf_lads = gpd.read_file(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_LADS)

    # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_regions_counts, \
    total_num_regions, \
    total_num_opportunities_with_regions = get_gdf_total_locations_counts(df_total_coords_counts, gdf_regions, 'eer18nm')

    # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_lads_counts, \
    total_num_lads, \
    total_num_opportunities_with_lads = get_gdf_total_locations_counts(df_total_coords_counts, gdf_lads, 'LAD24NM')

    # --------------------------------------------------------------------------------------------------

    # For the 'KPIs' tab

    # Columns: ['sport', 'discipline', 'sport_and_discipline']
    df_se_sport_and_discipline = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_SE_SPORT_AND_DISCIPLINE)
    # Columns: ['activity', 'sport_and_discipline']
    df_oa_se_mapping = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_OA_SE_MAPPING)

    # Automatically update the mapping file if confident in the handling of incoming activity labels i.e.
    # if the names have been stripped of junk and formatted in a compatible way, otherwise we'll potentially
    # get unmatched repetition e.g. 'kettlebells' may have a match, but a new entry 'kettlebells\r\n' will
    # not. Currently commenting this out as it could pollute the mapping file if not done right, instead
    # relying on the dataframe merge below with no matches resulting in NaN, which can be changed to 'No Match'
    # here in code. This means that the code may produce mistakes on-the-fly depending on the full chain
    # of data handling choices, but at least they won't be hard-wired into the mapping file:

    # df_oa_se_mapping_additions = \
    #     df_total_activities_counts[~df_total_activities_counts['activity'].isin(df_oa_se_mapping['activity'])] \
    #     .copy() \
    #     .drop(columns=['count']) \
    #     .assign(sport_and_discipline='No Match') \
    #     .reset_index(drop=True)

    # df_oa_se_mapping = \
    #     pd.concat([df_oa_se_mapping, df_oa_se_mapping_additions]) \
    #     .sort_values(by='activity') \
    #     .reset_index(drop=True)

    # df_oa_se_mapping.to_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_OA_SE_MAPPING)

    # Columns: ['activity', 'count', 'sport_and_discipline']
    df_total_sad_counts = pd.merge(
        df_total_activities_counts \
        .drop(columns=['percentage']) \
        .assign(activity=lambda x: x['activity'].str.strip()),
        df_oa_se_mapping,
        how='left',
    )

    # Pull out non-matching activities before they are changed to 'No Match', as then they will be indistinguishable
    # from the existing 'No Match' entries in the mapping file:
    df_total_sad_counts_na = df_total_sad_counts.loc[df_total_sad_counts['sport_and_discipline'].isna()]
    df_total_sad_counts_na.to_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'unmatched_activities.csv', index=False)

    df_total_sad_counts['sport_and_discipline'].fillna('No Match', inplace=True)
    df_total_sad_counts_matched = df_total_sad_counts.loc[df_total_sad_counts['sport_and_discipline'] != 'No Match']
    df_total_sad_counts_unmatched = df_total_sad_counts.loc[df_total_sad_counts['sport_and_discipline'] == 'No Match']

    # Note that after this operation we have MultiIndex columns, where each element of a tuple corresponds
    # to a different header row:
    # Columns: [('sport_and_discipline', ''), ('activity', '<lambda>'), ('count', 'count'), ('count', 'sum')]
    df_total_sad_counts_matched = \
        df_total_sad_counts_matched \
        .groupby('sport_and_discipline') \
        .agg({
            'activity': lambda x: '; '.join(list(x)), # Don't join activity labels with commas as the labels may use commas
            'count': ['count', 'sum'], # This is the 'count' column with the 'count' and 'sum' functions applied to it separately, producing two new sub-columns, and hence the MultiIndex output
        }) \
        .sort_values(by=('count', 'sum'), ascending=False) \
        .reset_index()

    # Compact to single index columns for simplicity, also because Streamlit can't display MultiIndex columns:
    # Columns: ['sport_and_discipline', 'activity', 'count_activities', 'count_opportunities']
    df_total_sad_counts_matched.columns = [
        'sport_and_discipline',
        'activity',
        'count_activities',
        'count_opportunities',
    ]

    # Columns: ['sport_and_discipline', 'activity', 'count']
    df_total_sad_counts_unmatched = df_total_sad_counts_unmatched[['sport_and_discipline', 'activity', 'count']]
    # Rename columns for consistency with df_total_sad_counts_matched, even though there's only one count here:
    # Columns: ['sport_and_discipline', 'activity', 'count_opportunities']
    df_total_sad_counts_unmatched.columns = [
        'sport_and_discipline',
        'activity',
        'count_opportunities',
    ]

    total_num_activities_with_sad = df_total_sad_counts_matched['count_activities'].sum()
    total_num_activities_without_sad = df_total_sad_counts_unmatched.shape[0]
    total_num_opportunities_with_sad = df_total_sad_counts_matched['count_opportunities'].sum()
    total_num_opportunities_without_sad = df_total_sad_counts_unmatched['count_opportunities'].sum()

    # Columns: ['sport_and_discipline', 'activity', 'count_activities', 'count_opportunities', 'percentage_activities', 'percentage_opportunities']
    df_total_sad_counts_matched['percentage_activities'] = (df_total_sad_counts_matched['count_activities'] / total_num_activities_with_sad) * 100
    df_total_sad_counts_matched['percentage_opportunities'] = (df_total_sad_counts_matched['count_opportunities'] / total_num_opportunities_with_sad) * 100

    # Columns: ['sport_and_discipline', 'activity', 'count_opportunities', 'percentage_opportunities']
    df_total_sad_counts_unmatched['percentage_opportunities'] = (df_total_sad_counts_unmatched['count_opportunities'] / total_num_opportunities_without_sad) * 100

    num_sad = df_se_sport_and_discipline['sport_and_discipline'].count()
    num_sad_matched = df_total_sad_counts_matched['sport_and_discipline'].count()
    num_sad_unmatched = num_sad - num_sad_matched
    percentage_sad_matched = (num_sad_matched / num_sad) * 100
    percentage_sad_unmatched = 100 - percentage_sad_matched

    df_se_sport_and_discipline_unmatched = df_se_sport_and_discipline.loc[
        ~df_se_sport_and_discipline['sport_and_discipline'] \
        .isin(df_total_sad_counts_matched['sport_and_discipline'])
    ]

    # --------------------------------------------------------------------------------------------------

    analysis = {
        'num_publishers_regular': num_publishers_regular, # 2024-08-23 Not currently used in the dashboard
        'num_publishers_preview': num_publishers_preview, # 2024-08-23 Not currently used in the dashboard
        'num_publishers': num_publishers,

        'num_datasets_regular': num_datasets_regular, # 2024-08-23 Not currently used in the dashboard
        'num_datasets_preview': num_datasets_preview, # 2024-08-23 Not currently used in the dashboard
        'num_datasets': num_datasets,

        'num_feeds_regular': num_feeds_regular, # 2024-08-23 Not currently used in the dashboard
        'num_feeds_preview': num_feeds_preview,
        'num_feeds': num_feeds,

        'total_num_opportunities_regular': total_num_opportunities_regular, # 2024-08-23 Not currently used in the dashboard
        'total_num_opportunities_preview': total_num_opportunities_preview,
        'total_num_opportunities': total_num_opportunities,

        'total_num_opportunities_future_regular': total_num_opportunities_future_regular, # 2024-08-23 Not currently used in the dashboard
        'total_num_opportunities_future_preview': total_num_opportunities_future_preview, # 2024-08-23 Not currently used in the dashboard
        'total_num_opportunities_future': total_num_opportunities_future, # 2024-08-23 Not currently used in the dashboard

        'total_num_opportunities_future_week_regular': total_num_opportunities_future_week_regular, # 2024-08-23 Not currently used in the dashboard
        'total_num_opportunities_future_week_preview': total_num_opportunities_future_week_preview, # 2024-08-23 Not currently used in the dashboard
        'total_num_opportunities_future_week': total_num_opportunities_future_week,

        'df_total_activities_counts': df_total_activities_counts,
        'total_num_activities': total_num_activities,
        'total_num_opportunities_with_activities': total_num_opportunities_with_activities,

        # 'df_total_coords_counts': df_total_coords_counts, # 2024-08-23 Not currently used in the dashboard
        # 'total_num_coords': total_num_coords, # 2024-08-23 Not currently used in the dashboard
        # 'total_num_opportunities_with_coords': total_num_opportunities_with_coords, # 2024-08-23 Not currently used in the dashboard

        'gdf_total_regions_counts': gdf_total_regions_counts,
        'total_num_regions': total_num_regions,
        'total_num_opportunities_with_regions': total_num_opportunities_with_regions,

        'gdf_total_lads_counts': gdf_total_lads_counts,
        'total_num_lads': total_num_lads,
        'total_num_opportunities_with_lads': total_num_opportunities_with_lads,

        # 'df_total_sad_counts': df_total_sad_counts, # 2024-08-23 Not currently used in the dashboard
        'df_total_sad_counts_matched': df_total_sad_counts_matched,
        'df_total_sad_counts_unmatched': df_total_sad_counts_unmatched,

        'total_num_activities_with_sad': total_num_activities_with_sad,
        'total_num_activities_without_sad': total_num_activities_without_sad,
        'total_num_opportunities_with_sad': total_num_opportunities_with_sad,
        'total_num_opportunities_without_sad': total_num_opportunities_without_sad,

        'num_sad': num_sad,
        'num_sad_matched': num_sad_matched,
        'num_sad_unmatched': num_sad_unmatched,
        'percentage_sad_matched': percentage_sad_matched,
        'percentage_sad_unmatched': percentage_sad_unmatched,

        'df_se_sport_and_discipline_unmatched': df_se_sport_and_discipline_unmatched,

        'filenames_sampleitems': filenames_sampleitems,
    }

    # --------------------------------------------------------------------------------------------------

    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS_DATA, 'wb') as file_out:
        pickle.dump(df_analysis_data, file_out)

    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'wb') as file_out:
        pickle.dump(analysis, file_out)

    # TEMPORARY: For checking geographically localised high opportunity count spikes
    # global coords_check
    # with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'coords_check.pickle', 'wb') as file_out:
    #     pickle.dump(coords_check, file_out)

# --------------------------------------------------------------------------------------------------

def get_activities_counts(opportunities):
    activities_counts = {}

    for item in opportunities['items'].values():
        item_activities = get_item_activities(item)
        for item_activity in item_activities:
            if (item_activity not in activities_counts.keys()):
                activities_counts[item_activity] = 1
            else:
                activities_counts[item_activity] += 1

    return activities_counts

# --------------------------------------------------------------------------------------------------

# Note that this returns prefLabels from both 'activity' and 'facilityType' lists, which are somewhat
# similar in use:
def get_item_activities(data):
    item_activities = []

    for key, val in data.items():
        if (key in ['activity', 'facilityType']):
            if (isinstance(val, list)):
                item_activities = [
                    i['prefLabel']
                    for i in val
                    if (    (isinstance(i, dict))
                        and ('prefLabel' in i.keys())
                        and (isinstance(i['prefLabel'], str))
                    )
                ]
            elif (  (isinstance(val, dict))
                and ('prefLabel' in val.keys())
                and (isinstance(val['prefLabel'], str))
            ):
                item_activities = [val['prefLabel']]
        elif (isinstance(val, dict)):
            item_activities = get_item_activities(val)
        if (item_activities):
            break

    return item_activities

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
        if (not item_coords):
            item_coords = get_item_coords_from_postalcode(item)
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

postalcodes_coords = {}
time_last_geocode = datetime.now()
def get_item_coords_from_postalcode(data):
    item_coords = []

    global time_last_geocode
    global postalcodes_coords

    for key, val in data.items():
        if (    (key == 'postalCode')
            and (isinstance(val, str))
        ):
            val_mod = val.upper().replace(' ', '')
            if (val_mod not in postalcodes_coords.keys()):
                # https://operations.osmfoundation.org/policies/nominatim/
                # Nominatim usage policy demands "an absolute maximum of 1 request per second", so if less than one
                # second has passed since the last request then wait before proceeding with the next request:
                if ((datetime.now() - time_last_geocode).seconds < 1):
                    sleep(1)
                time_last_geocode = datetime.now()
                loc = geolocator.geocode(val_mod + ',GB')
                if (    (loc is not None)
                    and (loc.latitude is not None)
                    and (loc.longitude is not None)
                ):
                    postalcodes_coords[val_mod] = [
                        round(loc.latitude, NUM_DECIMAL_PLACES_COORDS),
                        round(loc.longitude, NUM_DECIMAL_PLACES_COORDS)
                    ]
                else:
                    print('Can\'t determine coordinates for postalcode:', val)
                    postalcodes_coords[val_mod] = None
            if (postalcodes_coords[val_mod] is not None):
                item_coords = postalcodes_coords[val_mod]
        elif (isinstance(val, dict)):
            item_coords = get_item_coords_from_postalcode(val)
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

def get_df_total_keys_counts(df_analysis_data, keys_counts, feeds_to_include='all'):
    if (feeds_to_include == 'all'):
        df_total_keys_counts = df_analysis_data
    elif (feeds_to_include == 'regular'):
        df_total_keys_counts = df_analysis_data.loc[df_analysis_data['is_regular']]
    elif (feeds_to_include == 'preview'):
        df_total_keys_counts = df_analysis_data.loc[~df_analysis_data['is_regular']]

    df_total_keys_counts = \
        df_total_keys_counts[keys_counts] \
        .apply(pd.Series) \
        .sum() \
        .apply(int) \
        .sort_values(ascending=False) \
        .reset_index()

    if (keys_counts == 'item_kinds_counts'):
        df_total_keys_counts.columns = ['item_kind', 'count']
    elif (keys_counts == 'item_data_types_counts'):
        df_total_keys_counts.columns = ['item_data_type', 'count']
    elif (keys_counts == 'activities_counts'):
        df_total_keys_counts.columns = ['activity', 'count']
    elif (keys_counts == 'coords_counts'):
        df_total_keys_counts.columns = ['coords', 'count']

    total_num_keys = df_total_keys_counts.shape[0]
    total_num_opportunities_with_keys = df_total_keys_counts['count'].sum()

    df_total_keys_counts['percentage'] = (df_total_keys_counts['count'] / total_num_opportunities_with_keys) * 100

    return df_total_keys_counts, total_num_keys, total_num_opportunities_with_keys

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

if (__name__ == '__main__'):
    try:
        get_filenames()
        analyse_opportunities()
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')