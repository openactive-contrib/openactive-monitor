import geopandas as gpd
import pandas as pd
import pickle
import sys
from numpy import nan

sys.path.append('../volume-1/common')
from settings import *

# --------------------------------------------------------------------------------------------------

def analyse_opportunities_aggregated(**kwargs):
    verbose = kwargs.get('verbose', False)

    # --------------------------------------------------------------------------------------------------

    with open(FEEDS_RELATIVE_FILEPATH + '/' + REGULAR_FEEDS_LATEST_FILENAME, 'rb') as file_in:
        feeds_regular = pickle.load(file_in)

    with open(FEEDS_RELATIVE_FILEPATH + '/' + PREVIEW_FEEDS_LATEST_FILENAME, 'rb') as file_in:
        feeds_preview = pickle.load(file_in)

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + ANALYSIS_PER_FEED_FILENAME, 'rb') as file_in:
         df_analysis_data = pickle.load(file_in)

    # --------------------------------------------------------------------------------------------------

    # For the 'Overview' tab

    num_publishers_regular = df_analysis_data['publisher_name'].loc[df_analysis_data['is_regular']].replace('', nan).nunique()
    num_publishers_preview = df_analysis_data['publisher_name'].loc[~df_analysis_data['is_regular']].replace('', nan).nunique()
    num_publishers = df_analysis_data['publisher_name'].replace('', nan).nunique()

    num_datasets_regular = df_analysis_data['dataset_url'].loc[df_analysis_data['is_regular']].replace('', nan).nunique()
    num_datasets_preview = df_analysis_data['dataset_url'].loc[~df_analysis_data['is_regular']].replace('', nan).nunique()
    num_datasets = df_analysis_data['dataset_url'].replace('', nan).nunique()

    num_feeds_regular = len(feeds_regular)
    num_feeds_preview = len(feeds_preview)
    num_feeds = num_feeds_regular + num_feeds_preview

    num_feeds_with_analysed_data_regular = \
            (df_analysis_data.loc[df_analysis_data['is_regular'] & df_analysis_data['is_merged_with_partner']].shape[0] * 2) \
        +   (df_analysis_data.loc[df_analysis_data['is_regular'] & ~df_analysis_data['is_merged_with_partner']].shape[0])
    num_feeds_with_analysed_data_preview = \
            (df_analysis_data.loc[~df_analysis_data['is_regular'] & df_analysis_data['is_merged_with_partner']].shape[0] * 2) \
        +   (df_analysis_data.loc[~df_analysis_data['is_regular'] & ~df_analysis_data['is_merged_with_partner']].shape[0])
    num_feeds_with_analysed_data = num_feeds_with_analysed_data_regular + num_feeds_with_analysed_data_preview

    total_num_items_regular = df_analysis_data['num_items'].loc[df_analysis_data['is_regular']].sum()
    total_num_items_preview = df_analysis_data['num_items'].loc[~df_analysis_data['is_regular']].sum()
    total_num_items = total_num_items_regular + total_num_items_preview

    # --------------------------------------------------------------------------------------------------

    # For the 'This week' tab

    total_num_future_items_regular = df_analysis_data['num_future_items'].loc[df_analysis_data['is_regular']].sum()
    total_num_future_items_preview = df_analysis_data['num_future_items'].loc[~df_analysis_data['is_regular']].sum()
    total_num_future_items = total_num_future_items_regular + total_num_future_items_preview

    total_num_future_week_items_regular = df_analysis_data['num_future_week_items'].loc[df_analysis_data['is_regular']].sum()
    total_num_future_week_items_preview = df_analysis_data['num_future_week_items'].loc[~df_analysis_data['is_regular']].sum()
    total_num_future_week_items = total_num_future_week_items_regular + total_num_future_week_items_preview

    # --------------------------------------------------------------------------------------------------

    # For the 'Activities' tab

    # Columns: ['activity', 'count', 'percentage']
    df_total_activities_counts, \
    total_num_activities, \
    total_num_items_with_activities = get_df_total_values_counts(df_analysis_data, 'activities_counts', feeds_to_include='all')

    # --------------------------------------------------------------------------------------------------

    # For the 'Organisers' tab

    # Columns: ['organiser', 'count', 'percentage']
    df_total_organisers_counts, \
    total_num_organisers, \
    total_num_items_with_organisers = get_df_total_values_counts(df_analysis_data, 'organisers_counts', feeds_to_include='all')

    # --------------------------------------------------------------------------------------------------

    # For the 'Locations' tab

    # Columns: ['address', 'count', 'percentage']
    df_total_addresses_counts, \
    total_num_addresses, \
    total_num_items_with_addresses = get_df_total_values_counts(df_analysis_data, 'addresses_counts', feeds_to_include='all')

    # Columns: ['latlon', 'count', 'percentage']
    df_total_latlons_counts, \
    total_num_latlons, \
    total_num_items_with_latlons = get_df_total_values_counts(df_analysis_data, 'latlons_counts', feeds_to_include='all')
    # Columns: ['latlon', 'count', 'percentage', 'latitude', 'longitude']
    df_total_latlons_counts[['latitude', 'longitude']] = pd.DataFrame(df_total_latlons_counts['latlon'].apply(lambda latlon: latlon.split(',')).tolist())
    # Columns: ['latitude', 'longitude', 'count', 'percentage']
    df_total_latlons_counts = df_total_latlons_counts[['latitude', 'longitude', 'count', 'percentage']]

    # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry']
    gdf_regions = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_REGIONS_FILENAME)
    # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry']
    gdf_lads = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_LADS_FILENAME)

    # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_regions_counts, \
    total_num_regions, \
    total_num_items_with_regions = get_gdf_total_locations_counts(df_total_latlons_counts, gdf_regions, 'eer18nm')

    # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_lads_counts, \
    total_num_lads, \
    total_num_items_with_lads = get_gdf_total_locations_counts(df_total_latlons_counts, gdf_lads, 'LAD24NM')

    # --------------------------------------------------------------------------------------------------

    # For the 'Labels' tab

    # Columns: ['item_kind', 'count', 'percentage']
    df_total_item_kinds_counts, \
    total_num_item_kinds, \
    total_num_items_with_kinds = get_df_total_values_counts(df_analysis_data, 'item_kinds_counts', feeds_to_include='all')

    # Columns: ['item_data_type', 'count', 'percentage']
    df_total_item_data_types_counts, \
    total_num_item_data_types, \
    total_num_items_with_data_types = get_df_total_values_counts(df_analysis_data, 'item_data_types_counts', feeds_to_include='all')

    # --------------------------------------------------------------------------------------------------

    # For the 'KPIs' tab

    # Columns: ['sport', 'discipline', 'sport_and_discipline']
    df_se_sport_and_discipline = pd.read_csv(ANALYSIS_RELATIVE_FILEPATH + '/' + SE_SPORT_AND_DISCIPLINE_FILENAME)
    # Columns: ['activity', 'sport_and_discipline']
    df_oa_se_mapping = pd.read_csv(ANALYSIS_RELATIVE_FILEPATH + '/' + OA_SE_MAPPING_FILENAME)

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

    # df_oa_se_mapping.to_csv(ANALYSIS_RELATIVE_FILEPATH + '/' + OA_SE_MAPPING_FILENAME)

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
    df_total_sad_counts_na.to_csv(ANALYSIS_RELATIVE_FILEPATH + '/' + 'unmatched_activities.csv', index=False)

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
    # Columns: ['sport_and_discipline', 'activity', 'count_activities', 'count_items']
    df_total_sad_counts_matched.columns = [
        'sport_and_discipline',
        'activity',
        'count_activities',
        'count_items',
    ]

    # Columns: ['sport_and_discipline', 'activity', 'count']
    df_total_sad_counts_unmatched = df_total_sad_counts_unmatched[['sport_and_discipline', 'activity', 'count']]
    # Rename columns for consistency with df_total_sad_counts_matched, even though there's only one count here:
    # Columns: ['sport_and_discipline', 'activity', 'count_items']
    df_total_sad_counts_unmatched.columns = [
        'sport_and_discipline',
        'activity',
        'count_items',
    ]

    total_num_activities_with_sad = df_total_sad_counts_matched['count_activities'].sum()
    total_num_activities_without_sad = df_total_sad_counts_unmatched.shape[0]
    total_num_items_with_sad = df_total_sad_counts_matched['count_items'].sum()
    total_num_items_without_sad = df_total_sad_counts_unmatched['count_items'].sum()

    # Columns: ['sport_and_discipline', 'activity', 'count_activities', 'count_items', 'percentage_activities', 'percentage_items']
    df_total_sad_counts_matched['percentage_activities'] = (df_total_sad_counts_matched['count_activities'] / total_num_activities_with_sad) * 100
    df_total_sad_counts_matched['percentage_items'] = (df_total_sad_counts_matched['count_items'] / total_num_items_with_sad) * 100

    # Columns: ['sport_and_discipline', 'activity', 'count_items', 'percentage_items']
    df_total_sad_counts_unmatched['percentage_items'] = (df_total_sad_counts_unmatched['count_items'] / total_num_items_without_sad) * 100

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

        'total_num_items_regular': total_num_items_regular, # 2024-08-23 Not currently used in the dashboard
        'total_num_items_preview': total_num_items_preview,
        'total_num_items': total_num_items,

        'total_num_future_items_regular': total_num_future_items_regular, # 2024-08-23 Not currently used in the dashboard
        'total_num_future_items_preview': total_num_future_items_preview, # 2024-08-23 Not currently used in the dashboard
        'total_num_future_items': total_num_future_items,

        'total_num_future_week_items_regular': total_num_future_week_items_regular, # 2024-08-23 Not currently used in the dashboard
        'total_num_future_week_items_preview': total_num_future_week_items_preview, # 2024-08-23 Not currently used in the dashboard
        'total_num_future_week_items': total_num_future_week_items,

        'df_total_activities_counts': df_total_activities_counts,
        'total_num_activities': total_num_activities,
        'total_num_items_with_activities': total_num_items_with_activities,

        'df_total_organisers_counts': df_total_organisers_counts,
        'total_num_organisers': total_num_organisers,
        'total_num_items_with_organisers': total_num_items_with_organisers,

        'df_total_addresses_counts': df_total_addresses_counts,
        'total_num_addresses': total_num_addresses,
        'total_num_items_with_addresses': total_num_items_with_addresses,

        'df_total_latlons_counts': df_total_latlons_counts, # 2024-08-23 Not currently used in the dashboard
        'total_num_latlons': total_num_latlons, # 2024-08-23 Not currently used in the dashboard
        'total_num_items_with_latlons': total_num_items_with_latlons, # 2024-08-23 Not currently used in the dashboard

        'gdf_total_regions_counts': gdf_total_regions_counts,
        'total_num_regions': total_num_regions,
        'total_num_items_with_regions': total_num_items_with_regions,

        'gdf_total_lads_counts': gdf_total_lads_counts,
        'total_num_lads': total_num_lads,
        'total_num_items_with_lads': total_num_items_with_lads,

        'df_total_item_kinds_counts': df_total_item_kinds_counts,
        'total_num_item_kinds': total_num_item_kinds,
        'total_num_items_with_kinds': total_num_items_with_kinds,

        'df_total_item_data_types_counts': df_total_item_data_types_counts,
        'total_num_item_data_types': total_num_item_data_types,
        'total_num_items_with_data_types': total_num_items_with_data_types,

        # 'df_total_sad_counts': df_total_sad_counts, # 2024-08-23 Not currently used in the dashboard
        'df_total_sad_counts_matched': df_total_sad_counts_matched,
        'df_total_sad_counts_unmatched': df_total_sad_counts_unmatched,

        'total_num_activities_with_sad': total_num_activities_with_sad,
        'total_num_activities_without_sad': total_num_activities_without_sad,
        'total_num_items_with_sad': total_num_items_with_sad,
        'total_num_items_without_sad': total_num_items_without_sad,

        'num_sad': num_sad,
        'num_sad_matched': num_sad_matched,
        'num_sad_unmatched': num_sad_unmatched,
        'percentage_sad_matched': percentage_sad_matched,
        'percentage_sad_unmatched': percentage_sad_unmatched,

        'df_se_sport_and_discipline_unmatched': df_se_sport_and_discipline_unmatched,
    }

    # --------------------------------------------------------------------------------------------------

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + ANALYSIS_AGGREGATED_FILENAME, 'wb') as file_out:
        pickle.dump(analysis, file_out)

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

    if (values_counts == 'item_kinds_counts'):
        df_total_values_counts.columns = ['item_kind', 'count']
    elif (values_counts == 'item_data_types_counts'):
        df_total_values_counts.columns = ['item_data_type', 'count']
    elif (values_counts == 'activities_counts'):
        df_total_values_counts.columns = ['activity', 'count']
    elif (values_counts == 'organisers_counts'):
        df_total_values_counts.columns = ['organiser', 'count']
    elif (values_counts == 'addresses_counts'):
        df_total_values_counts.columns = ['address', 'count']
    elif (values_counts == 'latlons_counts'):
        df_total_values_counts.columns = ['latlon', 'count']

    total_num_keys = df_total_values_counts.shape[0]
    total_num_items_with_keys = df_total_values_counts['count'].sum()

    df_total_values_counts['percentage'] = (df_total_values_counts['count'] / total_num_items_with_keys) * 100

    return df_total_values_counts, total_num_keys, total_num_items_with_keys

