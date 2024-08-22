# The following code up to and including get_opportunities_next_url() is a custom version of code from
# the OpenActive Python library v2.0.0. Modifications are:
# - try_requests
#   - Headers given
#   - None handling
#   - An alternative approach to requests.Session() is noted
# - get_opportunities:
#   - Non-recursive
#   - Memory logging
#   - Timeout

import copy
import requests
from inspect import stack
from urllib.parse import unquote, urlparse

# --------------------------------------------------------------------------------------------------

SECONDS_TIMEOUT_DEFAULT = 600
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

def get_bytesize(arg):
    bytesize = 0
    if (type(arg) == list):
        bytesize = sum([get_bytesize(val) for val in arg])
    elif (type(arg) == dict):
        bytesize = sum([get_bytesize(val) for val in arg.values()])
    else:
        bytesize = sys.getsizeof(arg)
    return bytesize

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
#     total=3,
#     backoff_factor=1
# )
# adapter = HTTPAdapter(max_retries=retry_strategy)
# session.mount('https://', adapter)
# session.mount('http://', adapter)

def try_requests(url, **kwargs):
    headers = kwargs.get('headers', {'User-Agent': 'OpenActive user'})
    num_tries_max = kwargs.get('num_tries_max', 10)
    seconds_wait_retry = kwargs.get('seconds_wait_retry', 1)
    verbose = kwargs.get('verbose', False)

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
            r = session.get(url, headers=headers)
            # https://docs.python-requests.org/en/latest/user/advanced/
            # "Sessions can also be used as context managers [...] This will make sure the session is closed as
            # soon as the with block is exited, even if unhandled exceptions occurred."
            # r = None
            # with requests.Session() as session:
            #     r = session.get(url)
            if (r is None):
                raise Exception('Call failed with no response')
            elif (r.status_code != 200):
                raise Exception(f'Call failed with status code {r.status_code}')
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
    feed = kwargs.get('feed', None)
    seconds_timeout = kwargs.get('seconds_timeout', SECONDS_TIMEOUT_DEFAULT)
    seconds_wait_next = kwargs.get('seconds_wait_next', SECONDS_WAIT_NEXT_DEFAULT)
    verbose = kwargs.get('verbose', False)

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
        time_start = datetime.now()
        get_opportunities_helper_done = False
        while (True):
            feed_url = opportunities['nextUrl']
            opportunities, get_opportunities_helper_done = get_opportunities_helper(opportunities, **kwargs)
            if (    (not get_opportunities_helper_done)
                and ((datetime.now() - time_start).seconds < seconds_timeout)
            ):
                sleep(seconds_wait_next)
            else:
                break
        opportunities['status'] = 'COMPLETE' if get_opportunities_helper_done else 'TIMEOUT'
    except:
        opportunities['status'] = 'ERROR'
        set_message('Issue encountered when getting feed: {}'.format(feed_url), 'error')

    if (    (feed is not None)
        and ('feed' not in opportunities.keys())
    ):
        opportunities['feed'] = feed

    return opportunities

# --------------------------------------------------------------------------------------------------

sum_bytesize_deltas = 0
def get_opportunities_helper(opportunities, **kwargs):
    log_memory = kwargs.get('log_memory', False)
    verbose = kwargs.get('verbose', False)

    feed_url = opportunities['nextUrl']
    feed_page, num_tries = try_requests(feed_url, **kwargs)

    if (    (feed_page is None)
        or  (feed_page.status_code != 200)
    ):
        raise Exception()

    if (log_memory):
        global sum_bytesize_deltas

    for item in feed_page.json()['items']:
        if (all([key in item.keys() for key in ['id', 'state', 'modified']])):
            if (log_memory):
                bytesize_delta = 0
            if (item['state'] == 'updated'):
                if (    (item['id'] not in opportunities['items'].keys())
                    or  (item['modified'] > opportunities['items'][item['id']]['modified'])
                ):
                    if (log_memory):
                        bytesize_item_old = get_bytesize(opportunities['items'][item['id']]) if (item['id'] in opportunities['items'].keys()) else 0
                        bytesize_item_new = get_bytesize(item)
                        bytesize_delta = bytesize_item_new - bytesize_item_old
                    opportunities['items'][item['id']] = item
            elif (  (item['state'] == 'deleted')
                and (item['id'] in opportunities['items'].keys())
            ):
                if (log_memory):
                    bytesize_delta = -get_bytesize(opportunities['items'][item['id']])
                del(opportunities['items'][item['id']])

            if (log_memory):
                sum_bytesize_deltas += bytesize_delta
                if (verbose):
                    print(f"Item ID: {item['id']}; Item bytesize delta: {bytesize_delta}; Sum of item bytesize deltas: {sum_bytesize_deltas}")

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

