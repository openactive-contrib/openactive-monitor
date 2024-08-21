import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import pickle
import random
import seaborn as sns
import streamlit as st
from datetime import datetime
from millify import millify
from os import getenv

# --------------------------------------------------------------------------------------------------

# st.set_page_config must be the first Streamlit command if it is present at all:

st.set_page_config(
    page_title='OpenActive',
    page_icon='https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png',
    layout='wide',
    menu_items={
        'Get help': 'mailto:hello@openactive.io',
        'About': 'Copyright 2024 OpenActive',
    }
)

# --------------------------------------------------------------------------------------------------

# Set custom styles before doing anything else, as they can take a short while to load and can cause
# twitchy behaviour if done later:

if ('style' not in st.session_state):
    with open('style.css', 'r') as file_in:
        st.session_state.style = file_in.read()

    # Even with no parameters given to set_theme(), simply running it empty initialises general Seaborn
    # theming, otherwise we have general Matplotlib theming:
    sns.set_theme(rc={
        # 'figure.figsize': (10, 4),
        'patch.linewidth': 0.0, # Border width around individual bars of a barplot
    })

st.html(f'''
    <style>
        {st.session_state.style}
    </style>
''')

# --------------------------------------------------------------------------------------------------

def is_feed_to_include(filename, feeds_to_include='all'):
    return ((feeds_to_include == 'all')
        or  ((feeds_to_include == 'regular') and ('000-preview' not in filename))
        or  ((feeds_to_include == 'preview') and ('000-preview' in filename))
    )

# --------------------------------------------------------------------------------------------------

def get_analyses(filename):
    try:
        with open(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + filename, 'rb') as file_in:
            analyses = pickle.load(file_in)
        return analyses
    except:
        return None

# --------------------------------------------------------------------------------------------------

def get_total_num_opportunities(analyses, feeds_to_include='all'):
    return sum([
        analysis['num_items']
        for filename, analysis in analyses.items()
        if (is_feed_to_include(filename, feeds_to_include=feeds_to_include))
    ])

# --------------------------------------------------------------------------------------------------

def get_df_total_keys_counts(analyses, keys_counts, feeds_to_include='all'):
    total_keys_counts = {}

    for filename, analysis in analyses.items():
        if (is_feed_to_include(filename, feeds_to_include=feeds_to_include)):
            for key, count in analysis[keys_counts].items():
                if (key not in total_keys_counts.keys()):
                    total_keys_counts[key] = count
                else:
                    total_keys_counts[key] += count

    if (keys_counts == 'activities_counts'):
        columns = ['activity', 'count']
        # with open(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + 'total_activities_counts.pickle', 'wb') as file_out:
        #     pickle.dump(total_keys_counts, file_out)
    elif (keys_counts == 'coords_counts'):
        columns = ['coords', 'count']
        # with open(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + 'total_coords_counts.pickle', 'wb') as file_out:
        #     pickle.dump(total_keys_counts, file_out)

    df_total_keys_counts = pd.DataFrame(
        sorted(
            total_keys_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        ),
        columns=columns,
    )

    total_num_keys = df_total_keys_counts.shape[0]
    total_num_opportunities_with_keys = df_total_keys_counts['count'].sum()

    df_total_keys_counts['percentage'] = (df_total_keys_counts['count'] / total_num_opportunities_with_keys) * 100

    # print(f'df_total_keys_counts ({keys_counts}):')
    # print(df_total_keys_counts)

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

# This version of get_value() focuses on the parent key for logic branching, whereas the new version
# focuses on the child key, and which seems more natural and simpler. Temporarily keeping this initial
# version just in case of need to revert back.

# def get_value(data, key_to_find, parent_key=None, continue_to_next_layer=True):
#     if (isinstance(key_to_find, str)):
#         key_to_find = [key_to_find]

#     if (isinstance(data, dict)):
#         value = None
#         for key, val in data.items():
#             if (parent_key is not None):
#                 if (key == parent_key):
#                     return get_value(val, key_to_find, continue_to_next_layer=False)
#                 else:
#                     value = get_value(val, key_to_find, parent_key=parent_key)
#             else:
#                 if (key in key_to_find):
#                     return val
#                 elif (continue_to_next_layer):
#                     value = get_value(val, key_to_find)
#             if (value is not None):
#                 return value

