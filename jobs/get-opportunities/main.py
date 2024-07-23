# The following code up to and including get_opportunities_next_url() is a custom version of code from
# the OpenActive Python library v2.0.0. This is to modify get_opportunities() by making it non-recursive,
# as the standard recursive behaviour is suspected of giving a possible memory leak. Also, Python limits
# recursion to 1000 levels by default, and get_opportunities() may well go beyond this limit for feeds
# with more than 1000 RPDE pages, which is not unseen. Even though this default limit can be changed,
# it's best to avoid the issue entirely by removing the need for recursion entirely, and that's what's
# done here by augmenting get_opportunities() with get_opportunities_helper().

import copy
import requests
from inspect import stack
from urllib.parse import unquote, urlparse

# --------------------------------------------------------------------------------------------------

SECONDS_WAIT_NEXT_DEFAULT = 0.2

# --------------------------------------------------------------------------------------------------

def set_message(message, message_type=None):
    if (message_type == 'calling'):
        print('CALLING: ' + message)
    elif (message_type == 'warning'):
        print('WARNING: ' + message)
    elif (message_type == 'error'):
        print('ERROR: ' + message)
    else:
        print(message)

# --------------------------------------------------------------------------------------------------

session = requests.Session()

# https://stackoverflow.com/a/65576055
# https://stackoverflow.com/a/72666365

# When making several requests to the same host, requests.get() can result in errors. For more robust
# behaviour, requests.Session().get() is used herein. If there are further issues, then try uncommenting
# the following code for even more supportive behaviour:

# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
# retry_strategy = Retry(
#   total=3,
#   backoff_factor=1
# )
# adapter = HTTPAdapter(max_retries=retry_strategy)
# session.mount('https://', adapter)
# session.mount('http://', adapter)

def try_requests(url, **kwargs):
    verbose = kwargs.get('verbose', False)
    seconds_wait_retry = kwargs.get('seconds_wait_retry', 1)
    num_tries_max = kwargs.get('num_tries_max', 10)

    r = None
    num_tries = 0

    while (True):
        if (num_tries == num_tries_max):
            set_message('Max. tries ({}) reached for: {}'.format(num_tries_max, url), 'warning')
            break
        elif (num_tries > 0):
            set_message('Retrying ({}/{}): {}'.format(num_tries, num_tries_max-1, url), 'warning')
            sleep(seconds_wait_retry)
        try:
            if (verbose):
                set_message(url, 'calling')
            num_tries += 1
            r = session.get(url)
            if (r.status_code == 200):
                break
        except Exception as error:
            set_message(str(error), 'error')
            # Continue otherwise we get kicked out of the while loop. This takes us to the top of the loop:
            continue

    return r, num_tries

# --------------------------------------------------------------------------------------------------

opportunities_template = {
    'items': {},
    'urls': [],
    'firstUrlOrigin': '',
    'nextUrl': '',
    'status': '',
}

def get_opportunities(arg, **kwargs):
    verbose = kwargs.get('verbose', False)
    seconds_wait_next = kwargs.get('seconds_wait_next', SECONDS_WAIT_NEXT_DEFAULT)

    if (    (verbose)
        and (stack()[0].function != stack()[1].function)
    ):
        print(stack()[0].function)

    if (type(arg) == str):
        if (len(arg) == 0):
            set_message('Invalid input, feed URL must be a string of non-zero length', 'warning')
            return
        opportunities = copy.deepcopy(opportunities_template)
        opportunities['nextUrl'] = get_opportunities_next_url(arg, opportunities)
    elif (type(arg) == dict):
        if (    (sorted(arg.keys()) != sorted(opportunities_template.keys()))
            or  (any([type(arg[key]) != type(opportunities_template[key]) for key in arg.keys()]))
            or  (len(arg['firstUrlOrigin']) == 0)
            or  (len(arg['nextUrl']) == 0)
        ):
            set_message('Invalid input, opportunities must be a dictionary with the expected content', 'warning')
            return
        opportunities = arg
    else:
        set_message('Invalid input, must be a feed URL string or an opportunities dictionary', 'warning')
        return

    try:
        while (True):
            feed_url = opportunities['nextUrl']
            opportunities, get_opportunities_helper_done = get_opportunities_helper(opportunities, **kwargs)
            if (not get_opportunities_helper_done):
                sleep(seconds_wait_next)
            else:
                break
        opportunities['status'] = 'COMPLETE'
    except:
        opportunities['status'] = 'ERROR'
        set_message('Issue encountered when getting feed: {}'.format(feed_url), 'error')

    return opportunities

