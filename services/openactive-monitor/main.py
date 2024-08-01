# import os
import pickle
import pandas as pd
import streamlit as st
from os import getenv
from datetime import datetime
import re
import difflib
import geopandas as gpd
import matplotlib.pyplot as plt

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

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this service called 'openactive-monitor', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run services update openactive-monitor \
#   --region europe-west2 \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_FEEDS = getenv('RELATIVE_FILEPATH_FEEDS', '../volume-1/data-feeds')
RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')

FILENAME_FEEDS = 'feeds.pickle'
FILENAME_ANALYSIS = 'analysis.pickle'

# --------------------------------------------------------------------------------------------------

def get_feeds():
    try:
        with open(RELATIVE_FILEPATH_FEEDS + '/' + FILENAME_FEEDS, 'rb') as file_in:
            feeds = pickle.load(file_in)
        return feeds
    except:
        return None


# --------------------------------------------------------------------------------------------------

def get_analysis():
    try:
        with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'rb') as file_in:
            analysis = pickle.load(file_in)
        # Calculate total 'num_items'
        total_num_items = sum(item['num_items'] for item in analysis.values())
        return total_num_items
    except:
        return None

# --------------------------------------------------------------------------------------------------

def get_activities_counts():
    try:

        with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'rb') as file_in:
            analysis = pickle.load(file_in)   
            
        activities_counts = {}
        
        for item in analysis.values():
            # Access the 'activities_counts' dictionary within each item
            item_activities_counts = item.get('activities_counts', {})
            # Iterate through the activities in the item's 'activities_counts'
            for activity, count in item_activities_counts.items():
                if activity in activities_counts:
                    activities_counts[activity] += count
                else:
                    activities_counts[activity] = count
        return activities_counts
    except:
        return None
    

# --------------------------------------------------------------------------------------------------

def get_coords_counts():
    try:

        with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'rb') as file_in:
            analysis = pickle.load(file_in)   

        coords_counts = {}
        
        for item in analysis.values():
            # Access the 'activities_counts' dictionary within each item
            item_coords_counts = item.get('coords_counts', {})
            # Iterate through the activities in the item's 'activities_counts'
            for coords, count in item_coords_counts.items():
                if coords in coords_counts:
                    coords_counts[coords] += count
                else:
                    coords_counts[coords] = count
        return coords_counts
    except:
        return None
    
# --------------------------------------------------------------------------------------------------


# Create tabs
tabs = st.tabs(["Overview", "This Week", "Activities and Facilities", "Locations", "KPIs"])

with tabs[0]:
    st.header('Overview of OpenActive Data Ecosystem')

    col1, col2 = st.columns(2)

    # Using 'with' notation:
    with col1:
        # Extract and present num_feeds from the JSON
        feeds_data = get_feeds()  # Get the feeds data
        if feeds_data is not None:
            num_feeds = feeds_data['num_feeds']  # Access the 'num_feeds' key
            st.metric('Number of Feeds', num_feeds)  # Display the num_feeds metric
        else:
            st.error('Error retrieving feeds data.')

    with col2:
        # Show total headline opportunity count
        total_num_items = get_analysis()
        if total_num_items is not None:
            st.metric('Total Num Items', f"{total_num_items:,}")  # Format with comma separators
        else:
            st.error('Error retrieving analysis data.')

    dated_counts = {
        'Jan 17': 0,
        'Jul 17': 80000,
        'Jan 18': 80000,
        'Jul 18': 110000,
        'Jan 19': 160000,
        'Jun 19': 200000
    }

    # Get today's month and year
    today = datetime.now()
    current_month = today.strftime('%b %y')

    # Append today's count to the data
    total_num_items = get_analysis()
    if total_num_items is not None:
        dated_counts[current_month] = total_num_items

    # Convert the dictionary to a Pandas DataFrame
    df = pd.DataFrame.from_dict(dated_counts, orient='index', columns=['Count'])

    # Reset the index to make the date column a regular column
    df.reset_index(inplace=True)

    # Rename the columns for clarity
    df.columns = ['Date', 'Count']

    # Convert the 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'], format='%b %y')

    # Sort the DataFrame by date
    df = df.sort_values(by='Date')

    # Now you have a DataFrame ready for plotting with Streamlit's line_chart:
    st.line_chart(df, x='Date', y='Count')

with tabs[1]:
    st.header('Opportunities over next 7 days')
    
