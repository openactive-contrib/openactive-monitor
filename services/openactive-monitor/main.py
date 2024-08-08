# import difflib
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import random
# import re
import seaborn as sns
import streamlit as st
# from datetime import datetime
from os import getenv

# --------------------------------------------------------------------------------------------------

def get_week():
    try:
        with open(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_WEEK, 'rb') as file_in:
            week = pickle.load(file_in)
        return week
    except:
        return None

# --------------------------------------------------------------------------------------------------

def get_analysis():
    try:
        with open(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_ANALYSIS, 'rb') as file_in:
            analysis = pickle.load(file_in)
        return analysis
    except:
        return None

# --------------------------------------------------------------------------------------------------

def get_total_num_items(analysis, preview=False):
    return sum([
        feed_analysis['num_items']
        for filename_with_infostamp, feed_analysis in analysis.items()
        if (    ((not preview) and ('000-preview' not in filename_with_infostamp))
            or  ((preview) and ('000-preview' in filename_with_infostamp)) )
    ])
    
def get_total_num_items_week(week):
    return sum([
        week['num_items']
        for filename_with_infostamp, week in week.items()
    ])

# --------------------------------------------------------------------------------------------------

def get_total_activities_counts(analysis, preview=False):
    total_activities_counts = {}

    for filename_with_infostamp, feed_analysis in analysis.items():
        if (    ((not preview) and ('000-preview' not in filename_with_infostamp))
            or  ((preview) and ('000-preview' in filename_with_infostamp))
        ):
            for activity, count in feed_analysis['activities_counts'].items():
                if (activity not in total_activities_counts.keys()):
                    total_activities_counts[activity] = count
                else:
                    total_activities_counts[activity] += count

    return total_activities_counts

# --------------------------------------------------------------------------------------------------

def get_df_total_coords_counts(analysis, preview=False):
    total_coords_counts = {}

    for filename_with_infostamp, feed_analysis in analysis.items():
        if (    ((not preview) and ('000-preview' not in filename_with_infostamp))
            or  ((preview) and ('000-preview' in filename_with_infostamp))
        ):
            for coords, count in feed_analysis['coords_counts'].items():
                if (coords not in total_coords_counts.keys()):
                    total_coords_counts[coords] = count
                else:
                    total_coords_counts[coords] += count

    df_total_coords_counts = pd.DataFrame(
        sorted(
            list(map(
                # lambda coords_count: tuple([float(coord) for coord in coords_count[0].split(',')] + [coords_count[1]]),
                lambda coords_count: tuple(list(map(float, coords_count[0].split(','))) + [coords_count[1]]),
                total_coords_counts.items() # total_coords_counts_regular
            )),
            key=lambda item: item[2],
            reverse=True,
        ),
        columns=['latitude', 'longitude', 'count'],
    )

    return df_total_coords_counts

# --------------------------------------------------------------------------------------------------

def get_gdf_total_regions_counts(gdf_regions, df_total_coords_counts):
    # gdf_regions: Columns are: [FID, RGN23CD, RGN23NM, BNG_E, BNG_N, LONG, LAT, GlobalID, geometry]
    # df_total_coords_counts: Columns are: [latitude, longitude, count]

    # Columns are: [latitude, longitude, count, geometry]
    gdf_total_coords_counts = gpd.GeoDataFrame(
        df_total_coords_counts,
        geometry=gpd.points_from_xy(
            df_total_coords_counts['longitude'],
            df_total_coords_counts['latitude'],
        ),
        crs='epsg:4326', # Set CRS to WGS84
    ) \
    .to_crs(gdf_regions.crs)

    # Columns are: [RGN23NM, count]
    gdf_total_regions_counts = gpd.GeoDataFrame(
        gpd.sjoin(
            gdf_regions[['RGN23NM', 'geometry']],
            gdf_total_coords_counts[['count', 'geometry']],
            how='right',
            predicate='intersects',
        ) \
        .groupby('RGN23NM')['count'] \
        .sum()
    ) \
    .reset_index()

    # Columns are: [FID, RGN23CD, RGN23NM, BNG_E, BNG_N, LONG, LAT, GlobalID, geometry, count]
    gdf_total_regions_counts = \
        gdf_regions \
        .merge(gdf_total_regions_counts, on='RGN23NM', how='left') \
        .sort_values(by='count', ascending=False)

    # Columns are: [FID, RGN23CD, RGN23NM, BNG_E, BNG_N, LONG, LAT, GlobalID, geometry, count, percentage]
    gdf_total_regions_counts['percentage'] = round((gdf_total_regions_counts['count'] / gdf_total_regions_counts['count'].sum(skipna=True)) * 100, 1)
    # print('gdf_total_regions_counts:')
    # print(gdf_total_regions_counts)

    return gdf_total_regions_counts