# --------------------------------------------------------------------------------------------------

def get_opportunities_helper(opportunities, **kwargs):
    feed_url = opportunities['nextUrl']
    feed_page, num_tries = try_requests(feed_url, **kwargs)

    if (    (feed_page is None)
        or  (feed_page.status_code != 200)
    ):
        raise Exception()

    for item in feed_page.json()['items']:
        if (all([key in item.keys() for key in ['id', 'state', 'modified']])):
            if (item['state'] == 'updated'):
                if (    (item['id'] not in opportunities['items'].keys())
                    or  (item['modified'] > opportunities['items'][item['id']]['modified'])
                ):
                    opportunities['items'][item['id']] = item
            elif (  (item['state'] == 'deleted')
                and (item['id'] in opportunities['items'].keys())
            ):
                del(opportunities['items'][item['id']])

    # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google
    # Cloud memory performance:
    # gc.collect()

    if (    ('next' in feed_page.json().keys())
        and (type(feed_page.json()['next']) == str)
        and (len(feed_page.json()['next']) > 0)
    ):
        opportunities['nextUrl'] = get_opportunities_next_url(feed_page.json()['next'], opportunities)
    else:
        opportunities['nextUrl'] = ''

    if (opportunities['nextUrl'] != feed_url):
        opportunities['urls'].append(feed_url)

    get_opportunities_helper_done = opportunities['nextUrl'] in ['', feed_url]

    return opportunities, get_opportunities_helper_done

# --------------------------------------------------------------------------------------------------

def get_opportunities_next_url(next_url_original, opportunities):
    next_url = ''

    next_url_original_unquoted = unquote(next_url_original)
    next_url_original_parsed = urlparse(next_url_original_unquoted)

    if (    (next_url_original_parsed.scheme != '')
        and (next_url_original_parsed.netloc != '')
    ):
        if (len(opportunities['urls']) == 0):
            opportunities['firstUrlOrigin'] = '://'.join([next_url_original_parsed.scheme, next_url_original_parsed.netloc])
        next_url = next_url_original_unquoted
    elif (  (next_url_original_parsed.path != '')
        or  (next_url_original_parsed.query != '')
    ):
        next_url = opportunities['firstUrlOrigin']
        if (next_url_original_parsed.path != ''):
            next_url += ('/' if (next_url_original_parsed.path[0] != '/') else '') + next_url_original_parsed.path
        if (next_url_original_parsed.query != ''):
            next_url += ('?' if (next_url_original_parsed.query[0] != '?') else '') + next_url_original_parsed.query

    return next_url

# --------------------------------------------------------------------------------------------------

# The above code should be incorporated into the OpenActive Python library. The main code of interest
# for the Google Cloud job being developed begins here.

import func_timeout
# import gc # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google Cloud memory performance
import gzip
import lzma
import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_opportunities
from os import getenv, listdir, remove
from os.path import isfile
from re import sub
from time import sleep

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_FEEDS = getenv('RELATIVE_FILEPATH_FEEDS', '../volume-1/data-feeds')
RELATIVE_FILEPATH_OPPORTUNITIES = getenv('RELATIVE_FILEPATH_OPPORTUNITIES', '../volume-1/data-opportunities')

FILENAME_FEEDS = 'feeds.pickle' # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_SEEN = '000_feeds_seen.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAME_FEEDS_CRASHED = '000_feeds_crashed.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAMES_SKIP = [FILENAME_FEEDS_SEEN, FILENAME_FEEDS_CRASHED] # Filenames to skip when checking for opportunity files in RELATIVE_FILEPATH_OPPORTUNITIES
FORMAT_FILE_OPPORTUNITIES = 'pickle'
COMPRESSION_FILE_OPPORTUNITIES = getenv('COMPRESSION_FILE_OPPORTUNITIES', 'gzip').lower() # 'none' / 'gzip' / 'xz'
SUFFIX_FILENAME_OPPORTUNITIES = '.' + FORMAT_FILE_OPPORTUNITIES + (('.' + COMPRESSION_FILE_OPPORTUNITIES) if (COMPRESSION_FILE_OPPORTUNITIES != 'none') else '')
LEN_SUFFIX_FILENAME_OPPORTUNITIES = len(SUFFIX_FILENAME_OPPORTUNITIES)