#     if (isinstance(data, list)):
#         values = [get_value(i, key_to_find, parent_key=parent_key) for i in data]
#         values = [value for value in values if (value is not None)]
#         if (values):
#             return values

#     return None

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

def parse_date(date_string):
    if (isinstance(date_string, list)):
        date_string = date_string[0]

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
            formatted_date = parsed_datetime.strftime('%a %d %b %I%p').replace(' 0', ' ')
            return formatted_date
        except:
            pass

    return date_string

# --------------------------------------------------------------------------------------------------

def set_opportunities_sample():
    st.session_state.opportunities_sample = []

    # Select some random feeds, and for each of them get a single random item from this week's sample:
    random_filenames_with_opportunities_sample = random.sample(
        st.session_state.filenames_with_opportunities_sample,
        min(st.session_state.num_filenames_with_opportunities_sample,
            st.session_state.max_num_random_filenames_with_opportunities_sample
        )
    )

    for filename in random_filenames_with_opportunities_sample:
        item = random.choice(list(st.session_state.analyses_this_week[filename]['items_sample'].values()))
        info = {
            'filename': filename,
            'id': get_value(item, 'id'),
            'kind': get_value(item, 'kind'),
            'type': get_value(item, 'data', ['type', '@type']),
            'name': get_value(item, 'data', 'name'),
            'url': get_value(item, 'data', 'url'),
            'description': get_value(item, 'data', 'description'),
            'activities': get_value(item, 'activity', 'prefLabel'),
            'startdate': parse_date(get_value(item, 'startDate')),
            'duration': get_value(item, 'duration'),
            'min_age': get_value(item, 'ageRange', 'minValue'),
            'max_age': get_value(item, 'ageRange', 'maxValue'),
            'offer_name': get_value(item, 'offers', 'name'),
            'offer_url': get_value(item, 'offers', 'url'),
            'offer_price': get_value(item, 'offers', 'price'),
            'offer_currency': get_value(item, 'offers', 'priceCurrency'),
            'organiser_name': get_value(item, 'organizer', 'name'),
            'organiser_url': get_value(item, 'organizer', 'url'),
            'organiser_email': get_value(item, 'organizer', 'email'),
            'organiser_telephone': get_value(item, 'organizer', 'telephone'),
            'location_name': get_value(item, 'location', 'name'),
            'location_url': get_value(item, 'location', 'url'),
            'location_email': get_value(item, 'location', 'email'),
            'location_telephone': get_value(item, 'location', 'telephone'),
            'address': get_value(item, 'address', 'streetAddress'),
            'postcode': get_value(item, 'address', 'postalCode'),
            'latitude': get_value(item, 'geo', 'latitude'),
            'longitude': get_value(item, 'geo', 'longitude'),
            'image': get_value(item, 'logo', 'url'),
        }
        st.session_state.opportunities_sample.append((item, info))

# --------------------------------------------------------------------------------------------------

