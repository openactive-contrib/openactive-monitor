from os import listdir
from os.path import isfile

from openactive_custom import get_partner_feed_url
from settings import *

# --------------------------------------------------------------------------------------------------

# A feeds filename is formed of a base, a stamp, and a suffix.
# The base is like:
#   'regular-feeds' or 'preview-feeds'
# The stamp is like:
#   '--timeFinish-2025-09-03-18-32-43-729646-UTC--timeTaken-131-21962--numFeeds-452--numDatasets-167'
# The suffix is like:
#   '.pickle'

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
    feeds_filename_stamp_parts = [
        'timeFinish',
        'timeTaken',
        'numFeeds',
        'numDatasets',
    ]
    opportunities_filename_stamp_parts = [
        'timeFinish',
        'timeTaken',
        'numItems',
        'numUrls',
        'status',
    ]

    # This is important to know outside of this class for when the filename is broken into parts, in order
    # to know how many of the parts form the stamp:
    num_feeds_filename_stamp_parts = len(feeds_filename_stamp_parts)
    num_opportunities_filename_stamp_parts = len(opportunities_filename_stamp_parts)

    def __init__(self, mode, t1, t2, args):

        time_delta = t2 - t1
        self.value = ''
        self.value += f"--{'timeFinish'}-{t2.year}-{t2.month:02}-{t2.day:02}-{t2.hour:02}-{t2.minute:02}-{t2.second:02}-{t2.microsecond:06}-UTC"
        self.value += f"--{'timeTaken'}-{time_delta.seconds}-{time_delta.microseconds}"

        if (mode == 'feeds'):
            parts = self.feeds_filename_stamp_parts
        elif (mode == 'opportunities'):
            parts = self.opportunities_filename_stamp_parts

        for part in parts[2:]:
            self.value += f"--{part}-{args[part]}"

# --------------------------------------------------------------------------------------------------

def get_filenames(mode):
    if (mode == 'feeds'):
        relative_filepath = FEEDS_RELATIVE_FILEPATH
        regular_filename_base = REGULAR_FEEDS_FILENAME_BASE
        preview_filename_base = PREVIEW_FEEDS_FILENAME_BASE
        filename_suffix = FEEDS_FILENAME_SUFFIX
        skip_filenames = FEEDS_RELATIVE_FILEPATH_SKIP_FILENAMES
    elif (mode == 'opportunities'):
        relative_filepath = OPPORTUNITIES_RELATIVE_FILEPATH
        regular_filename_base = REGULAR_OPPORTUNITIES_FILENAME_BASE
        preview_filename_base = PREVIEW_OPPORTUNITIES_FILENAME_BASE
        filename_suffix = OPPORTUNITIES_FILENAME_SUFFIX
        skip_filenames = OPPORTUNITIES_RELATIVE_FILEPATH_SKIP_FILENAMES

    filenames = sorted([
        i
        for i in listdir(relative_filepath)
        if (    (isfile(relative_filepath + '/' + i))
            and (i.startswith(regular_filename_base) or i.startswith(preview_filename_base))
            and (i.endswith(filename_suffix))
            and (i not in skip_filenames)
        )
    ])

    return filenames

# --------------------------------------------------------------------------------------------------

def get_current_filenames(mode, filename_prestamp, filenames):
    if (mode == 'feeds'):
        num_parts = FilenameStamp.num_feeds_filename_stamp_parts
    elif (mode == 'opportunities'):
        num_parts = FilenameStamp.num_opportunities_filename_stamp_parts

    current_filenames = sorted([
        filename
        for filename in filenames
        if ('--'.join(filename.split('--')[:-num_parts]) == filename_prestamp) # We can't simply use filename.startswith(filename_prestamp), as filename_prestamp might be a substring of a filename with a longer pre-stamp, which would then also be gathered e.g. consider 'facility-uses' and 'facility-uses-events' within the pre-stamp
    ])

    return current_filenames

# --------------------------------------------------------------------------------------------------

def get_filename_prestamps(mode, filenames):
    if (mode == 'feeds'):
        num_parts = FilenameStamp.num_feeds_filename_stamp_parts
    elif (mode == 'opportunities'):
        num_parts = FilenameStamp.num_opportunities_filename_stamp_parts

    # Here we split on '--' which is used as the filename stamp delimiter, then remove the number of parts
    # that we know exist in the filename stamp. If we are then left with multiple fragments from the split,
    # that's because there were other instances of '--' in the filename pre-stamp that we don't want to
    # lose, hence we rejoin these fragments with '--' again:

    filename_prestamps = sorted(set([
        '--'.join(filename.split('--')[:-num_parts])
        for filename in filenames
    ]))

    return filename_prestamps

# --------------------------------------------------------------------------------------------------

def get_filename_prestamp_pairs(filename_prestamps):
    filename_prestamp_pairs = []
    found_filename_prestamps = []

    for filename_prestamp in filename_prestamps:
        if (filename_prestamp not in found_filename_prestamps):
            partner_filename_prestamp = get_partner_feed_url(filename_prestamp, filename_prestamps)
            filename_prestamp_pairs.append([filename_prestamp, partner_filename_prestamp])
            if (partner_filename_prestamp is not None):
                found_filename_prestamps.append(partner_filename_prestamp)

    return filename_prestamp_pairs

# --------------------------------------------------------------------------------------------------

def get_filename_pairs():
    filename_pairs = []

    filenames = get_filenames('opportunities')
    filename_prestamps = get_filename_prestamps('opportunities', filenames)
    filename_prestamp_pairs = get_filename_prestamp_pairs(filename_prestamps)

    for filename_prestamp_pair in filename_prestamp_pairs:
        filename_pair = []
        for filename_prestamp in filename_prestamp_pair:
            if (filename_prestamp is not None):
                current_filenames = get_current_filenames('opportunities', filename_prestamp, filenames)
                filename_pair.append(current_filenames[-1])
            else:
                filename_pair.append(None)
        filename_pairs.append(filename_pair)

    # If something unusual seems to be going on with the filename pairing, then uncomment the following
    # and run to see exactly what is being paired:

    # print('\nfilenames:')
    # for filename in filenames:
    #     print(filename)

    # print('\nfilename_prestamps:')
    # for filename_prestamp in filename_prestamps:
    #     print(filename_prestamp)

    # print('\nfilename_prestamp_pairs:')
    # for filename_prestamp_pair in filename_prestamp_pairs:
    #     print(filename_prestamp_pair[0])
    #     print(filename_prestamp_pair[1])
    #     print()

    # print('filename_pairs:')
    # for filename_pair in filename_pairs:
    #     print(filename_pair[0])
    #     print(filename_pair[1])
    #     print()

    return filename_pairs