FILENAME_FEEDS = getenv('FILENAME_FEEDS', 'feeds.pickle') # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_PREVIEW = getenv('FILENAME_FEEDS_PREVIEW', 'feeds-preview.pickle') # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_SEEN = '000-feeds-seen.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAME_FEEDS_CRASHED = '000-feeds-crashed.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
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
LOG_MEMORY = getenv('LOG_MEMORY', 'False').title()
LOG_MEMORY = True if (LOG_MEMORY == 'True') else False
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

feed_urls_skip = [
    # 'https://opendata.leisurecloud.live/api/feeds/EveryoneActive-test-slots', # Crashed Jupyter one time, before timeout code was present
]
# For feeds that error during get_opportunities():
feed_urls_retry = {}

print('Environment variables:')
print('RELATIVE_FILEPATH_FEEDS:', RELATIVE_FILEPATH_FEEDS)
print('RELATIVE_FILEPATH_OPPORTUNITIES:', RELATIVE_FILEPATH_OPPORTUNITIES)
print('FILENAME_FEEDS:', FILENAME_FEEDS)
print('FILENAME_FEEDS_PREVIEW:', FILENAME_FEEDS_PREVIEW)
print('COMPRESSION_FILE_OPPORTUNITIES:', COMPRESSION_FILE_OPPORTUNITIES)
print('MAX_NUM_FEEDS:', MAX_NUM_FEEDS)
print('MAX_NUM_FEED_SECONDS:', MAX_NUM_FEED_SECONDS)
print('MAX_NUM_FEED_TRIES:', MAX_NUM_FEED_TRIES)
print('MAX_NUM_FEED_FILES:', MAX_NUM_FEED_FILES)
print('LOG_MEMORY:', LOG_MEMORY)
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
# filenames_without_infostamp = None # Not currently using in job get-opportunities, but used in job analyse-opportunities
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