MAX_NUM_FEEDS = int(getenv('MAX_NUM_FEEDS', '-1'))
MAX_NUM_FEEDS = None if (MAX_NUM_FEEDS < 0) else MAX_NUM_FEEDS # Negative indicates to do all feeds, otherwise cap at the stated number of feeds. This is useful for testing on a subset of all feeds.
MAX_NUM_FEED_SECONDS = int(getenv('MAX_NUM_FEED_SECONDS', '600'))
MAX_NUM_FEED_TRIES = int(getenv('MAX_NUM_FEED_TRIES', '3')) # Initial try plus retries in one run of this code
MAX_NUM_FEED_FILES = int(getenv('MAX_NUM_FEED_FILES', '1')) # Number of historical outputs to keep for each feed, including the latest output
VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

print('Environment variables:')
print('RELATIVE_FILEPATH_FEEDS:', RELATIVE_FILEPATH_FEEDS)
print('RELATIVE_FILEPATH_OPPORTUNITIES:', RELATIVE_FILEPATH_OPPORTUNITIES)
print('COMPRESSION_FILE_OPPORTUNITIES:', COMPRESSION_FILE_OPPORTUNITIES)
print('MAX_NUM_FEEDS:', MAX_NUM_FEEDS)
print('MAX_NUM_FEED_SECONDS:', MAX_NUM_FEED_SECONDS)
print('MAX_NUM_FEED_TRIES:', MAX_NUM_FEED_TRIES)
print('MAX_NUM_FEED_FILES:', MAX_NUM_FEED_FILES)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

class Infostamp:
    # Files of the same filename prefix are later grouped and alphabetically sorted to determine the order
    # in which they were made, and to then delete earlier ones. It's therefore important that 'timeFinish'
    # is the first part of the filename infostamp suffix. Other parts can appear in any order. The alternative
    # would be to break down the infostamp and seek the 'timeFinish' part when sorting, which is a bit
    # more work and not necessary at the time of writing (2024-06-20):
    parts = [
        'timeFinish',
        'timeTaken',
        'numItems',
        'numUrls',
        'status',
    ]

    # This is important to know outside of this class for when the filename is broken into parts, in order
    # to know how many of the parts form the infostamp suffix:
    num_parts = len(parts)

    def __init__(self, opportunities, t1, t2):
        time_delta = t2 - t1
        self.value = ''
        for part in Infostamp.parts:
            if (part == 'numItems'):
                self.value += f"--{part}-{len(opportunities['items'].keys())}"
            elif (part == 'numUrls'):
                self.value += f"--{part}-{len(opportunities['urls'])}"
            elif (part == 'status'):
                self.value += f"--{part}-{opportunities['status']}"
            elif (part == 'timeFinish'):
                self.value += f"--{part}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}-UTC"
            elif (part == 'timeTaken'):
                self.value += f"--{part}-{time_delta.seconds}-{time_delta.microseconds}"

# --------------------------------------------------------------------------------------------------

filenames_with_infostamp = None
# filenames_without_infostamp = None # Not currently using
def get_filenames():
    global filenames_with_infostamp
    # global filenames_without_infostamp
    filenames_with_infostamp = sorted([
        i[:-LEN_SUFFIX_FILENAME_OPPORTUNITIES]
        for i in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)
        if (    (isfile(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + i))
            and (i not in FILENAMES_SKIP)
            and (len(i) > LEN_SUFFIX_FILENAME_OPPORTUNITIES)
            and (i[-LEN_SUFFIX_FILENAME_OPPORTUNITIES:] == SUFFIX_FILENAME_OPPORTUNITIES)
        )
    ])
    # filenames_without_infostamp = sorted(set([
    #     '--'.join(i.split('--')[:-Infostamp.num_parts])
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
        global get_opportunities_done
        get_opportunities_done = False
    def __exit__(self, type, value, traceback): # All arguments are needed in this definition to ensure that exit occurs properly
        global get_opportunities_done
        get_opportunities_done = True

# --------------------------------------------------------------------------------------------------

