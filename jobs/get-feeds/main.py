import csv
import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_feeds
from os import getenv, remove, symlink

sys.path.append('../volume-1/common')
from fileutils import FilenameStamp, get_filenames, get_current_filenames
from openactive_custom import get_feeds
from settings import *

# --------------------------------------------------------------------------------------------------

VERBOSE = getenv('VERBOSE', str(GET_FEEDS_VERBOSE)).title()
VERBOSE = True if (VERBOSE == 'True') else False

# --------------------------------------------------------------------------------------------------

def run_get_feeds(**kwargs):
    preview = kwargs.get('preview', False)

    # --------------------------------------------------------------------------------------------------

    t1 = datetime.now()
    feeds = get_feeds(**{**kwargs, **{'flat': True}})
    t2 = datetime.now()

    # --------------------------------------------------------------------------------------------------

    current_filename_base = PREVIEW_FEEDS_FILENAME_BASE if preview else REGULAR_FEEDS_FILENAME_BASE
    current_filename = \
        current_filename_base + \
        FilenameStamp('feeds', t1, t2, {'numFeeds': len(feeds), 'numDatasets': len(set([feed['dataset_url'] for feed in feeds]))}).value + \
        FEEDS_FILENAME_SUFFIX

    with open(FEEDS_RELATIVE_FILEPATH + '/' + current_filename, 'wb') as file_out:
        pickle.dump(feeds, file_out)

    filenames = get_filenames('feeds')
    current_filenames = get_current_filenames('feeds', current_filename_base, filenames)

    if (len(current_filenames) > MAX_NUM_FEEDS_FILES):
        for filename in current_filenames[:-MAX_NUM_FEEDS_FILES]:
            try:
                remove(FEEDS_RELATIVE_FILEPATH + '/' + filename)
            except:
                pass

    # --------------------------------------------------------------------------------------------------

    # By the above code, a new file with a unique filename stamp will be made every time this code is run.
    # In other jobs we just want the latest version, and rather than having those jobs check all filename
    # stamps we instead use this job to make a constantly named symlink file, which can always be taken
    # as referring to the latest content without actually duplicating it. Note that the relative filepath
    # is only needed on the location of the symlink file being made, as symlinks are relative to their point
    # of use and the file being referred to is already at that location:

    current_latest_filename = PREVIEW_FEEDS_LATEST_FILENAME if preview else REGULAR_FEEDS_LATEST_FILENAME

    try:
        remove(FEEDS_RELATIVE_FILEPATH + '/' + current_latest_filename)
    except:
        pass

    symlink(current_filename, FEEDS_RELATIVE_FILEPATH + '/' + current_latest_filename)

    # --------------------------------------------------------------------------------------------------

    current_history_filename = PREVIEW_FEEDS_HISTORY_FILENAME if preview else REGULAR_FEEDS_HISTORY_FILENAME

    current_historical_filenames = []
    current_feed_urls_records = {}

    try:
        with open(FEEDS_RELATIVE_FILEPATH + '/' + current_history_filename, 'r') as file_in:
            csv_reader = csv.reader(file_in)
            for row in csv_reader:
                if (csv_reader.line_num == 1):
                    current_historical_filenames = row[1:]
                else:
                    current_feed_urls_records[row[0]] = row[1:]
    except:
        pass

    num_current_historical_filenames = len(current_historical_filenames)
    for feed_url in sorted(set([feed['url'] for feed in feeds])):
        if (feed_url in current_feed_urls_records.keys()):
            current_feed_urls_records[feed_url].append('y')
        else:
            current_feed_urls_records[feed_url] = num_current_historical_filenames * [''] + ['y']

    with open(FEEDS_RELATIVE_FILEPATH + '/' + current_history_filename, 'w') as file_out:
        csv_writer = csv.writer(file_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['feed_url'] + current_historical_filenames + [current_filename])
        for key, val in current_feed_urls_records.items():
            csv_writer.writerow([key] + val)

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
    for preview in [False, True]:
        try:
            run_get_feeds(
                headers = HEADERS,
                preview = preview,
                verbose = VERBOSE,
            )
        except Exception as error:
            print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    # For running on Google Cloud to trigger the next job, comment out if running locally:
    try:
        run_job('get-opportunities')
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')