def run_get_opportunities(idx_feed, feed, **kwargs):
    preview = kwargs.get('preview', False)

    # --------------------------------------------------------------------------------------------------

    filename_without_infostamp_current = ('000-preview-' if preview else '') + sub('https://|http://|www.', '', feed['url']).replace('.', '-').replace('/', '-').strip('-')
    filenames_with_infostamp_current = sorted([
        filename_with_infostamp
        for filename_with_infostamp in filenames_with_infostamp
        if ('--'.join(filename_with_infostamp.split('--')[:-Infostamp.num_parts]) == filename_without_infostamp_current)
    ])

    # --------------------------------------------------------------------------------------------------

    if (len(filenames_with_infostamp_current) == 0):
        opportunities_in = feed['url']
    else:
        opportunities_in = None
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

    if (opportunities_in in ['', None]):
        print('No input')
        return

    # --------------------------------------------------------------------------------------------------

    if (LOG_MEMORY):
        bytesize_opportunities_in = get_bytesize(opportunities_in) if (type(opportunities_in) == dict) else 0
        print(f'Bytesize opportunities_in: {bytesize_opportunities_in}')
        global sum_bytesize_deltas
        sum_bytesize_deltas = 0

    t1 = datetime.now()
    # If opportunities_in is a dictionary, then it is modified by this function to become opportunities_out.
    # Both of these variables will then point to the same information in memory after this function:
    opportunities_out = get_opportunities(opportunities_in, feed=feed, **kwargs)
    t2 = datetime.now()

    if (LOG_MEMORY):
        bytesize_opportunities_out = get_bytesize(opportunities_out) if (type(opportunities_out) == dict) else 0
        print(f'bytesize_opportunities_in                             : {bytesize_opportunities_in}')
        print(f'bytesize_opportunities_out                            : {bytesize_opportunities_out}')
        print(f'bytesize_opportunities_out - bytesize_opportunities_in: {bytesize_opportunities_out - bytesize_opportunities_in}')
        print(f'Sum of item bytesize deltas                           : {sum_bytesize_deltas}')
        sum_bytesize_deltas = 0

    # --------------------------------------------------------------------------------------------------

    if (opportunities_out is not None):
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
            if (feed['url'] not in feed_urls_retry.keys()):
                feed_urls_retry[feed['url']] = {
                    'idx_feed': idx_feed,
                    'feed': feed,
                    'num_feed_tries_remaining': MAX_NUM_FEED_TRIES - 1,
                    'status': 'ERROR',
                }
        elif (feed['url'] in feed_urls_retry.keys()):
            feed_urls_retry[feed['url']]['num_feed_tries_remaining'] = 0
            feed_urls_retry[feed['url']]['status'] = opportunities_out['status']

    # --------------------------------------------------------------------------------------------------

    print(idx_feed, feed['url'], opportunities_out['status'] if (opportunities_out is not None) else 'ERROR')

    # --------------------------------------------------------------------------------------------------

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
    # FILENAME_FEEDS_SEEN is deleted at the end of a full successful run of harvesting all feeds, so if
    # this file exists at this point it means that this is not the first time we've run the code, which
    # in turn means that we had a forced stop during the previous run, either because of manual intervention
    # or a crash. Taking the latter as the standard production scenario, as manual intervention should
    # only be done when testing, we then have that the last feed to be written to FILENAME_FEEDS_SEEN may
    # itself have been the ultimate cause of the crash. We therefore add that feed to FILENAME_FEEDS_CRASHED
    # and ignore these feeds in further processing attempts:
    try:
        if (FILENAME_FEEDS_SEEN in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)):
            with open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_SEEN, 'r') as file_in:
                date_time_feed_urls_seen = file_in.read().strip('\n').split('\n')
                feed_urls_seen = [date_time_feed_url_seen.split()[2] for date_time_feed_url_seen in date_time_feed_urls_seen]
            with open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_CRASHED, 'a') as file_out:
                file_out.write(date_time_feed_urls_seen[-1] + '\n')
        else:
            feed_urls_seen = []
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    try:
        get_filenames()
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    for preview in [False, True]:
        try:
            print(f"Started first attempt of all{' preview ' if preview else ' '}feed URLs")

            with open(RELATIVE_FILEPATH_FEEDS + '/' + (FILENAME_FEEDS_PREVIEW if preview else FILENAME_FEEDS), 'rb') as file_in:
                feeds = pickle.load(file_in)

            # --------------------------------------------------------------------------------------------------

            for idx_feed, feed in enumerate(feeds['feeds'][0:MAX_NUM_FEEDS]):
                print(idx_feed, feed['url'], 'START')

                if (feed['url'] in feed_urls_skip):
                    feed_urls_skip.remove(feed['url'])
                    print('Feed URL in skip list, skipping')
                    continue
                elif (feed['url'] in feed_urls_seen):
                    feed_urls_seen.remove(feed['url'])
                    print('Feed URL in seen list, skipping')
                    continue

                try:
                    with open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_SEEN, 'a') as file_out:
                        file_out.write(str(datetime.now()) + ' ' + feed['url'] + '\n')
                    run_get_opportunities(
                        idx_feed,
                        feed,
                        headers = HEADERS,
                        log_memory = LOG_MEMORY,
                        preview = preview,
                        seconds_timeout = MAX_NUM_FEED_SECONDS,
                        verbose = VERBOSE,
                    )
                except Exception as error:
                    print('ERROR:', error)

            # --------------------------------------------------------------------------------------------------

            print(f"Finished first attempt of all{' preview ' if preview else ' '}feed URLs")

        except Exception as error:
            print('ERROR:', error)
            sys.exit(1)

        # --------------------------------------------------------------------------------------------------

        try:
            num_feed_urls_retry_remaining = len(feed_urls_retry.keys())

            if (num_feed_urls_retry_remaining > 0):
                print(f"\nStarted{' preview ' if preview else ' '}retries ({num_feed_urls_retry_remaining})")
                print(feed_urls_retry.keys())

                while (num_feed_urls_retry_remaining > 0):
                    # A given feed_url could be retried multiple times if it keeps erroring, with each attempt resulting
                    # in a separate output file. As such, we must get the filenames in the output directory each time we
                    # enter this loop, in order for run_get_opportunities to always have an up-to-date list of filenames
                    # to work with:
                    get_filenames()

                    for feed_url, feed_info in feed_urls_retry.items():
                        if (feed_info['num_feed_tries_remaining'] > 0):
                            print(feed_info['idx_feed'], feed_url, 'START')
                            try:
                                run_get_opportunities(
                                    feed_info['idx_feed'],
                                    feed_info['feed'],
                                    headers = HEADERS,
                                    log_memory = LOG_MEMORY,
                                    preview = preview,
                                    seconds_timeout = MAX_NUM_FEED_SECONDS,
                                    verbose = VERBOSE,
                                )
                            except Exception as error:
                                print('ERROR:', error)
                            if (feed_info['num_feed_tries_remaining'] > 0):
                                feed_info['num_feed_tries_remaining'] -= 1
                            if (feed_info['num_feed_tries_remaining'] == 0):
                                num_feed_urls_retry_remaining -= 1

                feed_urls_retry = {}
                print(f"Finished{' preview ' if preview else ' '}retries")

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

    if (FILENAME_FEEDS_SEEN in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)):
        remove(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_SEEN)
    # if (FILENAME_FEEDS_CRASHED in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)):
    #     remove(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + FILENAME_FEEDS_CRASHED)

    # --------------------------------------------------------------------------------------------------

    print('Finished')