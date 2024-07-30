# import os
import pickle
import pandas as pd
import streamlit as st
from os import getenv
from datetime import datetime

# --------------------------------------------------------------------------------------------------

st.set_page_config(
    page_title='OpenActive',
    page_icon='https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png',
    layout='wide',
    menu_items={
        'Get help': 'mailto:hello@openactive.io',
        'About': 'Copyright 2024 OpenActive: Build trigger test 2',
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
    st.bar_chart(chart_data, x='activity', y='count', horizontal=True, use_container_width=True)

with tabs[3]:
    st.header('Locations')
    # Add content related to data feeds here

with tabs[4]:
    st.header('KPIs')
    # Add content related to analysis here

# --------------------------------------------------------------------------------------------------