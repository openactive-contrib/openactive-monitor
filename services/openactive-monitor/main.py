# import difflib
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import pickle
# import re
import seaborn as sns
import streamlit as st
# from datetime import datetime
from os import getenv

# --------------------------------------------------------------------------------------------------

def is_feed_to_include(filename, feeds_to_include='all'):
    return ((feeds_to_include == 'all')
        or  ((feeds_to_include == 'regular') and ('000-preview' not in filename))
        or  ((feeds_to_include == 'preview') and ('000-preview' in filename))
    )

# --------------------------------------------------------------------------------------------------

def get_analyses():
    try:
        with open(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_ANALYSES, 'rb') as file_in:
            analyses = pickle.load(file_in)
        return analyses
    except:
        return None

# --------------------------------------------------------------------------------------------------

def get_total_num_items(analyses, feeds_to_include='all'):
    return sum([
        analysis['num_items']
        for filename, analysis in analyses.items()
        if (is_feed_to_include(filename, feeds_to_include=feeds_to_include))
    ])

# --------------------------------------------------------------------------------------------------

def get_df_total_activities_counts(analyses, feeds_to_include='all'):
    total_activities_counts = {}

    for filename, analysis in analyses.items():
        if (is_feed_to_include(filename, feeds_to_include=feeds_to_include)):
            for activity, count in analysis['activities_counts'].items():
                if (activity not in total_activities_counts.keys()):
                    total_activities_counts[activity] = count
                else:
                    total_activities_counts[activity] += count

    df_total_activities_counts = pd.DataFrame(
        sorted(
            total_activities_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        ),
        columns=['activity', 'count'],
    )

    return df_total_activities_counts

# --------------------------------------------------------------------------------------------------

def get_df_total_coords_counts(analyses, feeds_to_include='all'):
    total_coords_counts = {}

    for filename, analysis in analyses.items():
        if (is_feed_to_include(filename, feeds_to_include=feeds_to_include)):
            for coords, count in analysis['coords_counts'].items():
                if (coords not in total_coords_counts.keys()):
                    total_coords_counts[coords] = count
                else:
                    total_coords_counts[coords] += count

    df_total_coords_counts = pd.DataFrame(
        sorted(
            list(map(
                # lambda coords_count: tuple([float(coord) for coord in coords_count[0].split(',')] + [coords_count[1]]),
                lambda coords_count: tuple(list(map(float, coords_count[0].split(','))) + [coords_count[1]]),
                total_coords_counts.items()
            )),
            key=lambda item: item[2],
            reverse=True,
        ),
        columns=['latitude', 'longitude', 'count'],
    )

    return df_total_coords_counts

# --------------------------------------------------------------------------------------------------

def get_gdf_total_locations_counts(df_total_coords_counts, gdf_locations, gdf_locations_name_column):
    # Columns: ['latitude', 'longitude', 'count', 'geometry']
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
    #     Columns: ['FID', 'RGN23CD', 'RGN23NM', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count']
    # If gdf_locations is 'lads.geojson':
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count']
    gdf_total_locations_counts = \
        gdf_locations \
        .merge(gdf_total_locations_counts, on=gdf_locations_name_column, how='left') \
        .sort_values(by='count', ascending=False) \
        .fillna(0)

    # If gdf_locations is 'regions.geojson':
    #     Columns: ['FID', 'RGN23CD', 'RGN23NM', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    # If gdf_locations is 'lads.geojson':
    #     Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
    gdf_total_locations_counts['percentage'] = round((gdf_total_locations_counts['count'] / gdf_total_locations_counts['count'].sum(skipna=True)) * 100, 1)

    # print('gdf_total_locations_counts:')
    # print(gdf_total_locations_counts)

    return gdf_total_locations_counts

# --------------------------------------------------------------------------------------------------

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

