import geopandas as gpd
import gzip
import lzma
# import openactive as oa
import pandas as pd
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import tz # For timezone handling
from geopy.geocoders import Nominatim
from numpy import nan
from os import getenv, listdir
from os.path import isfile
from time import sleep

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
FORMAT_FILE_OPPORTUNITIES = 'pickle'
COMPRESSION_FILE_OPPORTUNITIES = getenv('COMPRESSION_FILE_OPPORTUNITIES', 'gzip').lower() # 'none' / 'gzip' / 'xz'
SUFFIX_FILENAME_OPPORTUNITIES = '.' + FORMAT_FILE_OPPORTUNITIES + (('.' + COMPRESSION_FILE_OPPORTUNITIES) if (COMPRESSION_FILE_OPPORTUNITIES != 'none') else '')
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
print('COMPRESSION_FILE_OPPORTUNITIES:', COMPRESSION_FILE_OPPORTUNITIES)
print('FILENAME_ANALYSIS_DATA:', FILENAME_ANALYSIS_DATA)
print('FILENAME_ANALYSIS:', FILENAME_ANALYSIS)
print('FILENAME_REGIONS:', FILENAME_REGIONS)
print('FILENAME_LADS:', FILENAME_LADS)
print('FILENAME_SE_SPORT_AND_DISCIPLINE:', FILENAME_SE_SPORT_AND_DISCIPLINE)
print('FILENAME_OA_SE_MAPPING:', FILENAME_OA_SE_MAPPING)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