# --------------------------------------------------------------------------------------------------

def get_gdf_total_lads_counts(gdf_lads, df_total_coords_counts):

    gdf_total_coords_counts = gpd.GeoDataFrame(
            df_total_coords_counts,
            geometry=gpd.points_from_xy(
                df_total_coords_counts['longitude'],
                df_total_coords_counts['latitude'],
            ),
            crs='epsg:4326', # Set CRS to WGS84
        ) \
        .to_crs(gdf_lads.crs)
        
    # Columns are: [LAD24NM, count]
    gdf_total_lads_counts = gpd.GeoDataFrame(
        gpd.sjoin(
            gdf_lads[['LAD24NM', 'geometry']],
            gdf_total_coords_counts[['count', 'geometry']],
            how='right',
            predicate='intersects',
        ) \
        .groupby('LAD24NM')['count'] \
        .sum()
    ) \
    .reset_index()

    gdf_total_lads_counts = \
        gdf_lads \
        .merge(gdf_total_lads_counts, on='LAD24NM', how='left') \
        .sort_values(by='count', ascending=False) \
        .fillna(0)

    gdf_total_lads_counts['percentage'] = round((gdf_total_lads_counts['count'] / gdf_total_lads_counts['count'].sum(skipna=True)) * 100, 1)
    # print('gdf_total_lads_counts:')
    # print(gdf_total_lads_counts)

    return gdf_total_lads_counts

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
    st.session_state.RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')

    st.session_state.FILENAME_ANALYSIS = getenv('FILENAME_ANALYSIS', 'analysis.pickle')
    st.session_state.FILENAME_WEEK = getenv('FILENAME_WEEK', 'week.pickle')
    st.session_state.FILENAME_REGIONS = getenv('FILENAME_REGIONS', 'regions.geojson')
    st.session_state.FILENAME_LADS = getenv('FILENAME_LADS', 'lads.geojson')
    st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE = getenv('FILENAME_SE_SPORT_AND_DISCIPLINE', 'SE-sport-and-discipline.csv')
    st.session_state.FILENAME_OA_SE_MAPPING = getenv('FILENAME_OA_SE_MAPPING', 'OA-SE-mapping.csv')

    print('Environment variables:')
    print('RELATIVE_FILEPATH_ANALYSIS:', st.session_state.RELATIVE_FILEPATH_ANALYSIS)
    print('FILENAME_ANALYSIS:', st.session_state.FILENAME_ANALYSIS)
    print('FILENAME_WEEK:', st.session_state.FILENAME_WEEK)
    print('FILENAME_REGIONS:', st.session_state.FILENAME_REGIONS)
    print('FILENAME_LADS:', st.session_state.FILENAME_LADS)
    print('FILENAME_SE_SPORT_AND_DISCIPLINE:', st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE)
    print('FILENAME_OA_SE_MAPPING:', st.session_state.FILENAME_OA_SE_MAPPING)

    # --------------------------------------------------------------------------------------------------

    st.session_state.analysis = get_analysis()
    st.session_state.week = get_week()
    
    if (st.session_state.analysis is None):
        st.session_state.error = True
        st.error('Error retrieving analysis data')
    else:
        st.session_state.error = False

        # Even with no parameters given to set_theme(), simply running it empty initialises general Seaborn
        # theming, otherwise we have general Matplotlib theming:
        sns.set_theme(rc={
            # 'figure.figsize': (10, 4),
            'patch.linewidth': 0.0, # Border width around individual bars
        })

        # --------------------------------------------------------------------------------------------------

        st.session_state.filenames_with_infostamp_regular = [filename_with_infostamp for filename_with_infostamp in st.session_state.analysis.keys() if ('000-preview' not in filename_with_infostamp)]
        st.session_state.filenames_with_infostamp_preview = [filename_with_infostamp for filename_with_infostamp in st.session_state.analysis.keys() if ('000-preview' in filename_with_infostamp)]
        st.session_state.filenames_with_infostamp_total = [filename_with_infostamp for filename_with_infostamp in st.session_state.analysis.keys()]

        st.session_state.total_num_items_regular = get_total_num_items(st.session_state.analysis, preview=False)
        st.session_state.total_num_items_preview = get_total_num_items(st.session_state.analysis, preview=True)
        st.session_state.total_num_items = st.session_state.total_num_items_regular + st.session_state.total_num_items_preview

        st.session_state.total_activities_counts_regular = get_total_activities_counts(st.session_state.analysis, preview=False)
        st.session_state.total_activities_counts_preview = get_total_activities_counts(st.session_state.analysis, preview=True)
 
 
        # --------------------------------------------------------------------------------------------------

        # For the '7 days' tab
        st.session_state.total_num_items_week = get_total_num_items_week(st.session_state.week)

        # --------------------------------------------------------------------------------------------------

        # For the 'Activities' tab

        st.session_state.df_total_activities_counts_regular = pd.DataFrame(
            sorted(
                st.session_state.total_activities_counts_regular.items(),
                key=lambda item: item[1],
                reverse=True,
            ),
            columns=['activity', 'count'],
        )
        st.session_state.df_total_activities_counts_preview = pd.DataFrame(
            sorted(
                st.session_state.total_activities_counts_preview.items(),
                key=lambda item: item[1],
                reverse=True,
            ),
            columns=['activity', 'count'],
        )

        st.session_state.total_activities_counts = st.session_state.total_activities_counts_regular.copy()
        for activity, count in st.session_state.total_activities_counts_preview.items():
            if (activity not in st.session_state.total_activities_counts.keys()):
                st.session_state.total_activities_counts[activity] = count
            else:
                st.session_state.total_activities_counts[activity] += count

        st.session_state.df_total_activities_counts = pd.DataFrame(
            sorted(
                st.session_state.total_activities_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            ),
            columns=['activity', 'count'],
        )

        st.session_state.df_total_activities_counts.to_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + 'sorted_activities.csv', index=False)
        # st.write("Sorted activities saved to 'sorted_activities.csv'")

        st.session_state.num_activities_top = 20

        # --------------------------------------------------------------------------------------------------

        # For the 'Locations' tab

        gdf_regions = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_REGIONS)
        gdf_lads = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_LADS)

        df_total_coords_counts_regular = get_df_total_coords_counts(st.session_state.analysis, preview=False)
        df_total_coords_counts_preview = get_df_total_coords_counts(st.session_state.analysis, preview=True)

        st.session_state.gdf_total_regions_counts_regular = get_gdf_total_regions_counts(gdf_regions, df_total_coords_counts_regular)
        st.session_state.gdf_total_regions_counts_preview = get_gdf_total_regions_counts(gdf_regions, df_total_coords_counts_preview)
        st.session_state.gdf_total_lads_counts_regular = get_gdf_total_lads_counts(gdf_lads, df_total_coords_counts_regular)
        st.session_state.gdf_total_lads_counts_preview = get_gdf_total_lads_counts(gdf_lads, df_total_coords_counts_preview)

        # --------------------------------------------------------------------------------------------------

        # For the 'KPIs' tab

        # Columns are: [sport, discipline, sport_and_discipline]
        df_se_sport_and_discipline = pd.read_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_SE_SPORT_AND_DISCIPLINE)

        # Columns are: [activity, sport_and_discipline]
        df_oa_se_mapping = pd.read_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_OA_SE_MAPPING)

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

        # df_oa_se_mapping.to_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_OA_SE_MAPPING)

        # Columns are: [activity, count, sport_and_discipline]
        st.session_state.df_total_sad_counts = pd.merge(st.session_state.df_total_activities_counts, df_oa_se_mapping, how='left')
        st.session_state.df_total_sad_counts['sport_and_discipline'].fillna('No Match', inplace=True)

        # Columns are: [('sport_and_discipline', ''), ('activity', '<lambda>'), ('count', 'count'), ('count', 'sum')] # Note that these are MultiIndex columns, each element of a tuple corresponds to a different header row
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

        col1, col2 = st.columns(2)
        with col1:
            st.metric('Number of OpenActive feeds', len(st.session_state.filenames_with_infostamp_total))

        with col2:
            st.metric('Number of live OpenActive opportunities', f'{st.session_state.total_num_items:,}')

        st.write(f'These figures include {len(st.session_state.filenames_with_infostamp_preview)} preview feeds with {round(st.session_state.total_num_items_preview / 1000000, 1)}m preview opportunities')

        # dated_counts = {
        #     'Jan 17': 0,
        #     'Jul 17': 80000,
        #     'Jan 18': 80000,
        #     'Jul 18': 110000,
        #     'Jan 19': 160000,
        #     'Jun 19': 200000,
        # }

        # current_month = datetime.now().strftime('%b %y')
        # dated_counts[current_month] = total_num_items_regular + total_num_items_preview
        # df = pd.DataFrame.from_dict(dated_counts, orient='index', columns=['Count'])
        # df.reset_index(inplace=True)
        # df.columns = ['Date', 'Count']
        # df['Date'] = pd.to_datetime(df['Date'], format='%b %y')
        # df = df.sort_values(by='Date')

        # st.line_chart(df, x='Date', y='Count')

    # --------------------------------------------------------------------------------------------------

    with tabs[1]:
        st.header('Opportunities over the next 7 days')

        st.metric('Number of live OpenActive opportunities', f'{st.session_state.total_num_items_week:,}')

        st.write('Sample data')
                # Access the 'week' dictionary
        week = st.session_state.week

