# import gc # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google Cloud memory performance
import gzip
import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_opportunities, get_bytesize
from os import getenv, listdir, remove
from os.path import isfile

sys.path.append('../volume-1/common')
from openactive_custom import get_opportunities, get_bytesize

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
FEEDS_RELATIVE_FILEPATH = getenv('FEEDS_RELATIVE_FILEPATH', '../volume-1/data-feeds')
OPPORTUNITIES_RELATIVE_FILEPATH = getenv('OPPORTUNITIES_RELATIVE_FILEPATH', '../volume-1/data-opportunities')

REGULAR_FEEDS_LATEST_FILENAME = getenv('REGULAR_FEEDS_LATEST_FILENAME', 'feeds.pickle') # Located in FEEDS_RELATIVE_FILEPATH TODO: Change to 'regular-feeds-latest.pickle' when accommodated in other jobs
PREVIEW_FEEDS_LATEST_FILENAME = getenv('PREVIEW_FEEDS_LATEST_FILENAME', 'feeds-preview.pickle') # Located in FEEDS_RELATIVE_FILEPATH TODO: Change to 'preview-feeds-latest.pickle' when accommodated in other jobs
REGULAR_OPPORTUNITIES_FILENAME_BASE = getenv('REGULAR_OPPORTUNITIES_FILENAME_BASE', 'regular-ops')
PREVIEW_OPPORTUNITIES_FILENAME_BASE = getenv('PREVIEW_OPPORTUNITIES_FILENAME_BASE', 'preview-ops')
OPPORTUNITIES_FILENAME_SUFFIX = '.pickle.gzip'
RUNNING_FEEDS_FILENAME = '000-running-feeds.pickle' # Located in OPPORTUNITIES_RELATIVE_FILEPATH
RUNNING_FEED_FILENAME = '000-running-feed.txt' # Located in OPPORTUNITIES_RELATIVE_FILEPATH
CRASHED_FEEDS_FILENAME = '000-crashed-feeds.txt' # Located in OPPORTUNITIES_RELATIVE_FILEPATH
SKIP_FILENAMES = [
    RUNNING_FEEDS_FILENAME,
    RUNNING_FEED_FILENAME,
    CRASHED_FEEDS_FILENAME,
] # Filenames to skip when checking for files in storage

MAX_NUM_FEEDS = int(getenv('MAX_NUM_FEEDS', '-1'))
MAX_NUM_FEEDS = None if (MAX_NUM_FEEDS < 0) else MAX_NUM_FEEDS # Negative indicates to do all feeds, otherwise cap at the stated number of feeds. This is useful for testing on a subset of all feeds.
MAX_NUM_FEED_SECONDS = int(getenv('MAX_NUM_FEED_SECONDS', '600'))
MAX_NUM_FEED_TRIES = int(getenv('MAX_NUM_FEED_TRIES', '3'))
MAX_NUM_WRITE_TRIES = int(getenv('MAX_NUM_WRITE_TRIES', '3'))
MAX_NUM_OPPORTUNITIES_FILES = int(getenv('MAX_NUM_OPPORTUNITIES_FILES', '1')) # Number of opportunities files to keep for each feed, including the latest output
LOG_MEMORY = getenv('LOG_MEMORY', 'False').title()
LOG_MEMORY = True if (LOG_MEMORY == 'True') else False
VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

HEADERS = {
    'timeout': '10',
    'User-Agent': 'OpenActive admin',
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', # Alternative 'User-Agent' based on laptop browser settings. Still doesn't seem to help some GCloud 403 errors though.
    'From': 'hello@openactive.io',
    'Referer': 'https://www.openactive.io',
}