if ('initialised' not in st.session_state):
    # These folders must have been made via the Google Cloud browser console under Cloud Storage for this
    # project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
    # this service called 'openactive-monitor', this was done as follows (note that the volume and its mount-path
    # were given the same name, which didn't have to be so):
    #   $ gcloud beta run services update openactive-monitor \
    #   --region europe-west2 \
    #   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
    #   --add-volume-mount volume=volume-1,mount-path=/volume-1
    st.session_state.RELATIVE_FILEPATH_ANALYSES = getenv('RELATIVE_FILEPATH_ANALYSES', '../volume-1/data-analysis')

    st.session_state.FILENAME_ANALYSES = getenv('FILENAME_ANALYSES', 'analysis.pickle')
    st.session_state.FILENAME_ANALYSES_THIS_WEEK = getenv('FILENAME_ANALYSES_THIS_WEEK', 'analyses-this-week.pickle')
    st.session_state.FILENAME_REGIONS = getenv('FILENAME_REGIONS', 'regions.geojson')
    st.session_state.FILENAME_LADS = getenv('FILENAME_LADS', 'lads.geojson')
    st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE = getenv('FILENAME_SE_SPORT_AND_DISCIPLINE', 'SE-sport-and-discipline.csv')
    st.session_state.FILENAME_OA_SE_MAPPING = getenv('FILENAME_OA_SE_MAPPING', 'OA-SE-mapping.csv')

    print('Environment variables:')
    print('RELATIVE_FILEPATH_ANALYSES:', st.session_state.RELATIVE_FILEPATH_ANALYSES)
    print('FILENAME_ANALYSES:', st.session_state.FILENAME_ANALYSES)
    print('FILENAME_ANALYSES_THIS_WEEK:', st.session_state.FILENAME_ANALYSES_THIS_WEEK)
    print('FILENAME_REGIONS:', st.session_state.FILENAME_REGIONS)
    print('FILENAME_LADS:', st.session_state.FILENAME_LADS)
    print('FILENAME_SE_SPORT_AND_DISCIPLINE:', st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE)
    print('FILENAME_OA_SE_MAPPING:', st.session_state.FILENAME_OA_SE_MAPPING)

    # --------------------------------------------------------------------------------------------------

    st.session_state.analyses = get_analyses(st.session_state.FILENAME_ANALYSES)
    st.session_state.analyses_this_week = get_analyses(st.session_state.FILENAME_ANALYSES_THIS_WEEK)

    if (    (st.session_state.analyses is None)
        or  (st.session_state.analyses_this_week is None)
    ):
        st.session_state.error = True
        st.error('Error retrieving data')
    else:
        st.session_state.error = False

        # --------------------------------------------------------------------------------------------------

        # For the 'Overview' tab

        # TODO: Remove use of .get once the new type of opportunities dictionary with 'feed' is fully established

        st.session_state.num_publishers_regular = len(set([
            analysis['feed']['publisherName']
            for filename, analysis in st.session_state.analyses.items()
            if (    (is_feed_to_include(filename, feeds_to_include='regular'))
                and (analysis.get('feed', None) is not None)
            )
        ]))
        st.session_state.num_publishers_preview = len(set([
            analysis['feed']['publisherName']
            for filename, analysis in st.session_state.analyses.items()
            if (    (is_feed_to_include(filename, feeds_to_include='preview'))
                and (analysis.get('feed', None) is not None)
            )
        ]))
        st.session_state.num_publishers = st.session_state.num_publishers_regular + st.session_state.num_publishers_preview

        st.session_state.num_datasets_regular = len(set([
            analysis['feed']['datasetUrl']
            for filename, analysis in st.session_state.analyses.items()
            if (    (is_feed_to_include(filename, feeds_to_include='regular'))
                and (analysis.get('feed', None) is not None)
            )
        ]))
        st.session_state.num_datasets_preview = len(set([
            analysis['feed']['datasetUrl']
            for filename, analysis in st.session_state.analyses.items()
            if (    (is_feed_to_include(filename, feeds_to_include='preview'))
                and (analysis.get('feed', None) is not None)
            )
        ]))
        st.session_state.num_datasets = st.session_state.num_datasets_regular + st.session_state.num_datasets_preview

        st.session_state.num_feeds_regular = len([filename for filename in st.session_state.analyses.keys() if (is_feed_to_include(filename, feeds_to_include='regular'))])
        st.session_state.num_feeds_preview = len([filename for filename in st.session_state.analyses.keys() if (is_feed_to_include(filename, feeds_to_include='preview'))])
        st.session_state.num_feeds = st.session_state.num_feeds_regular + st.session_state.num_feeds_preview

        st.session_state.total_num_opportunities_regular = get_total_num_opportunities(st.session_state.analyses, feeds_to_include='regular')
        st.session_state.total_num_opportunities_preview = get_total_num_opportunities(st.session_state.analyses, feeds_to_include='preview')
        st.session_state.total_num_opportunities = st.session_state.total_num_opportunities_regular + st.session_state.total_num_opportunities_preview

        # --------------------------------------------------------------------------------------------------

        # For the 'This week' tab

        st.session_state.total_num_opportunities_this_week_regular = get_total_num_opportunities(st.session_state.analyses_this_week, feeds_to_include='regular')
        st.session_state.total_num_opportunities_this_week_preview = get_total_num_opportunities(st.session_state.analyses_this_week, feeds_to_include='preview')
        st.session_state.total_num_opportunities_this_week = st.session_state.total_num_opportunities_this_week_regular + st.session_state.total_num_opportunities_this_week_preview

        st.session_state.filenames_with_opportunities_sample = [
            filename
            for filename in st.session_state.analyses_this_week.keys()
            if (st.session_state.analyses_this_week[filename]['num_items_sample'] > 0)
        ]

        st.session_state.num_filenames_with_opportunities_sample = len(st.session_state.filenames_with_opportunities_sample)
        st.session_state.max_num_random_filenames_with_opportunities_sample = 5
        set_opportunities_sample()

        # --------------------------------------------------------------------------------------------------

        # For the 'Activities' tab

        # Columns: ['activity', 'count', 'percentage']
        st.session_state.df_total_activities_counts, \
        st.session_state.total_num_activities, \
        st.session_state.total_num_opportunities_with_activities = get_df_total_keys_counts(st.session_state.analyses, 'activities_counts', feeds_to_include='all')

        st.session_state.num_activities_top = 20

        # --------------------------------------------------------------------------------------------------

        # For the 'Locations' tab

        # Columns: ['coords', 'count', 'percentage']
        st.session_state.df_total_coords_counts, \
        st.session_state.total_num_coords, \
        st.session_state.total_num_opportunities_with_coords = get_df_total_keys_counts(st.session_state.analyses, 'coords_counts', feeds_to_include='all')
        # Columns: ['coords', 'count', 'percentage', 'latitude', 'longitude']
        st.session_state.df_total_coords_counts[['latitude', 'longitude']] = pd.DataFrame(st.session_state.df_total_coords_counts['coords'].apply(lambda coords: coords.split(',')).tolist())
        # Columns: ['latitude', 'longitude', 'count', 'percentage']
        st.session_state.df_total_coords_counts = st.session_state.df_total_coords_counts[['latitude', 'longitude', 'count', 'percentage']]

        # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry']
        gdf_regions = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_REGIONS)

        # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry']
        gdf_lads = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_LADS)

        # Columns: ['OBJECTID', 'eer18cd', 'eer18nm', 'bng_e', 'bng_n', 'long', 'lat', 'GlobalID', 'geometry', 'count', 'percentage']
        st.session_state.gdf_total_regions_counts, \
        st.session_state.total_num_regions, \
        st.session_state.total_num_opportunities_with_regions = get_gdf_total_locations_counts(st.session_state.df_total_coords_counts, gdf_regions, 'eer18nm')

        # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
        st.session_state.gdf_total_lads_counts, \
        st.session_state.total_num_lads, \
        st.session_state.total_num_opportunities_with_lads = get_gdf_total_locations_counts(st.session_state.df_total_coords_counts, gdf_lads, 'LAD24NM')

        # --------------------------------------------------------------------------------------------------

        # For the 'KPIs' tab

        # Columns: ['sport', 'discipline', 'sport_and_discipline']
        df_se_sport_and_discipline = pd.read_csv(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE)
        # Columns: ['activity', 'sport_and_discipline']
        df_oa_se_mapping = pd.read_csv(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_OA_SE_MAPPING)

        # Automatically update the mapping file if confident in the handling of incoming activity labels i.e.
        # if the names have been stripped of junk and formatted in a compatible way, otherwise we'll potentially
        # get unmatched repetition e.g. 'kettlebells' may have a match, but a new entry 'kettlebells\r\n' will
        # not. Currently commenting this out as it could pollute the mapping file if not done right, instead
        # relying on the dataframe merge below with no matches resulting in NaN, which can be changed to 'No Match'
        # here in code. This means that the code may produce mistakes on-the-fly depending on the full chain
        # of data handling choices, but at least they won't be hard-wired into the mapping file:

        # df_oa_se_mapping_additions = \
        #     st.session_state.df_total_activities_counts[~st.session_state.df_total_activities_counts['activity'].isin(df_oa_se_mapping['activity'])] \
        #     .copy() \
        #     .drop(columns=['count']) \
        #     .assign(sport_and_discipline='No Match') \
        #     .reset_index(drop=True)

        # df_oa_se_mapping = \
        #     pd.concat([df_oa_se_mapping, df_oa_se_mapping_additions]) \
        #     .sort_values(by='activity') \
        #     .reset_index(drop=True)

        # df_oa_se_mapping.to_csv(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_OA_SE_MAPPING)

        # Columns: ['activity', 'count', 'sport_and_discipline']
        st.session_state.df_total_sad_counts = pd.merge(
            st.session_state.df_total_activities_counts.drop(columns=['percentage']).assign(activity=lambda x: x['activity'].str.strip()),
            df_oa_se_mapping, how='left')
        # Pull out non matching activities before they are changed to 'No Match':
        st.session_state.df_total_sad_na = st.session_state.df_total_sad_counts.loc[st.session_state.df_total_sad_counts['sport_and_discipline'].isna()]
        # TODO: This file is written out on each page load, is it needed?
        st.session_state.df_total_sad_na.to_csv(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + 'unmatched_activities.csv', index=False)
        print("Activities not matched to SE Sports and Disciplines saved to 'unmatched_activities.csv'")
        st.session_state.df_total_sad_counts['sport_and_discipline'].fillna('No Match', inplace=True)

        st.session_state.df_total_sad_counts_matched = st.session_state.df_total_sad_counts.loc[st.session_state.df_total_sad_counts['sport_and_discipline'] != 'No Match']
        st.session_state.df_total_sad_counts_unmatched = st.session_state.df_total_sad_counts.loc[st.session_state.df_total_sad_counts['sport_and_discipline'] == 'No Match']

        # Note that after this operation we have MultiIndex columns, where each element of a tuple corresponds
        # to a different header row:
        # Columns: [('sport_and_discipline', ''), ('activity', '<lambda>'), ('count', 'count'), ('count', 'sum')]
        st.session_state.df_total_sad_counts_matched = \
            st.session_state.df_total_sad_counts_matched \
            .groupby('sport_and_discipline') \
            .agg({
                'activity': lambda x: '; '.join(list(x)), # Don't join activity labels with commas as the labels may use commas
                'count': ['count', 'sum'], # This is the 'count' column with the 'count' and 'sum' functions applied to it separately, producing two new sub-columns, and hence the MultiIndex output
            }) \
            .sort_values(by=('count', 'sum'), ascending=False) \
            .reset_index()

        # Compact to single index columns for simplicity, also because Streamlit can't display MultiIndex columns:
        # Columns: ['sport_and_discipline', 'activity', 'count_activities', 'count_opportunities']
        st.session_state.df_total_sad_counts_matched.columns = [
            'sport_and_discipline',
            'activity',
            'count_activities',
            'count_opportunities',
        ]

        # Columns: ['sport_and_discipline', 'activity', 'count']
        st.session_state.df_total_sad_counts_unmatched = st.session_state.df_total_sad_counts_unmatched[['sport_and_discipline', 'activity', 'count']]
        # Rename columns for consistency with df_total_sad_counts_matched, even though there's only one count here:
        # Columns: ['sport_and_discipline', 'activity', 'count_opportunities']
        st.session_state.df_total_sad_counts_unmatched.columns = [
            'sport_and_discipline',
            'activity',
            'count_opportunities',
        ]

        st.session_state.total_num_activities_with_sad = st.session_state.df_total_sad_counts_matched['count_activities'].sum()
        st.session_state.total_num_activities_without_sad = st.session_state.df_total_sad_counts_unmatched.shape[0]
        st.session_state.total_num_opportunities_with_sad = st.session_state.df_total_sad_counts_matched['count_opportunities'].sum()
        st.session_state.total_num_opportunities_without_sad = st.session_state.df_total_sad_counts_unmatched['count_opportunities'].sum()

        # Columns: ['sport_and_discipline', 'activity', 'count_activities', 'count_opportunities', 'percentage_activities', 'percentage_opportunities']
        st.session_state.df_total_sad_counts_matched['percentage_activities'] = (st.session_state.df_total_sad_counts_matched['count_activities'] / st.session_state.total_num_activities_with_sad) * 100
        st.session_state.df_total_sad_counts_matched['percentage_opportunities'] = (st.session_state.df_total_sad_counts_matched['count_opportunities'] / st.session_state.total_num_opportunities_with_sad) * 100

        # Columns: ['sport_and_discipline', 'activity', 'count_opportunities', 'percentage_opportunities']
        st.session_state.df_total_sad_counts_unmatched['percentage_opportunities'] = (st.session_state.df_total_sad_counts_unmatched['count_opportunities'] / st.session_state.total_num_opportunities_without_sad) * 100

        st.session_state.num_sad = df_se_sport_and_discipline['sport_and_discipline'].count()
        st.session_state.num_sad_matched = st.session_state.df_total_sad_counts_matched['sport_and_discipline'].count()
        st.session_state.num_sad_unmatched = st.session_state.num_sad - st.session_state.num_sad_matched
        st.session_state.percentage_sad_matched = (st.session_state.num_sad_matched / st.session_state.num_sad) * 100
        st.session_state.percentage_sad_unmatched = 100 - st.session_state.percentage_sad_matched

        st.session_state.df_se_sport_and_discipline_unmatched = df_se_sport_and_discipline.loc[
            ~df_se_sport_and_discipline['sport_and_discipline'] \
            .isin(st.session_state.df_total_sad_counts_matched['sport_and_discipline'])
        ]

    # --------------------------------------------------------------------------------------------------

    st.session_state.initialised = True