# Keep track of how many items we've displayed
        items_displayed = 0

        while items_displayed < 5:
            # Choose a random key
            random_key = random.choice(list(week.keys()))

            # Access the 'items' list within the week data
            sample = week[random_key]['items']

            # Print a random item from the sample
            if sample:
                random_item = random.choice(sample)
                st.write(random_item)
                items_displayed += 1
            else:
                print(f"No items in the sample for file: {random_key}")


        
        
        
        
    # --------------------------------------------------------------------------------------------------

    with tabs[2]:
        st.header('Most popular activities')

        for preview in [False, True]:
            if (not preview):
                st.subheader('Regular feeds', divider='gray')
                df_total_activities_counts = st.session_state.df_total_activities_counts_regular
            else:
                st.subheader('Preview feeds', divider='gray')
                df_total_activities_counts = st.session_state.df_total_activities_counts_preview

            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(
                    '<div style="text-align: center;">All activities</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    df_total_activities_counts,
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
                    df_total_activities_counts[:st.session_state.num_activities_top],
                    x='count',
                    y='activity',
                    ax=ax,
                )
                ax.bar_label(ax.containers[0], fontsize=8)
                # ax.set_title(f'Top {st.session_state.num_activities_top} activities')
                st.pyplot(fig)
                plt.close(fig)

        # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # sns.barplot(
        #     st.session_state.df_total_activities_counts_regular[:st.session_state.num_activities_top],
        #     x='count',
        #     y='activity',
        #     ax=ax1,
        # )

        # sns.barplot(
        #     st.session_state.df_total_activities_counts_preview[:st.session_state.num_activities_top],
        #     x='count',
        #     y='activity',
        #     ax=ax2,
        # )

        # plt.tight_layout() # Prevents top subplot x-axis label overlapping bottom subplot title
        # st.pyplot(fig)

    # --------------------------------------------------------------------------------------------------

    with tabs[3]:
        st.header('OpenActive opportunities by region')

        for preview in [False, True]:
            if (not preview):
                st.subheader('Regular feeds', divider='gray')
                gdf_total_regions_counts = st.session_state.gdf_total_regions_counts_regular
            else:
                st.subheader('Preview feeds', divider='gray')
                gdf_total_regions_counts = st.session_state.gdf_total_regions_counts_preview

            col1, col2, col3 = st.columns(3)
            with col1:
                st.dataframe(
                    gdf_total_regions_counts[['RGN23NM', 'count', 'percentage']].set_index('RGN23NM'),
                    use_container_width=True,
                )
            with col2:
                fig, ax = plt.subplots(1, 1)
                gdf_total_regions_counts.plot(
                    column='percentage',
                    cmap='YlOrRd', # 'Greys_r' for reversed greyscale
                    legend=True,
                    ax=ax,
                )
                ax.set_xticks([])
                ax.set_yticks([])
                st.pyplot(fig)
                plt.close(fig)

    # LA breakdown
    
        for preview in [False, True]:
            if (not preview):
                st.subheader('Regular feeds', divider='gray')
                gdf_total_lads_counts = st.session_state.gdf_total_lads_counts_regular
            else:
                st.subheader('Preview feeds', divider='gray')
                gdf_total_lads_counts = st.session_state.gdf_total_lads_counts_preview

            col1, col2, col3 = st.columns(3)
            with col1:
                st.dataframe(
                    gdf_total_lads_counts[['LAD24NM', 'count', 'percentage']].set_index('LAD24NM'),
                    use_container_width=True,
                )
            with col2:
                fig, ax = plt.subplots(1, 1)
                gdf_total_lads_counts.plot(
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