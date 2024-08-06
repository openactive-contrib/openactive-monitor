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
    gdf_total_regions_counts['percentage'] = round((gdf_total_regions_counts['count'] / sum(gdf_total_regions_counts['count'])) * 100, 1)

    return gdf_total_regions_counts

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
    st.session_state.FILENAME_REGIONS = getenv('FILENAME_REGIONS', 'regions.geojson')

    print('Environment variables:')
    print('RELATIVE_FILEPATH_ANALYSIS:', st.session_state.RELATIVE_FILEPATH_ANALYSIS)
    print('FILENAME_ANALYSIS:', st.session_state.FILENAME_ANALYSIS)
    print('FILENAME_REGIONS:', st.session_state.FILENAME_REGIONS)

    # --------------------------------------------------------------------------------------------------

    st.session_state.analysis = get_analysis()

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

        st.session_state.total_num_items_regular = get_total_num_items(st.session_state.analysis, preview=False)
        st.session_state.total_num_items_preview = get_total_num_items(st.session_state.analysis, preview=True)

        st.session_state.total_activities_counts_regular = get_total_activities_counts(st.session_state.analysis, preview=False)
        st.session_state.total_activities_counts_preview = get_total_activities_counts(st.session_state.analysis, preview=True)

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

        st.session_state.df_total_activities_counts_regular.to_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + 'sorted_activities.csv', index=False)
        # st.write("Sorted activities saved to 'sorted_activities.csv'")

        st.session_state.num_activities_top = 20

        # --------------------------------------------------------------------------------------------------

        # For the 'Locations' tab

        gdf_regions = gpd.read_file(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + st.session_state.FILENAME_REGIONS)

        df_total_coords_counts_regular = get_df_total_coords_counts(st.session_state.analysis, preview=False)
        df_total_coords_counts_preview = get_df_total_coords_counts(st.session_state.analysis, preview=True)

        st.session_state.gdf_total_regions_counts_regular = get_gdf_total_regions_counts(gdf_regions, df_total_coords_counts_regular)
        st.session_state.gdf_total_regions_counts_preview = get_gdf_total_regions_counts(gdf_regions, df_total_coords_counts_preview)

        # --------------------------------------------------------------------------------------------------

        # For the 'KPIs' tab

# --------------------------------------------------------------------------------------------------

if (not st.session_state.error):
    tabs = st.tabs(['Overview', 'This week', 'Activities', 'Locations', 'KPIs'])

    with tabs[0]:
        st.header('Overview of the OpenActive data ecosystem')

        for preview in [False, True]:
            if (not preview):
                st.subheader('Regular feeds', divider='gray')
                filenames_with_infostamp = st.session_state.filenames_with_infostamp_regular
                total_num_items = st.session_state.total_num_items_regular
            else:
                st.subheader('Preview feeds', divider='gray')
                filenames_with_infostamp = st.session_state.filenames_with_infostamp_preview
                total_num_items = st.session_state.total_num_items_preview

            col1, col2 = st.columns(2)
            with col1:
                st.metric('Num. feeds', len(filenames_with_infostamp))
            with col2:
                st.metric('Num. opportunities', f'{total_num_items:,}')

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

    # --------------------------------------------------------------------------------------------------

    with tabs[4]:
        st.header('KPIs')

        st.subheader('Regular feeds', divider='gray')

        # 2.1.1 - % of Sport England recognised activities appearing in OpenActive data feeds

        # Load Sport England recognised activities from a CSV file
        df_sport_england = pd.read_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + 'Sport and Disciplines.csv')

        # Create a DataFrame from the gemini matched activities
        df_activities = pd.read_csv(st.session_state.RELATIVE_FILEPATH_ANALYSIS + '/' + 'matched_activities.csv')

        df_activities = df_activities.loc[df_activities['activity'] != 'activity']

        # Convert 'count' column to integers before grouping
        df_activities['count'] = df_activities['count'].astype(int)

        # Group by 'sport_and_discipline' and sum the 'count' column
        df_grouped = df_activities.groupby('sport_and_discipline')['count'].sum().reset_index()

        # Create a new column 'activities' to store comma-separated activities
        activities_string = df_activities.groupby('sport_and_discipline')['activity'].apply(list).apply(lambda x: ', '.join(x))
        df_output = pd.merge(df_grouped, activities_string, left_on='sport_and_discipline', right_on='sport_and_discipline', how='inner')

        # Sort the DataFrame by 'count' in descending order
        df_output = df_output.sort_values(by='count', ascending=False)

        percentage_matched = round(len(df_output) / len(df_sport_england) * 100, 0)

        st.subheader(f"2.1.1 - {percentage_matched}% of Sport England recognised activities appearing in OpenActive data feeds")

        # Print the resulting DataFrame, including the 'activities' column
        st.write(f"Matching {len(df_output) } of {len(df_sport_england)} Sports and Disciplines")
        st.dataframe(df_output[['sport_and_discipline', 'count','activity']], width=1000, hide_index=True)

        # Get unmatched sports and disciplines
        unmatched_sport_england = df_sport_england[~df_sport_england['sd'].isin(df_output['sport_and_discipline'])]

        st.write(f"Unmatched: {len(df_sport_england) - len(df_output) } Sports and Disciplines")
        st.dataframe(unmatched_sport_england[['SPORT','DISCIPLINE']], hide_index=True, width=600)