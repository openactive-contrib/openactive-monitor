import csv
import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_feeds
from os import getenv, listdir, remove, symlink
from os.path import isfile

sys.path.append('../volume-1/common')
from openactive_custom import get_feeds

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. This
# was done for each job as follows (note that the volume and its mount-path were given the same name,
# which didn't have to be so):
#   $ gcloud beta run jobs update <JOB NAME> \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
FEEDS_RELATIVE_FILEPATH = getenv('FEEDS_RELATIVE_FILEPATH', '../volume-1/data-feeds')

REGULAR_FEEDS_FILENAME_BASE = getenv('REGULAR_FEEDS_FILENAME_BASE', 'regular-feeds')
PREVIEW_FEEDS_FILENAME_BASE = getenv('PREVIEW_FEEDS_FILENAME_BASE', 'preview-feeds')
FEEDS_FILENAME_SUFFIX = '.pickle'
REGULAR_FEEDS_LATEST_FILENAME = getenv('REGULAR_FEEDS_LATEST_FILENAME', 'feeds.pickle') # Located in FEEDS_RELATIVE_FILEPATH TODO: Change to 'regular-feeds-latest.pickle' when accommodated in other jobs
PREVIEW_FEEDS_LATEST_FILENAME = getenv('PREVIEW_FEEDS_LATEST_FILENAME', 'feeds-preview.pickle') # Located in FEEDS_RELATIVE_FILEPATH TODO: Change to 'preview-feeds-latest.pickle' when accommodated in other jobs
REGULAR_FEEDS_HISTORY_FILENAME = getenv('REGULAR_FEEDS_HISTORY_FILENAME', 'regular-feeds-history.csv') # Located in FEEDS_RELATIVE_FILEPATH
PREVIEW_FEEDS_HISTORY_FILENAME = getenv('PREVIEW_FEEDS_HISTORY_FILENAME', 'preview-feeds-history.csv') # Located in FEEDS_RELATIVE_FILEPATH
SKIP_FILENAMES = [
    REGULAR_FEEDS_LATEST_FILENAME,
    PREVIEW_FEEDS_LATEST_FILENAME,
    REGULAR_FEEDS_HISTORY_FILENAME,
    PREVIEW_FEEDS_HISTORY_FILENAME,
] # Filenames to skip when checking for files in storage

MAX_NUM_FEEDS_FILES = int(getenv('MAX_NUM_FEEDS_FILES', '500')) # Number of feeds files to keep for each feed type (regular and preview), including the latest output. 2025-09-03 A regular feeds file is currently ~100KB, so 500 of these is ~50MB. A preview feeds file is currently ~1KB, so 500 of these is ~0.5MB. 500 was chosen to go back ~1.5 years if this is run daily.
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
print('REGULAR_FEEDS_FILENAME_BASE:', REGULAR_FEEDS_FILENAME_BASE)
print('PREVIEW_FEEDS_FILENAME_BASE:', PREVIEW_FEEDS_FILENAME_BASE)
print('REGULAR_FEEDS_LATEST_FILENAME:', REGULAR_FEEDS_LATEST_FILENAME)
print('PREVIEW_FEEDS_LATEST_FILENAME:', PREVIEW_FEEDS_LATEST_FILENAME)
print('REGULAR_FEEDS_HISTORY_FILENAME:', REGULAR_FEEDS_HISTORY_FILENAME)
print('PREVIEW_FEEDS_HISTORY_FILENAME:', PREVIEW_FEEDS_HISTORY_FILENAME)
print('MAX_NUM_FEEDS_FILES:', MAX_NUM_FEEDS_FILES)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

# A feeds filename is formed of a base, a stamp, and a suffix.
# The base is like:
#   'regular-feeds' or 'preview-feeds'
# The stamp is like:
#   '--timeFinish-2025-09-03-18-32-43-729646-UTC--timeTaken-131-21962--numFeeds-452--numDatasets-167'
# The suffix is like:
#   '.pickle'
class FilenameStamp:
    # Files of the same filename pre-stamp are later grouped and alphabetically sorted to find the order
    # in which they were made, via the filename stamp, so that earlier files can be deleted. It's important
    # that 'timeFinish' is the first part of the filename stamp for this to work as intended. Other parts
    # can appear in any order. The alternative would be to break down the stamp and seek the 'timeFinish'
    # part when sorting, which is a bit more work and not necessary at the time of writing (2024-06-20):
    parts = [
        'timeFinish',
        'timeTaken',
        'numFeeds',
        'numDatasets',
    ]

    # This is important to know outside of this class for when the filename is broken into parts, in order
    # to know how many of the parts form the stamp:
    num_parts = len(parts)

    def __init__(self, t1, t2, num_feeds, num_datasets):
        time_delta = t2 - t1
        self.value = ''
        for part in self.parts:
            if (part == 'timeFinish'):
                self.value += f"--{part}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}-UTC"
            elif (part == 'timeTaken'):
                self.value += f"--{part}-{time_delta.seconds}-{time_delta.microseconds}"
            elif (part == 'numFeeds'):
                self.value += f"--{part}-{num_feeds}"
            elif (part == 'numDatasets'):
                self.value += f"--{part}-{num_datasets}"

# --------------------------------------------------------------------------------------------------

filenames = None
# filename_prestamps = None # Not currently used herein, but may be useful
def get_filenames():
    global filenames
    # global filename_prestamps

    filenames = sorted([
        i
        for i in listdir(FEEDS_RELATIVE_FILEPATH)
        if (    (isfile(FEEDS_RELATIVE_FILEPATH + '/' + i))
            and (i.startswith(REGULAR_FEEDS_FILENAME_BASE) or i.startswith(PREVIEW_FEEDS_FILENAME_BASE))
            and (i.endswith(FEEDS_FILENAME_SUFFIX))
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
        FilenameStamp(t1, t2, len(feeds), len(set([feed['datasetUrl'] for feed in feeds]))).value + \
        FEEDS_FILENAME_SUFFIX

    with open(FEEDS_RELATIVE_FILEPATH + '/' + current_filename, 'wb') as file_out:
        # TODO: Change this to the following when accommodated in other jobs, no further information is necessary:
        # pickle.dump(feeds, file_out)
        pickle.dump(
            {
                'feeds': feeds,
                'num_feeds': len(feeds),
            },
            file_out
        )

    get_filenames()
    current_filenames = sorted([
        filename
        for filename in filenames
        if (filename.startswith(current_filename_base))
    ])

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