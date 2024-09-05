import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_feeds
from os import getenv

sys.path.append('../volume-1/common')
from openactive_custom import get_feeds

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-feeds', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-feeds \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_FEEDS = getenv('RELATIVE_FILEPATH_FEEDS', '../volume-1/data-feeds')

FILENAME_FEEDS = getenv('FILENAME_FEEDS', 'feeds.pickle') # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_PREVIEW = getenv('FILENAME_FEEDS_PREVIEW', 'feeds-preview.pickle') # Located in RELATIVE_FILEPATH_FEEDS

VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

HEADERS = {
    'timeout': '10',
    'User-Agent': 'OpenActive admin',
    # Alternative 'User-Agent' based on laptop browser settings. Still doesn't seem to help some GCloud 403 errors though:
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'From': 'hello@openactive.io',
    'Referer': 'https://www.openactive.io',
}

print('Environment variables:')
print('RELATIVE_FILEPATH_FEEDS:', RELATIVE_FILEPATH_FEEDS)
print('FILENAME_FEEDS:', FILENAME_FEEDS)
print('FILENAME_FEEDS_PREVIEW:', FILENAME_FEEDS_PREVIEW)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

def run_get_feeds(**kwargs):
    preview = kwargs.get('preview', False)

    t1 = datetime.now()
    feeds = get_feeds(**{**kwargs, **{'flat': True}})
    t2 = datetime.now()

    with open(RELATIVE_FILEPATH_FEEDS + '/' + (FILENAME_FEEDS_PREVIEW if preview else FILENAME_FEEDS), 'wb') as file_out:
        pickle.dump(
            {
                'time_start': str(t1),
                'time_finish': str(t2),
                'time_taken': str(t2 - t1),
                'num_feeds': len(feeds),
                'feeds': feeds,
            },
            file_out
        )

# --------------------------------------------------------------------------------------------------

def run_job(name_job):
    publisher = pubsub_v1.PublisherClient()
    future = publisher.publish(
        publisher.topic_path('openactive-monitor', 'run-job'),
        name_job.encode('utf-8')
    )
    future.result()

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    # Temporarily disabled as GCloud is not getting all feeds for some reason, so just using feeds from
    # local run instead:
    # for preview in [False, True]:
    #     try:
    #         run_get_feeds(
    #             headers = HEADERS,
    #             preview = preview,
    #             verbose = VERBOSE,
    #         )
    #     except Exception as error:
    #         print('ERROR:', error)
    #         sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    try:
        run_job('get-opportunities')
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')