def create_summary(): 

    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS_DATA, 'rb') as file_in:
         df_analysis_data = pickle.load(file_in)
         
    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_SAMPLE_DATA, 'rb') as file_in:
         filenames_sampleitems = pickle.load(file_in)

    with open(RELATIVE_FILEPATH_FEEDS + '/' + FILENAME_FEEDS, 'rb') as file_in:
        feeds = pickle.load(file_in)

    with open(RELATIVE_FILEPATH_FEEDS + '/' + FILENAME_FEEDS_PREVIEW, 'rb') as file_in:
        feeds_preview = pickle.load(file_in)

    # --------------------------------------------------------------------------------------------------

    # For the 'Overview' tab

    num_publishers_regular = df_analysis_data['publisher_name'].loc[df_analysis_data['is_regular']].replace('', nan).nunique()
    num_publishers_preview = df_analysis_data['publisher_name'].loc[~df_analysis_data['is_regular']].replace('', nan).nunique()
    num_publishers = df_analysis_data['publisher_name'].replace('', nan).nunique()

    num_datasets_regular = df_analysis_data['dataset_url'].loc[df_analysis_data['is_regular']].replace('', nan).nunique()
    num_datasets_preview = df_analysis_data['dataset_url'].loc[~df_analysis_data['is_regular']].replace('', nan).nunique()
    num_datasets = df_analysis_data['dataset_url'].replace('', nan).nunique()

    num_feeds_regular = feeds['num_feeds']
    num_feeds_preview = feeds_preview['num_feeds']
    num_feeds = num_feeds_regular + num_feeds_preview

    num_feeds_with_analysed_data_regular = \
            (df_analysis_data.loc[df_analysis_data['is_regular'] & df_analysis_data['is_merged_with_partner']].shape[0] * 2) \
        +   (df_analysis_data.loc[df_analysis_data['is_regular'] & ~df_analysis_data['is_merged_with_partner']].shape[0])
    num_feeds_with_analysed_data_preview = \
            (df_analysis_data.loc[~df_analysis_data['is_regular'] & df_analysis_data['is_merged_with_partner']].shape[0] * 2) \
        +   (df_analysis_data.loc[~df_analysis_data['is_regular'] & ~df_analysis_data['is_merged_with_partner']].shape[0])
    num_feeds_with_analysed_data = num_feeds_with_analysed_data_regular + num_feeds_with_analysed_data_preview

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
    total_num_opportunities_with_activities = get_df_total_values_counts(df_analysis_data, 'activities_counts', feeds_to_include='all')

    # --------------------------------------------------------------------------------------------------

    # For the 'Organisers' tab

    # Columns: ['organiser', 'count', 'percentage']
    df_total_organisers_counts, \
    total_num_organisers, \
    total_num_opportunities_with_organisers = get_df_total_values_counts(df_analysis_data, 'organisers_counts', feeds_to_include='all')

    # --------------------------------------------------------------------------------------------------

    # For the 'Locations' tab

    # Columns: ['coords', 'count', 'percentage']
    df_total_coords_counts, \
    total_num_coords, \
    total_num_opportunities_with_coords = get_df_total_values_counts(df_analysis_data, 'coords_counts', feeds_to_include='all')
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

    # For the 'Labels' tab

    # Columns: ['kind', 'count', 'percentage']
    df_total_kinds_counts, \
    total_num_kinds, \
    total_num_opportunities_with_kinds = get_df_total_values_counts(df_analysis_data, 'kinds_counts', feeds_to_include='all')

    # Columns: ['type', 'count', 'percentage']
    df_total_types_counts, \
    total_num_types, \
    total_num_opportunities_with_types = get_df_total_values_counts(df_analysis_data, 'types_counts', feeds_to_include='all')
    # --------------------------------------------------------------------------------------------------

    # Columns: ['address', 'count', 'percentage']
    df_total_address_counts, \
    total_num_address, \
    total_num_opportunities_with_address = get_df_total_values_counts(df_analysis_data, 'address_counts', feeds_to_include='all')

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

        'num_feeds_with_analysed_data_regular': num_feeds_with_analysed_data_regular, # 2024-09-27 Not currently used in the dashboard
        'num_feeds_with_analysed_data_preview': num_feeds_with_analysed_data_preview, # 2024-09-27 Not currently used in the dashboard
        'num_feeds_with_analysed_data': num_feeds_with_analysed_data, # 2024-09-27 Not currently used in the dashboard

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

        'df_total_organisers_counts': df_total_organisers_counts,
        'total_num_organisers': total_num_organisers,
        'total_num_opportunities_with_organisers': total_num_opportunities_with_organisers,

        # 'df_total_coords_counts': df_total_coords_counts, # 2024-08-23 Not currently used in the dashboard
        # 'total_num_coords': total_num_coords, # 2024-08-23 Not currently used in the dashboard
        # 'total_num_opportunities_with_coords': total_num_opportunities_with_coords, # 2024-08-23 Not currently used in the dashboard

        'gdf_total_regions_counts': gdf_total_regions_counts,
        'total_num_regions': total_num_regions,
        'total_num_opportunities_with_regions': total_num_opportunities_with_regions,

        'gdf_total_lads_counts': gdf_total_lads_counts,
        'total_num_lads': total_num_lads,
        'total_num_opportunities_with_lads': total_num_opportunities_with_lads,

        'df_total_kinds_counts': df_total_kinds_counts,
        'total_num_kinds': total_num_kinds,
        'total_num_opportunities_with_kinds': total_num_opportunities_with_kinds,

        'df_total_types_counts': df_total_types_counts,
        'total_num_types': total_num_types,
        'total_num_opportunities_with_types': total_num_opportunities_with_types,
        
        'df_total_address_counts': df_total_address_counts,
        'total_num_address': total_num_address,
        'total_num_opportunities_with_address': total_num_opportunities_with_address,
        
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

    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'wb') as file_out:
        pickle.dump(analysis, file_out)

    # TEMPORARY: For checking geographically localised high opportunity count spikes
    # global coords_check
    # with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'coords_check.pickle', 'wb') as file_out:
    #     pickle.dump(coords_check, file_out)

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
    elif (values_counts == 'address_counts'):
        df_total_values_counts.columns = ['address', 'count']
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