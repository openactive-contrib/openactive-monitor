# import os
import pickle
import streamlit as st
from os import getenv

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

with st.sidebar:
    st.image('https://openactive.io/brand-assets/openactive-logo-large.png')

# --------------------------------------------------------------------------------------------------

st.json(get_feeds())

# --------------------------------------------------------------------------------------------------

# Display the total count in Streamlit
st.title('Dashboard Metrics')
st.metric('Total Num Items', get_analysis())

# --------------------------------------------------------------------------------------------------