with tabs[2]:
    st.header('Top 100 Activities')

    activities_summary = get_activities_counts()

    # Sort the activities_summary dictionary by value in descending order
    sorted_activities = dict(sorted(activities_summary.items(), key=lambda item: item[1], reverse=True))

    # Take the top 100 activities
    top_100_activities = dict(list(sorted_activities.items())[:100])

    # Convert the top_100_activities dictionary to a format suitable for Streamlit's bar chart
    chart_data = [{'activity': activity, 'count': int(count)} for activity, count in top_100_activities.items()]

    # Create the horizontal bar chart
    #st.bar_chart(chart_data, x='activity', y='count', horizontal=True, use_container_width=True)
    
    st.dataframe(chart_data, width=1000, hide_index=True)
        
    # Output sorted_activities to CSV
    df_sorted_activities = pd.DataFrame.from_dict(sorted_activities, orient='index', columns=['count'])
    df_sorted_activities.reset_index(inplace=True)
    df_sorted_activities.rename(columns={'index': 'activity'}, inplace=True)
    df_sorted_activities.to_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'sorted_activities.csv', index=False)
    st.write("Sorted activities saved to 'sorted_activities.csv'")

# ... (rest of your code)

with tabs[3]:
    st.header('OpenActive Opportunities by Region')


    col1, col2 = st.columns(2)
    
    # Load your data
    data = get_coords_counts()

    # Convert location strings to coordinates
    coords_data = []  # Create an empty list to store coordinates and counts
    for coords, count in data.items():
        latitude, longitude = map(float, coords.split(','))  # Split coords string and convert to floats
        coords_data.append({'coords': coords, 'latitude': latitude, 'longitude': longitude, 'count': count})

    # Create a DataFrame from the coords_data list
    data_df = pd.DataFrame(coords_data)

    # Load your shapefile
    shapefile_path = RELATIVE_FILEPATH_ANALYSIS + '/' + "regions.geojson"  # Replace with your shapefile path
    gdf = gpd.read_file(shapefile_path)

    # Get the CRS of your shapefile
    shapefile_crs = gdf.crs

    # Create a GeoDataFrame from your data with the correct CRS
    data_gdf = gpd.GeoDataFrame(
        data_df,
        geometry=gpd.points_from_xy(data_df['longitude'], data_df['latitude'], crs='epsg:4326'),  # Set CRS to WGS84
        crs='epsg:4326',  # Set CRS to WGS84
    )

    # Reproject the point data to match the shapefile's CRS
    data_gdf = data_gdf.to_crs(shapefile_crs)

    # Perform spatial join (using 'intersects' for potential boundary matches)
    joined_gdf = gpd.sjoin(data_gdf, gdf, how='left', predicate='intersects')

    # Group by shapefile ID and sum the counts
    counts_by_shape = joined_gdf.groupby('RGN23NM')['count'].sum().reset_index()
    # Sort counts_by_shape by 'count' in descending order
    counts_by_shape = counts_by_shape.sort_values(by='count', ascending=False)
    # Calculate total count for percentage calculation
    total_count = counts_by_shape['count'].sum()

    # Convert count to percentage
    counts_by_shape['percentage'] = round((counts_by_shape['count'] / total_count) * 100,1)

    # Merge counts with the shapefile GeoDataFrame
    merged_gdf = gdf.merge(counts_by_shape, on='RGN23NM', how='left')

    # Convert count to percentage
    merged_gdf['percentage'] = (merged_gdf['count'] / total_count) * 100

    # Create the chloropleth map
    fig, ax = plt.subplots(1, 1)

    # Remove numbers from axes
    ax.set_xticks([])
    ax.set_yticks([])

    # Plot the polygons with color based on 'percentage' using a greyscale colormap
    merged_gdf.plot(ax=ax, column='percentage', legend=True, cmap='YlOrRd')  # 'Greys_r' for reversed greyscale

    
    with col1:
        st.dataframe(counts_by_shape.set_index('RGN23NM'))

    with col2:
        st.pyplot(fig)

# ... (rest of your code)


with tabs[4]:
    st.header('KPIs')
    
    # 2.1.1 - % of Sport England recognised activities appearing in OpenActive data feeds
    
    # Load Sport England recognised activities from a CSV file
    df_sport_england = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'Sport and Disciplines.csv')
    
    # Create a DataFrame from the gemini matched activities
    df_activities = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'matched_activities.csv')

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