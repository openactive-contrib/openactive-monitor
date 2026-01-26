# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. This
# was done for each job and service as follows (note that the volume and its mount-path were given
# the same name, which didn't have to be so):
#
#   $ gcloud beta run jobs update <JOB NAME> \
#   --region europe-west2 \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
#
#   $ gcloud beta run services update <SERVICE NAME> \
#   --region europe-west2 \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1

FEEDS_RELATIVE_FILEPATH = '../volume-1/data-feeds'
OPPORTUNITIES_RELATIVE_FILEPATH = '../volume-1/data-opportunities'
ANALYSIS_RELATIVE_FILEPATH = '../volume-1/data-analysis'

# --------------------------------------------------------------------------------------------------

# Files in FEEDS_RELATIVE_FILEPATH

REGULAR_FEEDS_FILENAME_BASE = 'regular-feeds'
PREVIEW_FEEDS_FILENAME_BASE = 'preview-feeds'
FEEDS_FILENAME_SUFFIX = '.pickle'

REGULAR_FEEDS_LATEST_FILENAME = 'regular-feeds.pickle'
PREVIEW_FEEDS_LATEST_FILENAME = 'preview-feeds.pickle'
REGULAR_FEEDS_HISTORY_FILENAME = 'regular-feeds-history.csv'
PREVIEW_FEEDS_HISTORY_FILENAME = 'preview-feeds-history.csv'
FEEDS_RELATIVE_FILEPATH_SKIP_FILENAMES = [
    REGULAR_FEEDS_LATEST_FILENAME,
    PREVIEW_FEEDS_LATEST_FILENAME,
    REGULAR_FEEDS_HISTORY_FILENAME,
    PREVIEW_FEEDS_HISTORY_FILENAME,
] # Filenames to skip when checking for feeds files in storage

# --------------------------------------------------------------------------------------------------

# Files in OPPORTUNITIES_RELATIVE_FILEPATH

REGULAR_OPPORTUNITIES_FILENAME_BASE = 'regular-ops'
PREVIEW_OPPORTUNITIES_FILENAME_BASE = 'preview-ops'
OPPORTUNITIES_FILENAME_SUFFIX = '.pickle.gzip'

TEMPORARY_OPPORTUNITIES_FILENAME = '000-temporary.pickle.gzip'
RUNNING_FEEDS_FILENAME = '000-running-feeds.pickle'
RUNNING_FEED_FILENAME = '000-running-feed.txt'
CRASHED_FEEDS_FILENAME = '000-crashed-feeds.txt'
OPPORTUNITIES_RELATIVE_FILEPATH_SKIP_FILENAMES = [
    TEMPORARY_OPPORTUNITIES_FILENAME,
    RUNNING_FEEDS_FILENAME,
    RUNNING_FEED_FILENAME,
    CRASHED_FEEDS_FILENAME,
] # Filenames to skip when checking for opportunities files in storage

# --------------------------------------------------------------------------------------------------

# Files in ANALYSIS_RELATIVE_FILEPATH

CROSS_ANALYSIS_FILENAME = 'cross-analysis.pickle'
SEPARATE_ANALYSIS_FILENAME = 'separate-analysis.pickle'
AGGREGATE_ANALYSIS_FILENAME = 'aggregate-analysis.pickle'
SAMPLE_ITEMS_FILENAME = 'sample-items.pickle'
ALL_ITEMS_FILENAME = 'all-items.pickle'

GEO_REGIONS_FILENAME = '000-location-regions.geojson'
GEO_DISTRICTS_FILENAME = '000-location-districts.geojson'
GEO_PARISHES_FILENAME = '000-location-parishes.geojson'
GEO_GPS_FILENAME = '000-location-gps.geojson'
SE_SPORT_AND_DISCIPLINE_FILENAME = '000-SE-sport-and-discipline.csv'
OA_SE_MAPPING_FILENAME = '000-OA-SE-mapping.csv'

# --------------------------------------------------------------------------------------------------

# Running get-feeds

MAX_NUM_FEEDS_FILES = 500 # Number of feeds files to keep for each feed type (regular and preview), including the latest output. 2025-09-03 A regular feeds file is currently ~100KB, so 500 of these is ~50MB. A preview feeds file is currently ~1KB, so 500 of these is ~0.5MB. 500 was chosen to go back ~1.5 years if this is run daily.

GET_FEEDS_VERBOSE = False # Will be overridden if also set as an environment variable e.g. on Google Cloud

# --------------------------------------------------------------------------------------------------

# Running get-opportunities

MAX_NUM_FEEDS = -1 # Negative indicates to do all feeds, otherwise cap at the stated number of feeds. This is useful for testing on a subset of all feeds.
MAX_NUM_FEED_SECONDS = 600
MAX_NUM_FEED_TRIES = 3
MAX_NUM_WRITE_TRIES = 3
MAX_NUM_OPPORTUNITIES_FILES = 1 # Number of opportunities files to keep for each feed, including the latest output

GET_OPPORTUNITIES_LOG_MEMORY = False # Will be overridden if also set as an environment variable e.g. on Google Cloud
GET_OPPORTUNITIES_VERBOSE = False # Will be overridden if also set as an environment variable e.g. on Google Cloud

# --------------------------------------------------------------------------------------------------

# Running analyse-opportunities

ANALYSE_OPPORTUNITIES_VERBOSE = True # Will be overridden if also set as an environment variable e.g. on Google Cloud

# --------------------------------------------------------------------------------------------------

HEADERS = {
    'timeout': '10',
    'User-Agent': 'OpenActive admin',
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', # Alternative 'User-Agent' based on laptop browser settings. Still doesn't seem to help some GCloud 403 errors though.
    'From': 'hello@openactive.io',
    'Referer': 'https://www.openactive.io',
}