print('Environment variables:')
print('FEEDS_RELATIVE_FILEPATH:', FEEDS_RELATIVE_FILEPATH)
print('OPPORTUNITIES_RELATIVE_FILEPATH:', OPPORTUNITIES_RELATIVE_FILEPATH)
print('REGULAR_FEEDS_LATEST_FILENAME:', REGULAR_FEEDS_LATEST_FILENAME)
print('PREVIEW_FEEDS_LATEST_FILENAME:', PREVIEW_FEEDS_LATEST_FILENAME)
print('REGULAR_OPPORTUNITIES_FILENAME_BASE:', REGULAR_OPPORTUNITIES_FILENAME_BASE)
print('PREVIEW_OPPORTUNITIES_FILENAME_BASE:', PREVIEW_OPPORTUNITIES_FILENAME_BASE)
print('MAX_NUM_FEEDS:', MAX_NUM_FEEDS)
print('MAX_NUM_FEED_SECONDS:', MAX_NUM_FEED_SECONDS)
print('MAX_NUM_FEED_TRIES:', MAX_NUM_FEED_TRIES)
print('MAX_NUM_WRITE_TRIES:', MAX_NUM_WRITE_TRIES)
print('MAX_NUM_OPPORTUNITIES_FILES:', MAX_NUM_OPPORTUNITIES_FILES)
print('LOG_MEMORY:', LOG_MEMORY)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

# An opportunities filename is formed of a base, a converted URL, a stamp, and a suffix.
# The base is like:
#   'regular-ops' or 'preview-ops'
# The converted URL is like:
#   '--actihire-bookteq-com-api-open-active-facility-uses'
# The stamp is like:
#   '--timeFinish-2024-11-28-02-17-30-651905-UTC--timeTaken-0-374038--numItems-4059--numUrls-39--status-COMPLETE'
# The suffix is like:
#   '.pickle.gzip'
class FilenameStamp:
    # Files of the same filename pre-stamp are later grouped and alphabetically sorted to find the order
    # in which they were made, via the filename stamp, so that earlier files can be deleted. It's important
    # that 'timeFinish' is the first part of the filename stamp for this to work as intended. Other parts
    # can appear in any order. The alternative would be to break down the stamp and seek the 'timeFinish'
    # part when sorting, which is a bit more work and not necessary at the time of writing (2024-06-20):
    parts = [
        'timeFinish',
        'timeTaken',
        'numItems',
        'numUrls',
        'status',
    ]

    # This is important to know outside of this class for when the filename is broken into parts, in order
    # to know how many of the parts form the stamp:
    num_parts = len(parts)

    def __init__(self, t1, t2, num_items, num_urls, status):
        time_delta = t2 - t1
        self.value = ''
        for part in self.parts:
            if (part == 'timeFinish'):
                self.value += f"--{part}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}-UTC"
            elif (part == 'timeTaken'):
                self.value += f"--{part}-{time_delta.seconds}-{time_delta.microseconds}"
            elif (part == 'numItems'):
                self.value += f"--{part}-{num_items}"
            elif (part == 'numUrls'):
                self.value += f"--{part}-{num_urls}"
            elif (part == 'status'):
                self.value += f"--{part}-{status}"

# --------------------------------------------------------------------------------------------------

filenames = None
# filename_prestamps = None # Not currently used herein, but may be useful
def get_filenames():
    global filenames
    # global filename_prestamps

    filenames = sorted([
        i
        for i in listdir(OPPORTUNITIES_RELATIVE_FILEPATH)
        if (    (isfile(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + i))
            and (i.startswith(REGULAR_OPPORTUNITIES_FILENAME_BASE) or i.startswith(PREVIEW_OPPORTUNITIES_FILENAME_BASE))
            and (i.endswith(OPPORTUNITIES_FILENAME_SUFFIX))
            and (i not in SKIP_FILENAMES)
        )
    ])

    # Here we split on '--' which is used as the filename stamp delimiter, then remove the number of parts
    # that we know exist in the filename stamp. If we are then left with multiple fragments from the split,
    # that's because there were other instances of '--' in the filename pre-stamp that we don't want to
    # lose, hence we rejoin these fragments with '--' again:

    # filename_prestamps = sorted(set([
    #     '--'.join(i.split('--')[:-FilenameStamp.num_parts])
    #     for i in filenames
    # ]))

# --------------------------------------------------------------------------------------------------

