import pickle
import seaborn as sns
import streamlit as st
import sys

sys.path.append('../volume-1/common')
from settings import *

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

    st.session_state.error = False

    if (not st.session_state.error):
        try:
            with open(FEEDS_RELATIVE_FILEPATH + '/' + REGULAR_FEEDS_LATEST_FILENAME, 'rb') as file_in: # Or PREVIEW_FEEDS_LATEST_FILENAME
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
        }

        for feed in feeds['feeds']:
            if feed.get('logoUrl'):
                if (feed['logoUrl'] not in logo_urls):
                    logo_urls.append(feed['logoUrl'])
            if feed.get('type'):
                feed_type = feed_type_map.get(feed['type'], feed['type'])
                feed_type_counts[feed_type] = feed_type_counts.get(feed_type, 0) + 1
            else:
                feed_type_counts['Event'] = feed_type_counts.get('Event', 0) + 1


        #Hardcode for now to avoid duplication and invalid images
        logo_urls =['https://activehartlepool.gs-signature.cloud/OpenActive/Content/images/gladstone.png',
            'https://res.cloudinary.com/gladstone/image/upload/ActiveLeeds-live/jomzctf3tyiaxwkplobw',
            'https://res.cloudinary.com/gladstone/image/upload/BrimhamsActive-live/x8ejlrqiurnrkwk6de0c',
            'https://res.cloudinary.com/gladstone/image/upload/CastlePoint-live/iqsv4e4vltiktbk5poqp',
            'https://res.cloudinary.com/gladstone/image/upload/Chelmsfordcitysports-live/w3epkovizgpzzwywfcfh',
            'https://res.cloudinary.com/gladstone/image/upload/Pembrokeshire-live/ob8ojuwtxmuvcgvcov3t',
            'https://res.cloudinary.com/gladstone/image/upload/EveryoneActive-live/rgcua81zg3tbakllsku0',
            'https://res.cloudinary.com/gladstone/image/upload/FyldeCoastYMCA-live/mjuxezbhgqkjtoxxbwls',
            'https://res.cloudinary.com/gladstone/image/upload/LED-live/ccitexbsykzhprracuvm',
            'https://res.cloudinary.com/gladstone/image/upload/LeisureSK-live/i2ngfvco92o8ynkovjkc',
            'https://res.cloudinary.com/gladstone/image/upload/LibertyLeisure-live/g3ravmvtqehkhaqr7lqf',
            'https://res.cloudinary.com/gladstone/image/upload/Oxford-Univesity-live/xtah7f0ul9r74hxyjzi4',
            'https://res.cloudinary.com/gladstone/image/upload/PlymouthCouncil-live/wbdbolfdxoyatgpdlu6x',
            'https://res.cloudinary.com/gladstone/image/upload/RedbridgeSportsCentre-live/ssuknvpivtiynnfu0l0p',
            'https://res.cloudinary.com/gladstone/image/upload/Calderdale-live/tcwuyxzlas9n0g0pepcw',
            'https://bwdleisure.com/wp-content/uploads/2019/08/bwd-leisure.jpg',
            'https://www.serco.com/images/twitter-logo.png',
            'https://www.activetameside.com/wp-content/uploads/2022/08/AT-Primary-RGB.png',
            'https://www.inderby.org.uk/themes/in_derby/assets/favicons/inderby/apple-icon-180x180.png',
            'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd6RsfZCLMwmh9xw5C-M9ADqM2K5EZaa17Vc0QdEI0KA&amp;s',
            'http://data.better.org.uk/images/logo.png',
            'https://cdn.bookwhen.com/assets/home/json_ld/bookwhen_logo-d08e3214ef4aa950bef4228170ed3f053c85cdd39306dfe266527631b316a818.png',
            'http://data.letsride.co.uk/images/logo.png',
            'http://data.britishorienteering.org.uk/images/logo.png',
            'http://data.britishtriathlon.org/images/logo.png',
            'https://data.englandnetball.co.uk/images/logo.png',
            'http://data.gomammoth.co.uk/images/logo.png',
            'http://data.goodgym.org/images/logo.png',
            'https://lawntennisassociation.github.io/images/logo.png',
            'https://opensession.s3.eu-west-2.amazonaws.com/assets/img/opensessionslogo.svg',
            'https://ourparks.org.uk/sites/all/themes/commons/commons_origins/images/logo.png',
            'https://data.playwaze.com/images/logo.png',
            'https://data.runtogether.co.uk/images/logo.png',
            'https://sportstarta.github.io/images/logo.png',
            'https://openactive.upshot.org.uk/images/logo.png',
            'https://opendata.exercise-anywhere.com/img/logo.jpg',
            'https://www.sportsuite.co.uk/css/ss/ss-logo.svg',
            'https://teamupstatic.com/assets/api/images/logo_with_wordmark.8f86d8d78e10.png',
            'https://api.premiertennis.co.uk/img/premier-tennis-logo-alt.svg',
            'https://playfootball-public-assets.s3.eu-west-2.amazonaws.com/playfootball_logo_black.svg',
            'https://s3.eu-west-2.amazonaws.com/cdn.bookteq.com/logo-small.png',
        ]

        st.session_state.logo_urls = logo_urls
        st.session_state.feed_type_counts = feed_type_counts
        st.session_state.num_feeds = len(feeds['feeds'])

    # --------------------------------------------------------------------------------------------------

    if (not st.session_state.error):
        try:
            with open(ANALYSIS_RELATIVE_FILEPATH + '/' + ANALYSIS_AGGREGATED_FILENAME, 'rb') as file_in:
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