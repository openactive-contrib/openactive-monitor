import func_timeout
import lzma
import pickle
import sys
from datetime import datetime
from io import StringIO
from openactive import get_opportunities
from os import listdir, remove
from os.path import isfile
from re import sub
from time import sleep

# --------------------------------------------------------------------------------------------------

stdout_orig = sys.stdout

FILENAME_FEEDS = 'feeds.pickle'
FILENAME_SUFFIX = '.pickle.xz'
LEN_FILENAME_SUFFIX = len(FILENAME_SUFFIX)

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-all-data-harvester_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
FILEPATH_RELATIVE_FEEDS = '../volume-1/data-feeds'
FILEPATH_RELATIVE_OPPORTUNITIES = '../volume-1/data-opportunities'

SECONDS_PER_FEED_MAX = 600
NUM_FEED_TRIES_MAX = 3 # Initial try plus retries
NUM_FEED_VERSIONS_TO_STORE_MAX = 1

# --------------------------------------------------------------------------------------------------

with open(FILEPATH_RELATIVE_FEEDS + '/' + FILENAME_FEEDS, 'rb') as file_in:
    feeds = pickle.load(file_in)

# --------------------------------------------------------------------------------------------------

feed_urls_skip = [
    # 'https://opendata.leisurecloud.live/api/feeds/EveryoneActive-test-slots', # Crashed Jupyter one time, before timeout code was present
]
# For feeds that result in "ERROR: Can't get feed":
feed_urls_retry = {}

# --------------------------------------------------------------------------------------------------

def set_infostamp(opportunities_out, error, timeout, t1, t2):
    time_delta = t2 - t1
    return \
        f"--status-{'ERROR' if error else 'TIMEOUT' if timeout else 'COMPLETE'}" + \
        f"--urls-{len(opportunities_out['urls'])}" + \
        f"--items-{len(opportunities_out['items'].keys())}" + \
        f"--timeFinish-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}" + \
        f"--timeTaken-{time_delta.seconds}-{time_delta.microseconds}"

# --------------------------------------------------------------------------------------------------

filenames_with_infostamp = None
# filenames_without_infostamp = None # Not currently used
def get_filenames():
    global filenames_with_infostamp
    # global filenames_without_infostamp
    filenames_with_infostamp = sorted([
        i[:-LEN_FILENAME_SUFFIX]
        for i in listdir(FILEPATH_RELATIVE_OPPORTUNITIES)
        if isfile(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + i)
        and len(i) > LEN_FILENAME_SUFFIX
        and i[-LEN_FILENAME_SUFFIX:] == FILENAME_SUFFIX
    ])
    # filenames_without_infostamp = sorted(set([
    #     '--'.join(i.split('--')[:-5])
    #     for i in filenames_with_infostamp
    # ]))

# --------------------------------------------------------------------------------------------------

# We wrap get_opportunities with Test_get_opportunities_done to test when it's done, regardless of
# its output i.e. we don't rely on checking if opportunities_out is not None, which it perhaps could
# be even if the function is done but something went wrong. This is important when get_opportunities
# is timed out, as it is the run_get_opportunities wrapper function which is primarily timed out and
# get_opportunities lags behind a bit and can still produce non-negligible output that we don't want
# to lose, so we must check to see when it's actually done in order to capture the output:
get_opportunities_done = False
class Test_get_opportunities_done:
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback): # All arguments are needed in this definition to ensure that exit occurs properly
        global get_opportunities_done
        get_opportunities_done = True

# --------------------------------------------------------------------------------------------------

# We wrap get_opportunities with run_get_opportunities and use a global opportunities_out in order
# to access this output even if the function is timed out, as func_timeout would otherwise lose
# the output if it wrapped get_opportunities directly:
opportunities_out = None
@func_timeout.func_set_timeout(SECONDS_PER_FEED_MAX)
def run_get_opportunities(opportunities_in):
    global opportunities_out
    with Test_get_opportunities_done():
        opportunities_out = get_opportunities(opportunities_in)

# --------------------------------------------------------------------------------------------------