if (not st.session_state):
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
    st.session_state.FILENAME_REGIONS = getenv('FILENAME_REGIONS', 'regions.geojson')
    st.session_state.FILENAME_LADS = getenv('FILENAME_LADS', 'lads.geojson')
    st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE = getenv('FILENAME_SE_SPORT_AND_DISCIPLINE', 'SE-sport-and-discipline.csv')
    st.session_state.FILENAME_OA_SE_MAPPING = getenv('FILENAME_OA_SE_MAPPING', 'OA-SE-mapping.csv')

    print('Environment variables:')
    print('RELATIVE_FILEPATH_ANALYSES:', st.session_state.RELATIVE_FILEPATH_ANALYSES)
    print('FILENAME_ANALYSES:', st.session_state.FILENAME_ANALYSES)
    print('FILENAME_REGIONS:', st.session_state.FILENAME_REGIONS)
    print('FILENAME_LADS:', st.session_state.FILENAME_LADS)
    print('FILENAME_SE_SPORT_AND_DISCIPLINE:', st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE)
    print('FILENAME_OA_SE_MAPPING:', st.session_state.FILENAME_OA_SE_MAPPING)

    # --------------------------------------------------------------------------------------------------

    analyses = get_analyses()

    if (analyses is None):
        st.session_state.error = True
        st.error('Error retrieving analyses data')
    else:
        st.session_state.error = False

        # Even with no parameters given to set_theme(), simply running it empty initialises general Seaborn
        # theming, otherwise we have general Matplotlib theming:
        sns.set_theme(rc={
            # 'figure.figsize': (10, 4),
            'patch.linewidth': 0.0, # Border width around individual bars of a barplot
        })

        # --------------------------------------------------------------------------------------------------

        # For the 'Overview' tab

        st.session_state.num_feeds_regular = len([filename for filename in analyses.keys() if (is_feed_to_include(filename, feeds_to_include='regular'))])
        st.session_state.num_feeds_preview = len([filename for filename in analyses.keys() if (is_feed_to_include(filename, feeds_to_include='preview'))])
        st.session_state.num_feeds = st.session_state.num_feeds_regular + st.session_state.num_feeds_preview

        st.session_state.total_num_items_regular = get_total_num_items(analyses, feeds_to_include='regular')
        st.session_state.total_num_items_preview = get_total_num_items(analyses, feeds_to_include='preview')
        st.session_state.total_num_items = st.session_state.total_num_items_regular + st.session_state.total_num_items_preview

        # --------------------------------------------------------------------------------------------------

        # For the 'Activities' tab

        st.session_state.df_total_activities_counts = get_df_total_activities_counts(analyses, feeds_to_include='all')
        st.session_state.num_activities_top = 20

        # --------------------------------------------------------------------------------------------------

        # For the 'Locations' tab

        # Columns: ['latitude', 'longitude', 'count']
        df_total_coords_counts = get_df_total_coords_counts(analyses, feeds_to_include='all')
        # Columns: ['FID', 'RGN23CD', 'RGN23NM', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry']
        gdf_regions = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_REGIONS)
        # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry']
        gdf_lads = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSES + '/' + st.session_state.FILENAME_LADS)

        # Columns: ['FID', 'RGN23CD', 'RGN23NM', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
        st.session_state.gdf_total_regions_counts = get_gdf_total_locations_counts(df_total_coords_counts, gdf_regions, 'RGN23NM')
        # Columns: ['FID', 'LAD24CD', 'LAD24NM', 'LAD24NMW', 'BNG_E', 'BNG_N', 'LONG', 'LAT', 'GlobalID', 'geometry', 'count', 'percentage']
        st.session_state.gdf_total_lads_counts = get_gdf_total_locations_counts(df_total_coords_counts, gdf_lads, 'LAD24NM')

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
        st.session_state.df_total_sad_counts = pd.merge(st.session_state.df_total_activities_counts, df_oa_se_mapping, how='left')
        st.session_state.df_total_sad_counts['sport_and_discipline'].fillna('No Match', inplace=True)

        # Columns: [('sport_and_discipline', ''), ('activity', '<lambda>'), ('count', 'count'), ('count', 'sum')] # Note that these are MultiIndex columns, each element of a tuple corresponds to a different header row
        st.session_state.df_total_sad_counts = \
            st.session_state.df_total_sad_counts \
            .groupby('sport_and_discipline') \
            .agg({
                'activity': lambda x: '; '.join(list(x)), # Don't join activity labels with commas as the labels may use commas
                'count': ['count', 'sum'], # This is the 'count' column with the 'count' and 'sum' functions applied to it separately, producing two new sub-columns, and hence the MultiIndex output
            }) \
            .sort_values(by=('count', 'sum'), ascending=False) \
            .reset_index()

        total_num_activities = st.session_state.df_total_sad_counts[('count', 'count')].sum() # == len(st.session_state.total_activities_counts.keys())
        total_num_opportunities = st.session_state.df_total_sad_counts[('count', 'sum')].sum() # == sum(st.session_state.total_activities_counts.values())

        st.session_state.df_total_sad_counts[('count', f'% of activities')] = round((st.session_state.df_total_sad_counts[('count', 'count')] / total_num_activities) * 100, 1)
        st.session_state.df_total_sad_counts[('count', f'% of opportunities')] = round((st.session_state.df_total_sad_counts[('count', 'sum')] / total_num_opportunities) * 100, 1)

        st.session_state.df_total_sad_counts.columns = [
            'sport_and_discipline',
            'activity',
            f'No. activities (/{total_num_activities})',
            f'No. opportunities (/{total_num_opportunities})',
            f'% activities',
            f'% opportunities',
        ]

        st.session_state.num_sad_se = df_se_sport_and_discipline['sport_and_discipline'].count()
        st.session_state.num_sad_matched = st.session_state.df_total_sad_counts['sport_and_discipline'].count()
        st.session_state.num_sad_unmatched = st.session_state.num_sad_se - st.session_state.num_sad_matched
        st.session_state.percentage_sad_matched = round((st.session_state.num_sad_matched / st.session_state.num_sad_se) * 100, 1)

        st.session_state.df_se_sport_and_discipline_unmatched = df_se_sport_and_discipline[
            ~df_se_sport_and_discipline['sport_and_discipline'] \
            .isin(st.session_state.df_total_sad_counts['sport_and_discipline'])
        ]