# --------------------------------------------------------------------------------------------------

if (    ('error' in st.session_state)
    and (not st.session_state.error)
):
    tabs = st.tabs(['Overview', 'This week', 'Activities', 'Locations', 'KPIs'])

    with tabs[0]:
        cols = st.columns([1, 1, 2])
        with cols[0]:
            st.metric(
                'Publishers',
                f'{st.session_state.num_publishers:,}',
                help='OpenActive is a decentralised open data initiative. Each data publisher shares one or more data sets, each with one or more data feeds, providing near real time availability of their activities and facilities.',
            )
            st.metric(
                'Data sets',
                f'{st.session_state.num_datasets:,}',
            )
            st.metric(
                'Data feeds',
                f'{st.session_state.num_feeds:,}',
            )
            st.metric(
                'Activities and facilities',
                f'{st.session_state.total_num_activities:,}',
                help='While the official OpenActive activity list contains over 700 standardised activity names, publishers can and do use their own wording for activity and facility names.',
            )
            st.metric(
                'Live opportunities',
                millify(st.session_state.total_num_opportunities, precision=1),
                help='OpenActive describes standards to make sharing information about "opportunities for sport and physical activity" easier and more effective. We use the word "opportunity" to describe the individual items or records that are contained in data feeds. Because the feeds vary in level of detail they represent, the total "opportunity" count is quite a crude measure. But generally, an increase in total opportunities shows that more activity and facility data is being made open, and we think that is a good thing!',
            )
        with cols[1]:
            fig, ax = plt.subplots(1, 1, figsize=(5, 10))
            plt.style.use('ggplot')
            st.session_state.gdf_total_regions_counts.plot(
                column='percentage',
                # cmap='YlOrRd',
                cmap='inferno_r',
                ax=ax,
            )
            ax.set(facecolor='white')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title('% of OpenActive Opportunities by Region')
            scalarmappable = ax.collections[0] # Assuming there's only one collection in the plot
            colorbar = plt.colorbar(scalarmappable, orientation='horizontal', pad=-0.04)
            colorbar.set_label('%')
            st.pyplot(fig)
            plt.close(fig)

        st.write(f'These figures include data from {st.session_state.num_feeds_preview} preview feeds with {millify(st.session_state.total_num_opportunities_preview, precision=1)} preview opportunities.')
        st.write(f'This snapshot of the OpenActive ecosystem was created on {datetime.now().date()}.')

        # dated_counts = {
        #     'Jan 17': 0,
        #     'Jul 17': 80000,
        #     'Jan 18': 80000,
        #     'Jul 18': 110000,
        #     'Jan 19': 160000,
        #     'Jun 19': 200000,
        # }

        # current_month = datetime.now().strftime('%b %y')
        # dated_counts[current_month] = st.session_state.total_num_opportunities
        # df = pd.DataFrame.from_dict(dated_counts, orient='index', columns=['Count'])
        # df.reset_index(inplace=True)
        # df.columns = ['Date', 'Count']
        # df['Date'] = pd.to_datetime(df['Date'], format='%b %y')
        # df = df.sort_values(by='Date')

        # st.line_chart(df, x='Date', y='Count')

    # --------------------------------------------------------------------------------------------------

    def display_map(location_data:pd.DataFrame):
        fig = px.scatter_mapbox(location_data, lat="latitude", lon="longitude", zoom=5)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig

    with tabs[1]:
        st.header('OpenActive opportunities over the next 7 days')

        cols = st.columns(3)
        with cols[1]:
            st.metric(
                'Live opportunities over the next 7 days',
                f'{st.session_state.total_num_opportunities_this_week:,}',
            )

        st.divider()

        st.subheader('Example OpenActive opportunities')
        st.button(
                'Show some more examples',
                type='primary',
                on_click=set_opportunities_sample,
            )

        for idx_col, col in enumerate(st.columns(5)):
            with col:
                opportunity = st.session_state.opportunities_sample[idx_col]
                # TODO: Why convert to a dataframe? This will always have only one row ...
                df_opportunity = pd.DataFrame([
                    {
                        'name': opportunity[1]['name'],
                        'offer_name': opportunity[1]['offer_name'],
                        'description': opportunity[1]['description'],
                        'startdate': opportunity[1]['startdate'],
                        'type': f"({opportunity[1]['type']})",
                        'activity': opportunity[1]['activities'],
                    }
                ])
                opp_image = opportunity[1]['image']
                if isinstance(opportunity[1]['activities'], list):
                    opp_activity = opportunity[1]['activities'][0]
                else:
                    opp_activity = opportunity[1]['activities']
                if isinstance(opportunity[1]['offer_name'], list):
                    opp_offer= opportunity[1]['offer_name'][0]
                else:
                    opp_offer= opportunity[1]['offer_name']
                opp_startdate = opportunity[1]['startdate']
                opp_type = f"({opportunity[1]['type']})"
                
                if opportunity[1]['latitude'] != None:
                    px_map = display_map(opportunity)
                    st.plotly_chart(px_map, use_container_width=True)
                    
                st.html(f'''<div class="opportunity-card">
                        <img src={opp_image} alt=""</img>
                        <table>
                            {''.join([f'<tr><td style="text-align: left;">{key}</td></tr>' for key in [opp_activity, opp_offer, opp_startdate,opp_type] if not isinstance(key, type(None))])}
                        </table>
                        </div>
                ''')


    # --------------------------------------------------------------------------------------------------

    with tabs[2]:
        st.header('OpenActive opportunities by activity')

        cols = st.columns([1, 2])
        with cols[0]:
            st.dataframe(
                st.session_state.df_total_activities_counts,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'activity': 'OA activity',
                    'count': 'Num. opportunities',
                    'percentage': st.column_config.NumberColumn(
                        '% opportunities',
                        format='%0.1f',
                    ),
                },
            )
            st.write(f'Num. activities: {st.session_state.total_num_activities:,}')
            st.write(f'Num. opportunities: {st.session_state.total_num_opportunities_with_activities:,}')
        with cols[1]:
            fig, ax = plt.subplots(1, 1, figsize=(10, 5))
            sns.barplot(
                st.session_state.df_total_activities_counts[:st.session_state.num_activities_top],
                x='count',
                y='activity',
                ax=ax,
            )
            ax.set_xlabel('Num. opportunities')
            ax.set_ylabel('OA activity')
            ax.set_title(f'Top {st.session_state.num_activities_top} live OA activities')
            ax.bar_label(ax.containers[0], fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

    # --------------------------------------------------------------------------------------------------

    with tabs[3]:
        st.header('OpenActive opportunities by location')

        cols = st.columns(3)
        with cols[0]:
            st.dataframe(
                st.session_state.gdf_total_regions_counts[['eer18nm', 'count', 'percentage']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'eer18nm': 'Location',
                    'count': 'Num. opportunities',
                    'percentage': st.column_config.NumberColumn(
                        '% opportunities',
                        format='%0.1f',
                    ),
                },
            )
            st.write(f'Num. locations: {st.session_state.total_num_regions:,}')
            st.write(f'Num. opportunities: {st.session_state.total_num_opportunities_with_regions:,}')
        with cols[1]:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            st.session_state.gdf_total_regions_counts.plot(
                column='percentage',
                # cmap='YlOrRd',
                cmap='inferno_r',
                legend=True,
                ax=ax,
            )
            ax.set(facecolor='white')
            ax.set_xticks([])
            ax.set_yticks([])
            st.pyplot(fig)
            plt.close(fig)

        st.divider()

        cols = st.columns(3)
        with cols[0]:
            st.dataframe(
                st.session_state.gdf_total_lads_counts[['LAD24NM', 'count', 'percentage']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'LAD24NM': 'Location',
                    'count': 'Num. opportunities',
                    'percentage': st.column_config.NumberColumn(
                        '% opportunities',
                        format='%0.1f',
                    ),
                },
            )
            st.write(f'Num. locations: {st.session_state.total_num_lads:,}')
            st.write(f'Num. opportunities: {st.session_state.total_num_opportunities_with_lads:,}')
        with cols[1]:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            st.session_state.gdf_total_lads_counts.plot(
                column='percentage',
                # cmap='YlOrRd',
                cmap='inferno_r',
                legend=True,
                ax=ax,
            )
            ax.set(facecolor='white')
            ax.set_xticks([])
            ax.set_yticks([])
            st.pyplot(fig)
            plt.close(fig)

    # --------------------------------------------------------------------------------------------------

    with tabs[4]:
        st.header('Key Performance Indicators')

        st.subheader('Growth of OpenActive')
        st.subheader(f'{st.session_state.percentage_sad_matched:.1f}% of Sport England recognised Sports and Disciplines appear in OpenActive data feeds')
        with st.expander('A higher value means more of the sports and disciplines recognised by Sport England are discoverable through the OpenActive ecosystem. Click here for more details.'):
            cols = st.columns([2, 1])
            with cols[0]:
                st.write(f'Matched SE categories: {st.session_state.num_sad_matched} / {st.session_state.num_sad} ({st.session_state.percentage_sad_matched:.1f}%)')
                st.dataframe(
                    st.session_state.df_total_sad_counts_matched,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'sport_and_discipline': 'SE sport and discipline',
                        'activity': st.column_config.TextColumn(
                            'OA activity',
                            width='small',
                        ),
                        'count_activities': 'Num. activities',
                        'count_opportunities': 'Num. opportunities',
                        'percentage_activities': st.column_config.NumberColumn(
                            '% activities',
                            format='%0.1f',
                        ),
                        'percentage_opportunities': st.column_config.NumberColumn(
                            '% opportunities',
                            format='%0.1f',
                        ),
                    },
                )
                st.write(f'Num. activities: {st.session_state.total_num_activities_with_sad:,}')
                st.write(f'Num. opportunities: {st.session_state.total_num_opportunities_with_sad:,}')
            with cols[1]:
                st.write(f'Unmatched SE categories: {st.session_state.num_sad_unmatched} / {st.session_state.num_sad} ({st.session_state.percentage_sad_unmatched:.1f}%)')
                st.dataframe(
                    st.session_state.df_se_sport_and_discipline_unmatched[['sport', 'discipline']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'sport': 'SE sport',
                        'discipline': 'SE discipline',
                    }
                )

            st.divider()
            st.write('Activities - Activities featured as individual concepts in the [OpenActive Activity List](https://activity-list.openactive.io/en/hierarchical_concepts.html).')
            st.write('Sports - Sports featured in the list of national governing bodies recognised by the UK Sports Councils. Taken in spreadsheet format from the [Sport England website](https://www.sportengland.org/guidance-and-support/national-governing-bodies?section=recognised_ngbs) and last accessed on 2024-01-24.')
            st.write('Disciplines - Disciplines featured within each of the recognised sports. For example: "crown", "federation", and "short mat" are all distinct disciplines of bowls.')
            st.divider()

            # st.write('Unmatched OA activities')
            # st.dataframe(
            #     st.session_state.df_total_sad_counts_unmatched,
            #     hide_index=True,
            #     column_config={
            #         'sport_and_discipline': 'SE sport and discipline',
            #         'activity': 'OA activity',
            #         'count_opportunities': 'Num. opportunities',
            #         'percentage_opportunities': st.column_config.NumberColumn(
            #             '% opportunities',
            #             format='%0.1f',
            #         ),
            #     },
            # )
            # st.write(f'Num. activities: {st.session_state.total_num_activities_without_sad:,}')
            # st.write(f'Num. opportunities: {st.session_state.total_num_opportunities_without_sad:,}')