# We wrap get_opportunities with run_get_opportunities and use a global opportunities_out in order
# to access this output even if the function is timed out, as func_timeout would otherwise lose
# the output if it wrapped get_opportunities directly:
opportunities_out = None
@func_timeout.func_set_timeout(MAX_NUM_FEED_SECONDS)
def run_get_opportunities(opportunities_in):
    global opportunities_out
    opportunities_out = None
    with Test_get_opportunities_done():
        opportunities_out = get_opportunities(opportunities_in, verbose=VERBOSE)

# --------------------------------------------------------------------------------------------------

feed_urls_skip = [
    # 'https://opendata.leisurecloud.live/api/feeds/EveryoneActive-test-slots', # Crashed Jupyter one time, before timeout code was present
]
# For feeds that error during get_opportunities():
feed_urls_retry = {}

# The refresh keyword means whether or not a given feed_url will be run again if it already has a file
# present from a previous run. It's useful to set this to False if a run fails part-way through the
# full list of feed_urls, and you want to start again but without redoing the ones that were already
# dealt with.
def harvester(idx_feed_url, feed_url, refresh=True):
    global get_opportunities_done
    global opportunities_out

    # --------------------------------------------------------------------------------------------------

    try:
        filename_without_infostamp_current = sub('https://|http://|www.', '', feed_url).replace('.', '-').replace('/', '-').strip('-')
        filenames_with_infostamp_current = sorted([
            filename_with_infostamp
            for filename_with_infostamp in filenames_with_infostamp
            if ('--'.join(filename_with_infostamp.split('--')[:-Infostamp.num_parts]) == filename_without_infostamp_current)
        ])

        # --------------------------------------------------------------------------------------------------

        opportunities_in = None
        if (len(filenames_with_infostamp_current) == 0):
            opportunities_in = feed_url
        elif (refresh):
            relative_filepath_opportunities_in = RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + SUFFIX_FILENAME_OPPORTUNITIES
            if (COMPRESSION_FILE_OPPORTUNITIES == 'none'):
                with open(relative_filepath_opportunities_in, 'rb') as file_in:
                    opportunities_in = pickle.load(file_in)
            elif (COMPRESSION_FILE_OPPORTUNITIES == 'gzip'):
                with gzip.open(relative_filepath_opportunities_in, 'rb') as file_in:
                    opportunities_in = pickle.load(file_in)
            elif (COMPRESSION_FILE_OPPORTUNITIES == 'xz'):
                with lzma.open(relative_filepath_opportunities_in, 'rb') as file_in:
                    opportunities_in = pickle.load(file_in)

        # --------------------------------------------------------------------------------------------------

        if (opportunities_in is not None):
            t1 = datetime.now()

            try:
                run_get_opportunities(opportunities_in)
                timeout = False
            except func_timeout.FunctionTimedOut:
                timeout = True

            # get_opportunities should always complete even if forcibly timed out, so let's wait for it in order
            # to get opportunities_out even if it only has partial content from cancellation part-way through the
            # RPDE chain:
            # t1a = datetime.now()
            while (not get_opportunities_done):
                sleep(1)
            # t2a = datetime.now()
            # print('Time taken for get_opportunities to complete after run_get_opportunities is complete:', t2a - t1a)

            t2 = datetime.now()

            # --------------------------------------------------------------------------------------------------

            if (opportunities_out is not None):
                if (timeout):
                    opportunities_out['status'] = 'TIMEOUT'

                filenames_with_infostamp_current.append(filename_without_infostamp_current + Infostamp(opportunities_out, t1, t2).value)
                relative_filepath_opportunities_out = RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + SUFFIX_FILENAME_OPPORTUNITIES

                if (COMPRESSION_FILE_OPPORTUNITIES == 'none'):
                    with open(relative_filepath_opportunities_out, 'wb') as file_out:
                        pickle.dump(opportunities_out, file_out)
                elif (COMPRESSION_FILE_OPPORTUNITIES == 'gzip'):
                    with gzip.open(relative_filepath_opportunities_out, 'wb') as file_out:
                        pickle.dump(opportunities_out, file_out)
                elif (COMPRESSION_FILE_OPPORTUNITIES == 'xz'):
                    with lzma.open(relative_filepath_opportunities_out, 'wb') as file_out:
                        pickle.dump(opportunities_out, file_out)

                if (len(filenames_with_infostamp_current) > MAX_NUM_FEED_FILES):
                    for filename_with_infostamp_current in filenames_with_infostamp_current[:-MAX_NUM_FEED_FILES]:
                        remove(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filename_with_infostamp_current + SUFFIX_FILENAME_OPPORTUNITIES)

            # --------------------------------------------------------------------------------------------------

            # Not currently retrying feeds that timeout, only retrying regular errors:
            if (MAX_NUM_FEED_TRIES > 1):
                if (    (opportunities_out is None)
                    or  (opportunities_out['status'] == 'ERROR')
                ):
                    if (feed_url not in feed_urls_retry.keys()):
                        feed_urls_retry[feed_url] = {
                            'idx_feed_url': idx_feed_url,
                            'num_feed_tries_remaining': MAX_NUM_FEED_TRIES - 1,
                            'status': 'ERROR',
                        }
                    else:
                        feed_urls_retry[feed_url]['num_feed_tries_remaining'] -= 1
                elif (feed_url in feed_urls_retry.keys()):
                    feed_urls_retry[feed_url]['num_feed_tries_remaining'] = 0
                    feed_urls_retry[feed_url]['status'] = opportunities_out['status']

            # --------------------------------------------------------------------------------------------------

            print(idx_feed_url, feed_url, opportunities_out['status'] if (opportunities_out is not None) else 'ERROR')

    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    get_opportunities_done = False
    opportunities_out = None
    # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google
    # Cloud memory performance:
    # gc.collect()

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
    try:
        print('Started first attempt of all feed URLs')

        with open(RELATIVE_FILEPATH_FEEDS + '/' + FILENAME_FEEDS, 'rb') as file_in:
            feeds = pickle.load(file_in)

        get_filenames()

        # FILENAME_FEEDS_SEEN is deleted at the end of a full successful run of harvesting all feeds, so if
        # this file exists at this point it means that this is not the first time we've run the code, which
        # in turn means that we had a forced stop during the previous run, either because of manual intervention
        # or a crash. Taking the latter as the standard production scenario, as manual intervention should
        # only be done when testing, we then have that the last feed to be written to FILENAME_FEEDS_SEEN may
        # itself have been the ultimate cause of the crash. We therefore add that feed to FILENAME_FEEDS_CRASHED
        # and ignore these feeds in further processing attempts.
        if (FILENAME_FEEDS_SEEN in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)):
            with open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_SEEN, 'r') as file_in:
                date_time_feed_urls_seen = file_in.read().strip('\n').split('\n')
                feed_urls_seen = [date_time_feed_url_seen.split()[2] for date_time_feed_url_seen in date_time_feed_urls_seen]
            with open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_CRASHED, 'a') as file_out:
                file_out.write(date_time_feed_urls_seen[-1] + '\n')
        else:
            feed_urls_seen = []

        for idx_feed_url, feed_url in enumerate([feed['url'] for feed in feeds['feeds'][0:MAX_NUM_FEEDS]]):
            print(idx_feed_url, feed_url, 'START')

            if (feed_url in feed_urls_skip):
                print('Feed URL in skip list, skipping')
                continue

            if (feed_url not in feed_urls_seen):
                with open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_SEEN, 'a') as file_out:
                    file_out.write(str(datetime.now()) + ' ' + feed_url + '\n')
                harvester(idx_feed_url, feed_url, True)
            else:
                feed_urls_seen.remove(feed_url)
                print('Feed URL seen, skipping')

        if (FILENAME_FEEDS_SEEN in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)):
            remove(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_SEEN)
        # if (FILENAME_FEEDS_CRASHED in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)):
        #     remove(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_CRASHED)

        print('Finished first attempt of all feed URLs')

    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    try:
        num_feed_urls_retry_remaining = len(feed_urls_retry.keys())

        if (num_feed_urls_retry_remaining > 0):

            print(f'\nStarted retries ({num_feed_urls_retry_remaining})')
            print(feed_urls_retry.keys())

            while (num_feed_urls_retry_remaining > 0):
                get_filenames()
                for feed_url, feed_url_info in feed_urls_retry.items():
                    if (feed_url_info['num_feed_tries_remaining'] > 0):
                        harvester(feed_url_info['idx_feed_url'], feed_url, True)
                        if (feed_url_info['num_feed_tries_remaining'] == 0):
                            num_feed_urls_retry_remaining -= 1

            print('Finished retries')

    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    try:
        run_job('analyse-opportunities')
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')