# The refresh keyword means whether or not a given feed_url will be run again if it already has a file
# present from a previous run. It's useful to set this to False if a run fails part-way through the
# full list of feed_urls, and you want to start again but without redoing the ones that were already
# dealt with.
def harvester(idx_feed_url, feed_url, refresh=True):
    print(datetime.now(), idx_feed_url, feed_url)

    # --------------------------------------------------------------------------------------------------

    if (feed_url in feed_urls_skip):
        print('Feed URL is in skip list, skipping')
        return

    # --------------------------------------------------------------------------------------------------

    global get_opportunities_done
    global opportunities_out

    # --------------------------------------------------------------------------------------------------

    try:
        filename_without_infostamp_current = sub('https://|http://|www.', '', feed_url).replace('.', '-').replace('/', '-').strip('-')
        filenames_with_infostamp_current = sorted([
            filename_with_infostamp
            for filename_with_infostamp in filenames_with_infostamp
            if ('--'.join(filename_with_infostamp.split('--')[:-5]) == filename_without_infostamp_current)
        ])

        # --------------------------------------------------------------------------------------------------

        if (len(filenames_with_infostamp_current) == 0):
            opportunities_in = feed_url
        elif (refresh):
            with lzma.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_SUFFIX, 'rb') as file_in:
                opportunities_in = pickle.load(file_in)
        else:
            opportunities_in = None

        # --------------------------------------------------------------------------------------------------

        if (opportunities_in is not None):

            sys.stdout = StringIO()
            try:
                t1 = datetime.now()
                run_get_opportunities(opportunities_in)
                timeout = False
                error = 'ERROR: Can\'t get feed' in sys.stdout.getvalue()
                message = sys.stdout.getvalue() if error else ''
            except func_timeout.FunctionTimedOut:
                timeout = True
                error = False
                message = 'TIMEOUT'
            sys.stdout = stdout_orig

            # --------------------------------------------------------------------------------------------------

            # Currently not retrying feeds that timeout, only retrying regular errors:
            if (error):
                if (feed_url not in feed_urls_retry.keys()):
                    feed_urls_retry[feed_url] = {
                        'idx_feed_url': idx_feed_url,
                        'num_feed_tries_remaining': NUM_FEED_TRIES_MAX - 1,
                        'status': 'ERROR',
                    }
                else:
                    feed_urls_retry[feed_url]['num_feed_tries_remaining'] -= 1
            elif (feed_url in feed_urls_retry.keys()):
                feed_urls_retry[feed_url]['num_feed_tries_remaining'] = 0
                feed_urls_retry[feed_url]['status'] = 'TIMEOUT' if timeout else 'COMPLETE'

            # --------------------------------------------------------------------------------------------------

            if (message):
                print(message)

            # --------------------------------------------------------------------------------------------------

            # get_opportunities should always complete even if forcibly timed out, so let's wait for it in order
            # to get opportunities_out even if it only has partial content from cancellation part-way through the
            # RPDE chain:
            # t1a = datetime.now()
            while (not get_opportunities_done):
                sleep(1)
            # t2a = datetime.now()
            # print('Time taken for get_opportunities to complete after run_get_opportunities is complete:', t2a - t1a)

            # --------------------------------------------------------------------------------------------------

            if (opportunities_out is not None):
                t2 = datetime.now()

                infostamp = set_infostamp(opportunities_out, error, timeout, t1, t2)
                filenames_with_infostamp_current.append(filename_without_infostamp_current + infostamp)

                with lzma.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_SUFFIX, 'wb') as file_out:
                    pickle.dump(opportunities_out, file_out)

                if (len(filenames_with_infostamp_current) > NUM_FEED_VERSIONS_TO_STORE_MAX):
                    for filename_with_infostamp_current in filenames_with_infostamp_current[:-NUM_FEED_VERSIONS_TO_STORE_MAX]:
                        remove(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filename_with_infostamp_current + FILENAME_SUFFIX)

    except Exception as e:
        sys.stdout = stdout_orig
        print('ERROR:', e)

    # --------------------------------------------------------------------------------------------------

    get_opportunities_done = False
    opportunities_out = None

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        print('Running first attempt of all feed URLs')
        get_filenames()
        for idx_feed_url, feed_url in enumerate([feed['url'] for feed in feeds['feeds']]):
            harvester(idx_feed_url, feed_url, True) # Set refresh to True for production
    except Exception as e:
        print('ERROR:', e)
        sys.exit(1)

    try:
        num_feed_urls_retry_remaining = sum([
            1
            for feed_url_info in feed_urls_retry.values()
            if feed_url_info['num_feed_tries_remaining'] > 0
        ])
        if (num_feed_urls_retry_remaining > 0):
            print(f'\nRunning retries ({len(feed_urls_retry.keys())})')
            print(feed_urls_retry.keys())
            while (num_feed_urls_retry_remaining > 0):
                get_filenames()
                for feed_url,feed_url_info in feed_urls_retry.items():
                    if (feed_url_info['num_feed_tries_remaining'] > 0):
                        harvester(feed_url_info['idx_feed_url'], feed_url, True)
                        if (feed_url_info['num_feed_tries_remaining'] == 0):
                            num_feed_urls_retry_remaining -= 1
    except Exception as e:
        print('ERROR:', e)
        sys.exit(1)

    print('Done')