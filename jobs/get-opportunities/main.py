# import gc # 2024-06-14 Not currently using this as forced garbage collection is suspected of affecting Google Cloud memory performance
import gzip
import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_opportunities, get_bytesize
from os import getenv, listdir, remove, rename

sys.path.append('../volume-1/common')
from fileutils import FilenameStamp, get_filenames, get_current_filenames
from openactive_custom import get_opportunities, get_bytesize
from settings import *

# --------------------------------------------------------------------------------------------------

LOG_MEMORY = getenv('LOG_MEMORY', str(GET_OPPORTUNITIES_LOG_MEMORY)).title()
LOG_MEMORY = True if (LOG_MEMORY == 'True') else False

VERBOSE = getenv('VERBOSE', str(GET_OPPORTUNITIES_VERBOSE)).title()
VERBOSE = True if (VERBOSE == 'True') else False

# --------------------------------------------------------------------------------------------------

def run_get_opportunities(feed, **kwargs):
    log_memory = kwargs.get('log_memory', False)
    preview = kwargs.get('preview', False)

    # --------------------------------------------------------------------------------------------------

    current_filename_base = PREVIEW_OPPORTUNITIES_FILENAME_BASE if preview else REGULAR_OPPORTUNITIES_FILENAME_BASE
    current_filename_url = feed['url'].replace('https://', '').replace('http://', '').replace('www.', '').replace('.', '-').replace('/', '-').strip('-')
    current_filename_prestamp = current_filename_base + '--' + current_filename_url

    filenames = get_filenames('opportunities')
    current_filenames = get_current_filenames('opportunities', current_filename_prestamp, filenames)

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
        opportunities['feed'] = feed

        current_filename = \
            current_filename_prestamp + \
            FilenameStamp('opportunities', t1, t2, {'numItems': len(opportunities['items'].keys()), 'numUrls': len(opportunities['urls']), 'status': opportunities['status']}).value + \
            OPPORTUNITIES_FILENAME_SUFFIX

        # We have seen that gzip sometimes doesn't write files correctly, as an attempted read of such a file
        # results in the error 'Compressed file ended before the end-of-stream marker was reached', which messes
        # things up on the next run of this code when that file is to be used as the input. This seems to affect
        # certain feeds more than others, and is not simply due to large file sizes as some feeds without this
        # issue have large file sizes, so the ultimate cause is unknown, it could be something about the actual
        # characters involved. Online comments for this error suggest trying to rewrite the file in the first
        # instance, hence the write-read-rewrite process below. Also, after the initial write the attempted
        # file opening may completely kill this running code, at least on Google Cloud, meaning the exception
        # handling itself is never entered. For this reason we use a temporary file name which we know not
        # to trust if found in storage, and only rename it to the desired name if it passes the opening test.
        # This workaround means that any opportunities file in storage which does not have the temporary file
        # name has been checked to open correctly, and should be fine for further use:

        num_write_tries = 0
        while (num_write_tries < MAX_NUM_WRITE_TRIES):
            num_write_tries += 1
            print(f'Writing filename: {current_filename}')
            print(f'Try: {num_write_tries}/{MAX_NUM_WRITE_TRIES}')
            try:
                try:
                    remove(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + TEMPORARY_OPPORTUNITIES_FILENAME)
                except:
                    pass
                with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + TEMPORARY_OPPORTUNITIES_FILENAME, 'wb') as file_out:
                    pickle.dump(opportunities, file_out)
                with gzip.open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + TEMPORARY_OPPORTUNITIES_FILENAME, 'rb') as file_in:
                    opportunities_test = pickle.load(file_in)
                rename(
                    OPPORTUNITIES_RELATIVE_FILEPATH + '/' + TEMPORARY_OPPORTUNITIES_FILENAME,
                    OPPORTUNITIES_RELATIVE_FILEPATH + '/' + current_filename
                )
                print('Successful write')
                del(opportunities_test)
                break
            except:
                if (num_write_tries < MAX_NUM_WRITE_TRIES):
                    print('Unsuccessful write, retrying ...')
                else:
                    print('Unsuccessful write, maximum number of tries reached')
                    opportunities['status'] = 'ERROR'

    # --------------------------------------------------------------------------------------------------

    # Keep this file removal section outside of the file creation section. This is in order to check if
    # there are more files than desired regardless of whether or not one has just been created, which could
    # be so if file removal was inhibited on the previous run or if the maximum number of files to keep
    # has changed since the previous run:

    filenames = get_filenames('opportunities')
    current_filenames = get_current_filenames('opportunities', current_filename_prestamp, filenames)

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

            num_feeds = len(feeds)

            crashed_feed_url = None
            if (RUNNING_FEED_FILENAME in listdir(OPPORTUNITIES_RELATIVE_FILEPATH)):
                with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + RUNNING_FEED_FILENAME, 'r') as file_in:
                    date_time_crashed_feed_url = file_in.read()
                with open(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + CRASHED_FEEDS_FILENAME, 'a') as file_out:
                    file_out.write(f'{date_time_crashed_feed_url}\n')
                crashed_feed_url = date_time_crashed_feed_url.split()[-1]

            # --------------------------------------------------------------------------------------------------

            while (any([(feed['status'] in [None, 'ERROR']) and (feed['num_tries'] < MAX_NUM_FEED_TRIES) for feed in feeds])):

                for feed_idx, feed in enumerate(feeds):

                    # If the previous run crashed then now jump ahead and progress from the next feed:
                    if (crashed_feed_url is not None):
                        if (feed['url'] == crashed_feed_url):
                            crashed_feed_url = None
                        continue

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

                    print(f"Running {'preview' if preview else 'regular'} feed: {feed_idx+1}/{num_feeds}")
                    print(f"URL: {feed['url']}")
                    print(f"Try: {feed['num_tries']}/{MAX_NUM_FEED_TRIES}")

                    try:
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

                    print('--------------------------------------------------')

            # --------------------------------------------------------------------------------------------------

            try:
                remove(OPPORTUNITIES_RELATIVE_FILEPATH + '/' + TEMPORARY_OPPORTUNITIES_FILENAME)
            except:
                pass

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