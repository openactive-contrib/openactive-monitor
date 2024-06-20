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
            opportunities, get_opportunities_helper_done = get_opportunities_helper(opportunities, **kwargs)
            if (not get_opportunities_helper_done):
                sleep(seconds_wait_next)
            else:
                break
        opportunities['status'] = 'COMPLETE'
    except:
        opportunities['status'] = 'ERROR'
        set_message('Can\'t get feed: {}'.format(opportunities['nextUrl']), 'error')

    return opportunities

# --------------------------------------------------------------------------------------------------

def get_opportunities_helper(opportunities, **kwargs):
    feed_url = opportunities['nextUrl']
    feed_page, num_tries = try_requests(feed_url, **kwargs)

    if (feed_page.status_code != 200):
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
import lzma
import pickle
import sys
from datetime import datetime
# from openactive import get_opportunities
from os import getenv, listdir, remove
from os.path import isfile
from re import sub
from time import sleep

# --------------------------------------------------------------------------------------------------

FILENAME_FEEDS = 'feeds.pickle'
FILENAME_OPPORTUNITIES_SUFFIX = '.pickle.xz'
LEN_FILENAME_OPPORTUNITIES_SUFFIX = len(FILENAME_OPPORTUNITIES_SUFFIX)

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-all-data-harvester_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
FILEPATH_RELATIVE_FEEDS = getenv('FILEPATH_RELATIVE_FEEDS', '../volume-1/data-feeds')
FILEPATH_RELATIVE_OPPORTUNITIES = getenv('FILEPATH_RELATIVE_OPPORTUNITIES', '../volume-1/data-opportunities')

NUM_FEED_TRIES_MAX = 3 # Initial try plus retries
NUM_FEED_VERSIONS_TO_STORE_MAX = 1
NUM_FEEDS_MAX = int(getenv('NUM_FEEDS_MAX', '-1'))
NUM_FEEDS_MAX = None if NUM_FEEDS_MAX < 0 else NUM_FEEDS_MAX
SECONDS_PER_FEED_MAX = int(getenv('SECONDS_PER_FEED_MAX', '600'))

print('FILEPATH_RELATIVE_FEEDS:', FILEPATH_RELATIVE_FEEDS)
print('FILEPATH_RELATIVE_OPPORTUNITIES:', FILEPATH_RELATIVE_OPPORTUNITIES)
print('NUM_FEEDS_MAX:', NUM_FEEDS_MAX)
print('SECONDS_PER_FEED_MAX:', SECONDS_PER_FEED_MAX)

# --------------------------------------------------------------------------------------------------

with open(FILEPATH_RELATIVE_FEEDS + '/' + FILENAME_FEEDS, 'rb') as file_in:
    feeds = pickle.load(file_in)

# --------------------------------------------------------------------------------------------------

feed_urls_skip = [
    # 'https://opendata.leisurecloud.live/api/feeds/EveryoneActive-test-slots', # Crashed Jupyter one time, before timeout code was present
]
# For feeds that error during get_opportunities():
feed_urls_retry = {}

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
                self.value += f"--{part}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}"
            elif (part == 'timeTaken'):
                self.value += f"--{part}-{time_delta.seconds}-{time_delta.microseconds}"

# --------------------------------------------------------------------------------------------------

filenames_with_infostamp = None
# filenames_without_infostamp = None # Not currently using
def get_filenames():
    global filenames_with_infostamp
    # global filenames_without_infostamp
    filenames_with_infostamp = sorted([
        i[:-LEN_FILENAME_OPPORTUNITIES_SUFFIX]
        for i in listdir(FILEPATH_RELATIVE_OPPORTUNITIES)
        if (    (isfile(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + i))
            and (len(i) > LEN_FILENAME_OPPORTUNITIES_SUFFIX)
            and (i[-LEN_FILENAME_OPPORTUNITIES_SUFFIX:] == FILENAME_OPPORTUNITIES_SUFFIX)
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
@func_timeout.func_set_timeout(SECONDS_PER_FEED_MAX)
def run_get_opportunities(opportunities_in):
    global opportunities_out
    opportunities_out = None
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
            if ('--'.join(filename_with_infostamp.split('--')[:-Infostamp.num_parts]) == filename_without_infostamp_current)
        ])

        # --------------------------------------------------------------------------------------------------

        opportunities_in = None
        if (len(filenames_with_infostamp_current) == 0):
            opportunities_in = feed_url
        elif (refresh):
            with lzma.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_OPPORTUNITIES_SUFFIX, 'rb') as file_in:
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

                infostamp = Infostamp(opportunities_out, t1, t2).value
                filenames_with_infostamp_current.append(filename_without_infostamp_current + infostamp)

                with lzma.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_OPPORTUNITIES_SUFFIX, 'wb') as file_out:
                    pickle.dump(opportunities_out, file_out)

                if (len(filenames_with_infostamp_current) > NUM_FEED_VERSIONS_TO_STORE_MAX):
                    for filename_with_infostamp_current in filenames_with_infostamp_current[:-NUM_FEED_VERSIONS_TO_STORE_MAX]:
                        remove(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filename_with_infostamp_current + FILENAME_OPPORTUNITIES_SUFFIX)

            # --------------------------------------------------------------------------------------------------

            # Not currently retrying feeds that timeout, only retrying regular errors:
            if (NUM_FEED_TRIES_MAX > 1):
                if (    (opportunities_out is None)
                    or  (opportunities_out['status'] == 'ERROR')
                ):
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
                    feed_urls_retry[feed_url]['status'] = opportunities_out['status']

            # --------------------------------------------------------------------------------------------------

            print(datetime.now(), opportunities_out['status'] if opportunities_out is not None else 'ERROR')

    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    get_opportunities_done = False
    opportunities_out = None
    # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google
    # Cloud memory performance:
    # gc.collect()

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        print('Running first attempt of all feed URLs')
        get_filenames()
        for idx_feed_url, feed_url in enumerate([feed['url'] for feed in feeds['feeds'][0:NUM_FEEDS_MAX]]):
            harvester(idx_feed_url, feed_url, True)
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    try:
        num_feed_urls_retry_remaining = len(feed_urls_retry.keys())
        if (num_feed_urls_retry_remaining > 0):
            print(f'\nRunning retries ({num_feed_urls_retry_remaining})')
            print(feed_urls_retry.keys())
            while (num_feed_urls_retry_remaining > 0):
                get_filenames()
                for feed_url,feed_url_info in feed_urls_retry.items():
                    if (feed_url_info['num_feed_tries_remaining'] > 0):
                        harvester(feed_url_info['idx_feed_url'], feed_url, True)
                        if (feed_url_info['num_feed_tries_remaining'] == 0):
                            num_feed_urls_retry_remaining -= 1
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    print('Finished')