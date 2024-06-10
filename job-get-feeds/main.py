import pickle
import sys
from datetime import datetime
from openactive import get_feeds

# --------------------------------------------------------------------------------------------------

FILENAME_FEEDS = 'feeds.pickle'
# This folder must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-feeds', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-feeds \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-all-data-harvester_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
FILEPATH_RELATIVE_FEEDS = '../volume-1/data-feeds'

# --------------------------------------------------------------------------------------------------

def run_get_feeds():
    t1 = datetime.now()
    feeds = get_feeds(flat=True)
    t2 = datetime.now()

    pickle.dump(
        {
            'time_start': str(t1),
            'time_finish': str(t2),
            'time_taken': str(t2 - t1),
            'num_feeds': len(feeds),
            'feeds': feeds,
        },
        open(FILEPATH_RELATIVE_FEEDS + '/' + FILENAME_FEEDS, 'wb')
    )

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        run_get_feeds()
    except Exception as e:
        print('ERROR:', e)
        sys.exit(1)