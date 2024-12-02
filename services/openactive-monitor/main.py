import pickle
import seaborn as sns
import streamlit as st
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

if ('initialised' not in st.session_state):
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
    FILENAME_FEEDS = getenv('FILENAME_FEEDS', 'feeds.pickle') # Located in RELATIVE_FILEPATH_FEEDS
    FILENAME_FEEDS_PREVIEW = getenv('FILENAME_FEEDS_PREVIEW', 'feeds-preview.pickle') # Located in RELATIVE_FILEPATH_FEEDS
    FILENAME_ANALYSIS = getenv('FILENAME_ANALYSIS', 'analysis.pickle')

    print('Environment variables:')
    print('RELATIVE_FILEPATH_FEEDS:', RELATIVE_FILEPATH_FEEDS)
    print('RELATIVE_FILEPATH_ANALYSIS:', RELATIVE_FILEPATH_ANALYSIS)
    print('FILENAME_FEEDS:', FILENAME_FEEDS)
    print('FILENAME_FEEDS_PREVIEW:', FILENAME_FEEDS_PREVIEW)
    print('FILENAME_ANALYSIS:', FILENAME_ANALYSIS)

    # --------------------------------------------------------------------------------------------------

    st.session_state.error = False

    # --------------------------------------------------------------------------------------------------

    if (not st.session_state.error):
        try:
            with open(RELATIVE_FILEPATH_FEEDS + '/' + FILENAME_FEEDS, 'rb') as file_in: # Or FILENAME_FEEDS_PREVIEW
                feeds = pickle.load(file_in)
        except:
            st.session_state.error = True
            st.error('Error retrieving feeds')

    if (not st.session_state.error):
        logo_urls = []
        feed_type_counts = {}

        feed_type_map = {
            'ScheduledSessions': 'ScheduledSession',
            'Slot for FacilityUse': 'Slot',
            # Add other mappings as needed
        }

        for feed in feeds['feeds']:
            if feed.get('logoUrl'):
                if (feed['logoUrl'] not in logo_urls):
                    logo_urls.append(feed['logoUrl'])
            if feed.get('type'):
                feed_type = feed_type_map.get(feed['type'], feed['type'])
                feed_type_counts[feed_type] = feed_type_counts.get(feed_type, 0) + 1

        st.session_state.logo_urls = logo_urls
        st.session_state.feed_type_counts = feed_type_counts

    # --------------------------------------------------------------------------------------------------

    if (not st.session_state.error):
        try:
            with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'rb') as file_in:
                st.session_state.analysis = pickle.load(file_in)
        except:
            st.session_state.error = True
            st.error('Error retrieving analysis')

    if (not st.session_state.error):
        # For the 'This week' tab
        st.session_state.num_feeds_with_sampleitems = len(st.session_state.analysis['filenames_sampleitems'])
        st.session_state.max_num_random_feeds_with_sampleitems = 5

        # For the 'Activities' tab
        st.session_state.num_activities_top = 20

    # --------------------------------------------------------------------------------------------------

    st.session_state.initialised = True

# --------------------------------------------------------------------------------------------------

if (not st.session_state.error):
    page = st.navigation(
        [
            st.Page('navigation/overview.py', title='Overview'),
            st.Page('navigation/details.py', title='Details'),
        ],
        #position='sidebar',
        position='hidden',
    )
    page.run()