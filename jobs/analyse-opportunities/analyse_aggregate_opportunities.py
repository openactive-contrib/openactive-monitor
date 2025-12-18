import geopandas as gpd
import pandas as pd
import pickle
import sys
from numpy import nan

sys.path.append('../volume-1/common')
from settings import *

# --------------------------------------------------------------------------------------------------

def analyse_aggregate_opportunities(**kwargs):
    verbose = kwargs.get('verbose', False)

    # --------------------------------------------------------------------------------------------------

    with open(FEEDS_RELATIVE_FILEPATH + '/' + REGULAR_FEEDS_LATEST_FILENAME, 'rb') as file_in:
        feeds_regular = pickle.load(file_in)

    with open(FEEDS_RELATIVE_FILEPATH + '/' + PREVIEW_FEEDS_LATEST_FILENAME, 'rb') as file_in:
        feeds_preview = pickle.load(file_in)

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + SEPARATE_ANALYSIS_FILENAME, 'rb') as file_in:
        separate_analysis = pickle.load(file_in)

    # --------------------------------------------------------------------------------------------------

    num_publishers_regular = separate_analysis['publisher_name'].loc[separate_analysis['is_regular']].replace('', nan).nunique()
    num_publishers_preview = separate_analysis['publisher_name'].loc[~separate_analysis['is_regular']].replace('', nan).nunique()
    num_publishers = separate_analysis['publisher_name'].replace('', nan).nunique()

    num_datasets_regular = separate_analysis['dataset_url'].loc[separate_analysis['is_regular']].replace('', nan).nunique()
    num_datasets_preview = separate_analysis['dataset_url'].loc[~separate_analysis['is_regular']].replace('', nan).nunique()
    num_datasets = separate_analysis['dataset_url'].replace('', nan).nunique()

    # The numbers of feeds here are the numbers of feeds retrieved from the latest crawl of datasets. Not
    # all of these feeds will be available or serving data, they are simply the known end-points that MAY
    # be available and serving data. As such, these numbers are the upper limits of what's currently live
    # in the ecosystem:

    num_feeds_regular = len(feeds_regular)
    num_feeds_preview = len(feeds_preview)
    num_feeds = num_feeds_regular + num_feeds_preview

    # The numbers of feeds here are the numbers of feeds that have been available and serving data, and
    # which therefore led to an opportunities file. These numbers should therefore equate to the numbers
    # of opportunities files in the associated storage volume. However, this includes files that may be
    # present from earlier than the latest crawl of feeds, which appear as and when previously available
    # feeds become unavailable, either temporarily or permanently. Such older files are intentionally kept
    # to use as a basis for as and when their associated feeds become live again. Even though such files
    # are not entirely up-to-date, they may still contain future items and still contribute to the analysis,
    # hence their inclusion in these counts:

    num_feeds_with_analysed_data_regular = \
            (separate_analysis.loc[separate_analysis['is_regular'] & separate_analysis['is_merged_with_partner']].shape[0] * 2) \
        +   (separate_analysis.loc[separate_analysis['is_regular'] & ~separate_analysis['is_merged_with_partner']].shape[0])
    num_feeds_with_analysed_data_preview = \
            (separate_analysis.loc[~separate_analysis['is_regular'] & separate_analysis['is_merged_with_partner']].shape[0] * 2) \
        +   (separate_analysis.loc[~separate_analysis['is_regular'] & ~separate_analysis['is_merged_with_partner']].shape[0])
    num_feeds_with_analysed_data = num_feeds_with_analysed_data_regular + num_feeds_with_analysed_data_preview

    # TODO: Get counts of feeds with future items. This will be the most relevant count to best represent the live ecosystem.

    total_num_items_regular = separate_analysis['num_items'].loc[separate_analysis['is_regular']].sum()
    total_num_items_preview = separate_analysis['num_items'].loc[~separate_analysis['is_regular']].sum()
    total_num_items = total_num_items_regular + total_num_items_preview

    # --------------------------------------------------------------------------------------------------

    total_num_future_items_regular = separate_analysis['num_future_items'].loc[separate_analysis['is_regular']].sum()
    total_num_future_items_preview = separate_analysis['num_future_items'].loc[~separate_analysis['is_regular']].sum()
    total_num_future_items = total_num_future_items_regular + total_num_future_items_preview

    total_num_future_week_items_regular = separate_analysis['num_future_week_items'].loc[separate_analysis['is_regular']].sum()
    total_num_future_week_items_preview = separate_analysis['num_future_week_items'].loc[~separate_analysis['is_regular']].sum()
    total_num_future_week_items = total_num_future_week_items_regular + total_num_future_week_items_preview

    # --------------------------------------------------------------------------------------------------

    df_total_item_kinds_counts, \
    total_num_item_kinds, \
    total_num_items_with_kinds = get_df_total_values_counts(separate_analysis, 'item_kinds_counts', feeds_to_include='all')

    # Columns: ['item_kind', 'count', 'percentage']
    df_total_item_kinds_counts.rename(columns={'value': 'item_kind'}, inplace=True)

    # --------------------------------------------------------------------------------------------------

    df_total_item_data_types_counts, \
    total_num_item_data_types, \
    total_num_items_with_data_types = get_df_total_values_counts(separate_analysis, 'item_data_types_counts', feeds_to_include='all')

    # Columns: ['item_data_type', 'count', 'percentage']
    df_total_item_data_types_counts.rename(columns={'value': 'item_data_type'}, inplace=True)

    # --------------------------------------------------------------------------------------------------

    df_total_activities_counts, \
    total_num_activities, \
    total_num_items_with_activities = get_df_total_values_counts(separate_analysis, 'activities_counts', feeds_to_include='all')

    # Columns: ['activity', 'count', 'percentage']
    df_total_activities_counts.rename(columns={'value': 'activity'}, inplace=True)

    # --------------------------------------------------------------------------------------------------

    df_total_organisers_counts, \
    total_num_organisers, \
    total_num_items_with_organisers = get_df_total_values_counts(separate_analysis, 'organisers_counts', feeds_to_include='all')

    # Columns: ['organiser', 'count', 'percentage']
    df_total_organisers_counts.rename(columns={'value': 'organiser'}, inplace=True)

    # --------------------------------------------------------------------------------------------------

    df_total_postcodes_counts, \
    total_num_postcodes, \
    total_num_items_with_postcodes = get_df_total_values_counts(separate_analysis, 'postcodes_counts', feeds_to_include='all')

    # Columns: ['postcode', 'count', 'percentage']
    df_total_postcodes_counts.rename(columns={'value': 'postcode'}, inplace=True)

    # --------------------------------------------------------------------------------------------------

    df_total_latlons_counts, \
    total_num_latlons, \
    total_num_items_with_latlons = get_df_total_values_counts(separate_analysis, 'latlons_counts', feeds_to_include='all')

    # Columns: ['latlon', 'count', 'percentage']
    df_total_latlons_counts.rename(columns={'value': 'latlon'}, inplace=True)

    # Columns: ['latlon', 'count', 'percentage', 'latitude', 'longitude']
    df_total_latlons_counts[['latitude', 'longitude']] = pd.DataFrame(df_total_latlons_counts['latlon'].apply(lambda latlon: [float(coord) for coord in latlon.split(',')]).tolist())

    # Columns: ['latitude', 'longitude', 'count', 'percentage']
    df_total_latlons_counts = df_total_latlons_counts[['latitude', 'longitude', 'count', 'percentage']]

    # --------------------------------------------------------------------------------------------------

    # The first few rows of gdf_regions are like:
    #    OBJECTID  eer18cd    eer18nm                   bng_e   bng_n   long       lat        GlobalID                              geometry
    # 0  1         E15000001  North East                417313  600358  -1.728900  55.297031  fbbc6e4d-8fd6-4719-a21d-49b62ff3af9b  MULTIPOLYGON (((397943.500 657534.102, 401095....
    # 1  2         E15000002  North West                350015  506280  -2.772370  54.449451  89a00d05-0013-4ac5-9db3-035c06600433  MULTIPOLYGON (((363823.401 578129.102, 364213....
    # 2  3         E15000003  Yorkshire and The Humber  446903  448736  -1.287120  53.932640  ccc57252-deb9-48dd-85b0-d31e38682574  MULTIPOLYGON (((479351.004 518706.501, 481340....
    # 3  4         E15000004  East Midlands             477660  322635  -0.849670  52.795719  68dfd43b-2798-4f85-a7db-bcc09b13b44c  POLYGON ((516022.702 412210.895, 515854.099 41...
    # 4  5         E15000005  West Midlands             386294  295477  -2.203580  52.556969  faba9cae-a323-43f9-9142-59832d9518c8  POLYGON ((409402.997 365710.796, 412633.099 36...
    # 12 rows total

    gdf_regions = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_REGIONS_FILENAME)

    # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_regions_counts, \
    total_num_regions, \
    total_num_items_with_regions = get_gdf_total_locations_counts(df_total_latlons_counts, gdf_regions, 'eer18nm')

    # --------------------------------------------------------------------------------------------------

    # LADs = Local Authority Districts, which are much smaller than regions, hence the higher row count.

    # The first few rows of gdf_lads are like:
    #    FID  LAD24CD    LAD24NM               LAD24NMW  BNG_E   BNG_N   LONG      LAT       GlobalID                              geometry
    # 0  1    E06000001  Hartlepool                      447161  531473  -1.27017  54.67613  3f58aa35-9ea6-4001-a80f-8aab0e41313f  POLYGON ((448964.105 536757.184, 448986.025 53...
    # 1  2    E06000002  Middlesbrough                   451141  516887  -1.21099  54.54467  c5bc1c3e-111f-46db-8e41-362fbbc78d30  POLYGON ((451894.299 521145.303, 453997.697 51...
    # 2  3    E06000003  Redcar and Cleveland            464330  519596  -1.00656  54.56752  29afa1cb-8719-44c2-9906-38bc7bae2981  POLYGON ((478232.947 518788.802, 477689.303 51...
    # 3  4    E06000004  Stockton-on-Tees                444940  518179  -1.30664  54.55687  8ebb86c0-86bb-466e-ae7e-a832eeb755ff  POLYGON ((452243.536 526335.188, 451711.300 52...
    # 4  5    E06000005  Darlington                      428029  515648  -1.56835  54.53534  bf2173db-02e1-4b58-9617-e775100f58ec  POLYGON ((436388.002 522354.197, 437351.702 52...
    # 361 rows total

    gdf_lads = gpd.read_file(ANALYSIS_RELATIVE_FILEPATH + '/' + GEO_LADS_FILENAME)

    # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_lads_counts, \
    total_num_lads, \
    total_num_items_with_lads = get_gdf_total_locations_counts(df_total_latlons_counts, gdf_lads, 'LAD24NM')

    # --------------------------------------------------------------------------------------------------

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

    aggregate_analysis = {
        'num_publishers_regular': num_publishers_regular,
        'num_publishers_preview': num_publishers_preview,
        'num_publishers': num_publishers,

        'num_datasets_regular': num_datasets_regular,
        'num_datasets_preview': num_datasets_preview,
        'num_datasets': num_datasets,

        'num_feeds_regular': num_feeds_regular,
        'num_feeds_preview': num_feeds_preview,
        'num_feeds': num_feeds,

        'num_feeds_with_analysed_data_regular': num_feeds_with_analysed_data_regular,
        'num_feeds_with_analysed_data_preview': num_feeds_with_analysed_data_preview,
        'num_feeds_with_analysed_data': num_feeds_with_analysed_data,

        'total_num_items_regular': total_num_items_regular,
        'total_num_items_preview': total_num_items_preview,
        'total_num_items': total_num_items,

        'total_num_future_items_regular': total_num_future_items_regular,
        'total_num_future_items_preview': total_num_future_items_preview,
        'total_num_future_items': total_num_future_items,

        'total_num_future_week_items_regular': total_num_future_week_items_regular,
        'total_num_future_week_items_preview': total_num_future_week_items_preview,
        'total_num_future_week_items': total_num_future_week_items,

        'df_total_item_kinds_counts': df_total_item_kinds_counts,
        'total_num_item_kinds': total_num_item_kinds,
        'total_num_items_with_kinds': total_num_items_with_kinds,

        'df_total_item_data_types_counts': df_total_item_data_types_counts,
        'total_num_item_data_types': total_num_item_data_types,
        'total_num_items_with_data_types': total_num_items_with_data_types,

        'df_total_activities_counts': df_total_activities_counts,
        'total_num_activities': total_num_activities,
        'total_num_items_with_activities': total_num_items_with_activities,

        'df_total_organisers_counts': df_total_organisers_counts,
        'total_num_organisers': total_num_organisers,
        'total_num_items_with_organisers': total_num_items_with_organisers,

        'df_total_postcodes_counts': df_total_postcodes_counts,
        'total_num_postcodes': total_num_postcodes,
        'total_num_items_with_postcodes': total_num_items_with_postcodes,

        'df_total_latlons_counts': df_total_latlons_counts,
        'total_num_latlons': total_num_latlons,
        'total_num_items_with_latlons': total_num_items_with_latlons,

        'gdf_total_regions_counts': gdf_total_regions_counts,
        'total_num_regions': total_num_regions,
        'total_num_items_with_regions': total_num_items_with_regions,

        'gdf_total_lads_counts': gdf_total_lads_counts,
        'total_num_lads': total_num_lads,
        'total_num_items_with_lads': total_num_items_with_lads,

        'df_total_sad_counts': df_total_sad_counts,
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

    with open(ANALYSIS_RELATIVE_FILEPATH + '/' + AGGREGATE_ANALYSIS_FILENAME, 'wb') as file_out:
        pickle.dump(aggregate_analysis, file_out)

# --------------------------------------------------------------------------------------------------

def get_df_total_values_counts(separate_analysis, values_counts, feeds_to_include='all'):
    if (feeds_to_include == 'all'):
        df_total_values_counts = separate_analysis
    elif (feeds_to_include == 'regular'):
        df_total_values_counts = separate_analysis.loc[separate_analysis['is_regular']]
    elif (feeds_to_include == 'preview'):
        df_total_values_counts = separate_analysis.loc[~separate_analysis['is_regular']]

    df_total_values_counts = \
        df_total_values_counts[values_counts] \
        .apply(pd.Series) \
        .sum() \
        .apply(int) \
        .sort_values(ascending=False) \
        .reset_index()

    df_total_values_counts.columns = ['value', 'count']

    total_num_values = df_total_values_counts.shape[0]
    total_num_items_with_values = df_total_values_counts['count'].sum()

    df_total_values_counts['percentage'] = (df_total_values_counts['count'] / total_num_items_with_values) * 100

    # The columns of df_total_values_counts are now:
    # ['value', 'count', 'percentage']

    return df_total_values_counts, total_num_values, total_num_items_with_values

# --------------------------------------------------------------------------------------------------

def get_gdf_total_locations_counts(df_total_latlons_counts, gdf_locations, gdf_locations_name_column):
    # A 'geometry' column contains a set of POINT coordinate objects, the contents of which depends on
    # exactly what Coordinate Reference System (CRS) is in use. In the following, we at first define such
    # a column as lonlat pairs (not latlon pairs!) before immediately converting to the CRS of an existing
    # input file i.e. the regions or Local Authority Districts (LADs) file. These happen to be in terms
    # of easting and northing, which have units of metres. Say we start with the following latlon pair:
    #   51.09163 -0.749606
    # This then gets converted to the following lonlat POINT object:
    #   POINT (-0.74961 51.09163)
    # Which then gets converted to the following easting northing POINT object:
    #   POINT (487662.910 133223.698)
    # There are a number of online tools to check these conversions if needed.

    # Columns: ['latitude', 'longitude', 'count', 'percentage', 'geometry']
    gdf_total_latlons_counts = gpd.GeoDataFrame(
        df_total_latlons_counts,
        geometry=gpd.points_from_xy(
            df_total_latlons_counts['longitude'],
            df_total_latlons_counts['latitude'],
        ),
        crs='epsg:4326', # Set Coordinate Reference System (CRS) to World Geodetic System 1984 (WGS84). See https://epsg.io/4326.
    ) \
    .to_crs(gdf_locations.crs)

    # --------------------------------------------------------------------------------------------------

    # Match the geometry POINT objects within gdf_total_latlons_counts to the geometry POLYGON and MULTIPOLYGON
    # objects within gdf_locations i.e. find the matching location (region or LAD) for each given POINT.
    # Group the counts by location and sum to get total counts for each location:

    # Columns: [<gdf_locations_name_column>, 'count']
    gdf_total_locations_counts = gpd.GeoDataFrame(
        gpd.sjoin(
            gdf_total_latlons_counts[['geometry', 'count']], # Left dataframe
            gdf_locations[['geometry', gdf_locations_name_column]], # Right dataframe
            how='left', # Use keys (i.e. rows) from left dataframe, and retain only left dataframe geometry column
            predicate='intersects',
        ) \
        .groupby(gdf_locations_name_column)['count'] \
        .sum()
    ) \
    .reset_index()

    # --------------------------------------------------------------------------------------------------

    # Merge the count values just obtained into the given location info dataframe. We use this as a basis
    # for the output of this function as the geometry info is needed for the front-end map display:

    # If gdf_locations is for regions:
    #     Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count']
    # If gdf_locations is for LADs:
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count']
    gdf_total_locations_counts = \
        gdf_locations \
        .merge(gdf_total_locations_counts, on=gdf_locations_name_column, how='left') \
        .sort_values(by='count', ascending=False) \
        .fillna(0)

    # If we had any NaN count rows during the last manipulation, then the count column would have been
    # converted to float, so re-type back to int:

    gdf_total_locations_counts['count'] = gdf_total_locations_counts['count'].astype(int)

    # --------------------------------------------------------------------------------------------------

    total_num_locations = gdf_total_locations_counts.shape[0]
    total_num_items_with_locations = gdf_total_locations_counts['count'].sum()

    # If gdf_locations is for regions:
    #     Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
    # If gdf_locations is for LADs:
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_locations_counts['percentage'] = (gdf_total_locations_counts['count'] / total_num_items_with_locations) * 100

    return gdf_total_locations_counts, total_num_locations, total_num_items_with_locations