# --------------------------------------------------------------------------------------------------

def get_gdf_total_locations_counts(df_total_latlons_counts, gdf_locations, gdf_locations_name_column):
    # Columns: ['latitude', 'longitude', 'count', 'percentage', 'geometry']
    gdf_total_latlons_counts = gpd.GeoDataFrame(
            df_total_latlons_counts,
            geometry=gpd.points_from_xy(
                df_total_latlons_counts['longitude'],
                df_total_latlons_counts['latitude'],
            ),
            crs='epsg:4326', # Set CRS to WGS84
        ) \
        .to_crs(gdf_locations.crs)

    # Columns: [<gdf_locations_name_column>, 'count']
    gdf_total_locations_counts = gpd.GeoDataFrame(
        gpd.sjoin(
            gdf_locations[['geometry', gdf_locations_name_column]],
            gdf_total_latlons_counts[['geometry', 'count']],
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
    total_num_items_with_locations = gdf_total_locations_counts['count'].sum()

    # If gdf_locations is 'regions.geojson':
    #     Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
    # If gdf_locations is 'lads.geojson':
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_locations_counts['percentage'] = (gdf_total_locations_counts['count'] / total_num_items_with_locations) * 100

    # print(f'gdf_total_locations_counts ({gdf_locations_name_column}):')
    # print(gdf_total_locations_counts)

    return gdf_total_locations_counts, total_num_locations, total_num_items_with_locations