def run_get_opportunities(feed, **kwargs):
    log_memory = kwargs.get('log_memory', False)
    preview = kwargs.get('preview', False)

    # --------------------------------------------------------------------------------------------------

    current_filename_base = PREVIEW_OPPORTUNITIES_FILENAME_BASE if preview else REGULAR_OPPORTUNITIES_FILENAME_BASE
    current_filename_url = feed['url'].replace('https://', '').replace('http://', '').replace('www.', '').replace('.', '-').replace('/', '-').strip('-')
    current_filename_prestamp = current_filename_base + '--' + current_filename_url

    get_filenames()
    current_filenames = sorted([
        filename
        for filename in filenames
        if (filename.startswith(current_filename_prestamp))
    ])

    # --------------------------------------------------------------------------------------------------

    if (len(current_filenames) == 0):
        opportunities = feed['url']
    else:
        with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + current_filenames[-1], 'rb') as file_in:
            opportunities = pickle.load(file_in)

    # --------------------------------------------------------------------------------------------------

    t1 = datetime.now()
    if (log_memory):
        bytesize_opportunities_1 = get_bytesize(opportunities) if (type(opportunities) == dict) else 0
        opportunities, sum_bytesize_item_deltas = get_opportunities(opportunities, **kwargs)
        bytesize_opportunities_2 = get_bytesize(opportunities) if (type(opportunities) == dict) else 0
        print(f'bytesize_opportunities_1                           : {bytesize_opportunities_1}')
        print(f'bytesize_opportunities_2                           : {bytesize_opportunities_2}')
        print(f'bytesize_opportunities_2 - bytesize_opportunities_1: {bytesize_opportunities_2 - bytesize_opportunities_1}')
        print(f'Sum of bytesize item deltas                        : {sum_bytesize_item_deltas}')
    else:
        opportunities = get_opportunities(opportunities, **kwargs)
    t2 = datetime.now()

    # --------------------------------------------------------------------------------------------------

    if (type(opportunities) == dict):
        if ('feed' not in opportunities.keys()):
            opportunities['feed'] = feed

        current_filename = \
            current_filename_prestamp + \
            FilenameStamp(t1, t2, len(opportunities['items'].keys()), len(opportunities['urls']), opportunities['status']).value + \
            OPPORTUNITIES_FILENAME_SUFFIX

        # We have seen that gzip sometimes doesn't write files correctly, as an attempted read of such a file
        # results in the error 'Compressed file ended before the end-of-stream marker was reached', which messes
        # things up on the next run of this code when that file is to be used as the input. This seems to affect
        # certain feeds more than others, and is not simply due to large file sizes as some feeds without this
        # issue have large file sizes, so the ultimate cause is unknown, it could be something about the actual
        # characters involved. Online comments for this error suggest trying to write the file again in the
        # first instance, hence the write-read-rewrite process below. This workaround at least results in only
        # safe files that can be opened being kept in storage:

        num_write_tries = 0
        while (num_write_tries < MAX_NUM_WRITE_TRIES):
            num_write_tries += 1
            try:
                print(f'Try {num_write_tries}/{MAX_NUM_WRITE_TRIES} of writing file {current_filename}')
                with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + current_filename, 'wb') as file_out:
                    pickle.dump(opportunities, file_out)
                with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + current_filename, 'rb') as file_in:
                    opportunities_test = pickle.load(file_in)
                print('Successful write')
                del(opportunities_test)
                break
            except:
                if (num_write_tries < MAX_NUM_WRITE_TRIES):
                    print('Unsuccessful write, retrying ...')
                else:
                    print('Unsuccessful write, maximum number of tries reached')
                    opportunities['status'] = 'ERROR'
                try:
                    remove(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + current_filename)
                except:
                    pass

    # --------------------------------------------------------------------------------------------------

    # Keep this file removal section outside of the file creation section. This is in order to check if
    # there are more files than desired regardless of whether or not one has just been created, which could
    # be so if file removal was inhibited on the previous run or if the maximum number of files to keep
    # has changed since the previous run:

    get_filenames()
    current_filenames = sorted([
        filename
        for filename in filenames
        if (filename.startswith(current_filename_prestamp))
    ])

    if (len(current_filenames) > MAX_NUM_OPPORTUNITIES_FILES):
        for filename in current_filenames[:-MAX_NUM_OPPORTUNITIES_FILES]:
            try:
                remove(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + filename)
            except:
                pass

    # --------------------------------------------------------------------------------------------------

    # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google
    # Cloud memory performance:

    # gc.collect()

    return opportunities

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
            # RUNNING_FEEDS_FILENAME and RUNNING_FEED_FILENAME are deleted at the end of a complete run of this
            # loop. So if these files exist at this point it means that we are continuing from an incomplete run,
            # either because the previous run was manually stopped or crashed. In normal operation with this code
            # left automatically running on Google Cloud, we must have the latter situation, and so we update the
            # crash list below:

            if (RUNNING_FEEDS_FILENAME in listdir(OPPORTUNITIES_RELATIVE_FILEPATH)):
                with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEEDS_FILENAME, 'rb') as file_in:
                    feeds = pickle.load(file_in)
            else:
                with open(FEEDS_RELATIVE_FILEPATH + '/' + (PREVIEW_FEEDS_LATEST_FILENAME if preview else REGULAR_FEEDS_LATEST_FILENAME), 'rb') as file_in:
                    # TODO: Change this to the following when get-feeds has been adjusted to output a list rather than a dictionary:
                    # feeds = pickle.load(file_in)[0:MAX_NUM_FEEDS]
                    feeds = pickle.load(file_in)['feeds'][0:MAX_NUM_FEEDS]
                for feed in feeds:
                    feed['time_started'] = None
                    feed['num_tries'] = 0
                    feed['status'] = None

            if (RUNNING_FEED_FILENAME in listdir(OPPORTUNITIES_RELATIVE_FILEPATH)):
                with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEED_FILENAME, 'r') as file_in:
                    date_time_feed_url = file_in.read()
                with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + CRASHED_FEEDS_FILENAME, 'a') as file_out:
                    file_out.write(f'{date_time_feed_url}\n')

            # --------------------------------------------------------------------------------------------------

            print(f"\n***** Started {'preview' if preview else 'regular'} feeds *****")

            while (any([(feed['status'] in [None, 'ERROR']) and (feed['num_tries'] < MAX_NUM_FEED_TRIES) for feed in feeds])):

                for feed_idx, feed in enumerate(feeds):
                    if (feed['status'] in ['COMPLETE', 'TIMEOUT']):
                        continue
                    elif (feed['status'] in [None, 'ERROR']):
                        if (feed['num_tries'] == MAX_NUM_FEED_TRIES):
                            continue
                        else:
                            feed['time_started'] = datetime.now()
                            feed['num_tries'] += 1
                            feed['status'] = None

                    with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEEDS_FILENAME, 'wb') as file_out:
                        pickle.dump(feeds, file_out)

                    with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEED_FILENAME, 'w') as file_out:
                        file_out.write(f"{feed['time_started']} {feed['url']}")

                    # --------------------------------------------------------------------------------------------------

                    try:
                        print(f"\nTry {feed['num_tries']}/{MAX_NUM_FEED_TRIES} of {'preview' if preview else 'regular'} feed {feed_idx+1} {feed['url']}")
                        opportunities = run_get_opportunities(
                            feed,
                            headers = HEADERS,
                            log_memory = LOG_MEMORY,
                            preview = preview,
                            seconds_timeout = MAX_NUM_FEED_SECONDS,
                            verbose = VERBOSE,
                        )
                    except Exception as error:
                        opportunities = None
                        print('ERROR:', error)

                    # --------------------------------------------------------------------------------------------------

                    if (type(opportunities) == dict):
                        feed['status'] = opportunities['status']
                    else:
                        feed['status'] = 'ERROR'

                    if (feed['status'] == 'COMPLETE'):
                        print('Successful feed')
                    elif (feed['status'] == 'TIMEOUT'):
                        print('Successful feed as read so far, but timed out so may be incomplete. Not retrying timeouts.')
                    elif (feed['status'] == 'ERROR'):
                        if (feed['num_tries'] < MAX_NUM_FEED_TRIES):
                            print('Unsuccessful feed, retrying after any other feeds left to try first ...')
                        else:
                            print('Unsuccessful feed, maximum number of tries reached')

                    with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEEDS_FILENAME, 'wb') as file_out:
                        pickle.dump(feeds, file_out)

            # --------------------------------------------------------------------------------------------------

            try:
                remove(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEEDS_FILENAME)
            except:
                pass

            try:
                remove(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEED_FILENAME)
            except:
                pass

        except Exception as error:
            print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    # For running on Google Cloud to trigger the next job, comment out if running locally:
    try:
        run_job('analyse-opportunities')
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')