# --------------------------------------------------------------------------------------------------

if (not st.session_state.error):
    tabs = st.tabs(['Overview', 'This week', 'Activities', 'Locations', 'KPIs'])

    with tabs[0]:
        st.header('Overview of the OpenActive data ecosystem')

        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric('Number of live OpenActive feeds', st.session_state.num_feeds)
        with col2:
            st.metric('Number of live OpenActive opportunities', f'{st.session_state.total_num_items:,}')

        st.write(f'These figures include {st.session_state.num_feeds_preview} preview feeds with {round(st.session_state.total_num_items_preview / 1000000, 1)}m preview opportunities')

        # dated_counts = {
        #     'Jan 17': 0,
        #     'Jul 17': 80000,
        #     'Jan 18': 80000,
        #     'Jul 18': 110000,
        #     'Jan 19': 160000,
        #     'Jun 19': 200000,
        # }

        # current_month = datetime.now().strftime('%b %y')
        # dated_counts[current_month] = st.session_state.total_num_items
        # df = pd.DataFrame.from_dict(dated_counts, orient='index', columns=['Count'])
        # df.reset_index(inplace=True)
        # df.columns = ['Date', 'Count']
        # df['Date'] = pd.to_datetime(df['Date'], format='%b %y')
        # df = df.sort_values(by='Date')

        # st.line_chart(df, x='Date', y='Count')

    # --------------------------------------------------------------------------------------------------

    with tabs[1]:
        st.header('OpenActive opportunities over the next 7 days')

    # --------------------------------------------------------------------------------------------------

    with tabs[2]:
        st.header('Most popular OpenActive activities')

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(
                '<div style="text-align: center;">All activities</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(
                st.session_state.df_total_activities_counts,
                use_container_width=True,
                hide_index=True,
            )
        with col2:
            st.markdown(
                f'<div style="text-align: center;">Top {st.session_state.num_activities_top} activities</div>',
                unsafe_allow_html=True,
            )
            fig, ax = plt.subplots(1, 1, figsize=(10, 5))
            sns.barplot(
                st.session_state.df_total_activities_counts[:st.session_state.num_activities_top],
                x='count',
                y='activity',
                ax=ax,
            )
            ax.bar_label(ax.containers[0], fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

    # --------------------------------------------------------------------------------------------------

    with tabs[3]:
        st.header('OpenActive opportunities by location')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.dataframe(
                st.session_state.gdf_total_regions_counts[['RGN23NM', 'count', 'percentage']].set_index('RGN23NM'),
                use_container_width=True,
            )
        with col2:
            fig, ax = plt.subplots(1, 1, figsize=(5, 5))
            st.session_state.gdf_total_regions_counts.plot(
                column='percentage',
                cmap='YlOrRd',
                legend=True,
                ax=ax,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            st.pyplot(fig)
            plt.close(fig)
        with col3:
            st.dataframe(
                st.session_state.gdf_total_lads_counts[['LAD24NM', 'count', 'percentage']].set_index('LAD24NM'),
                use_container_width=True,
            )
        with col4:
            fig, ax = plt.subplots(1, 1, figsize=(5, 5))
            st.session_state.gdf_total_lads_counts.plot(
                column='percentage',
                cmap='YlOrRd',
                legend=True,
                ax=ax,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            st.pyplot(fig)
            plt.close(fig)

    # --------------------------------------------------------------------------------------------------

    with tabs[4]:
        st.header(f'KPI 2.1.1 - {st.session_state.percentage_sad_matched}% of Sport England activities found in OpenActive data')

        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f'Matched: {st.session_state.num_sad_matched} of {st.session_state.num_sad_se} sports and disciplines')
            st.dataframe(st.session_state.df_total_sad_counts, hide_index=True)
        with col2:
            st.write(f'Unmatched: {st.session_state.num_sad_unmatched} of {st.session_state.num_sad_se} sports and disciplines')
            st.dataframe(st.session_state.df_se_sport_and_discipline_unmatched[['sport', 'discipline']], hide_index=True)