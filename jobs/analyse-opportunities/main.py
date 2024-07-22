import gzip
import lzma
import pickle
import sys
from datetime import datetime
from geopy.geocoders import Nominatim
from os import getenv, listdir
from os.path import isfile
from time import sleep

# --------------------------------------------------------------------------------------------------

# TODO: Consider using a non-infinite timeout here. See:
# https://gis.stackexchange.com/questions/173569/avoid-time-out-error-nominatim-geopy-openstreetmap
# https://geopy.readthedocs.io/en/latest/index.html#nominatim
geolocator = Nominatim(user_agent='OpenActive Monitor', timeout=None)

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'analyse-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update analyse-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_OPPORTUNITIES = getenv('RELATIVE_FILEPATH_OPPORTUNITIES', '../volume-1/data-opportunities')
RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')

FILENAME_FEEDS_SEEN = '000_feeds_seen.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAME_FEEDS_CRASHED = '000_feeds_crashed.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAMES_SKIP = [FILENAME_FEEDS_SEEN, FILENAME_FEEDS_CRASHED] # Filenames to skip when checking for opportunity files in RELATIVE_FILEPATH_OPPORTUNITIES
FORMAT_FILE_OPPORTUNITIES = 'pickle'
COMPRESSION_FILE_OPPORTUNITIES = getenv('COMPRESSION_FILE_OPPORTUNITIES', 'gzip').lower() # 'none' / 'gzip' / 'xz'
SUFFIX_FILENAME_OPPORTUNITIES = '.' + FORMAT_FILE_OPPORTUNITIES + (('.' + COMPRESSION_FILE_OPPORTUNITIES) if (COMPRESSION_FILE_OPPORTUNITIES != 'none') else '')
LEN_SUFFIX_FILENAME_OPPORTUNITIES = len(SUFFIX_FILENAME_OPPORTUNITIES)
FILENAME_ANALYSIS = 'analysis.pickle'

print('Environment variables:')
print('RELATIVE_FILEPATH_OPPORTUNITIES:', RELATIVE_FILEPATH_OPPORTUNITIES)
print('RELATIVE_FILEPATH_ANALYSIS:', RELATIVE_FILEPATH_ANALYSIS)

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
filenames_without_infostamp = None
def get_filenames():
    global filenames_with_infostamp
    global filenames_without_infostamp
    filenames_with_infostamp = sorted([
        i[:-LEN_SUFFIX_FILENAME_OPPORTUNITIES]
        for i in listdir(RELATIVE_FILEPATH_OPPORTUNITIES)
        if (    (isfile(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + i))
            and (i not in FILENAMES_SKIP)
            and (len(i) > LEN_SUFFIX_FILENAME_OPPORTUNITIES)
            and (i[-LEN_SUFFIX_FILENAME_OPPORTUNITIES:] == SUFFIX_FILENAME_OPPORTUNITIES)
        )
    ])
    filenames_without_infostamp = sorted(set([
        '--'.join(i.split('--')[:-Infostamp.num_parts])
        for i in filenames_with_infostamp
    ]))

# --------------------------------------------------------------------------------------------------

def analyse_opportunities():
    analysis = {}

    # --------------------------------------------------------------------------------------------------

    for idx_filename_without_infostamp_current, filename_without_infostamp_current in enumerate(filenames_without_infostamp):
        filenames_with_infostamp_current = sorted([
            filename_with_infostamp
            for filename_with_infostamp in filenames_with_infostamp
            if ('--'.join(filename_with_infostamp.split('--')[:-Infostamp.num_parts]) == filename_without_infostamp_current)
        ])

        print(idx_filename_without_infostamp_current, filenames_with_infostamp_current[-1])

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

        if (opportunities_in is not None):
            analysis[filenames_with_infostamp_current[-1]] = {
                'num_items': len(opportunities_in['items'].keys()),
                'num_urls': len(opportunities_in['urls']),
                'status': opportunities_in['status'],
                'activities_counts': get_activities_counts(opportunities_in),
                'coords_counts': get_coords_counts(opportunities_in),
            }

    # --------------------------------------------------------------------------------------------------

    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + FILENAME_ANALYSIS, 'wb') as file_out:
        pickle.dump(analysis, file_out)

# --------------------------------------------------------------------------------------------------

def get_activities_counts(opportunities):
    activities_counts = {}

    for item in opportunities['items'].values():
        item_activities = get_item_activities(item)
        for item_activity in item_activities:
            if (item_activity not in activities_counts.keys()):
                activities_counts[item_activity] = 1
            else:
                activities_counts[item_activity] += 1

    return activities_counts

# --------------------------------------------------------------------------------------------------

def get_item_activities(data):
    item_activities = []

    for key, val in data.items():
        if (key in ['facilityType', 'activity']):
            if (isinstance(val, list)):
                item_activities = [
                    i['prefLabel']
                    for i in val
                    if (    (isinstance(i, dict))
                        and ('prefLabel' in i.keys())
                        and (isinstance(i['prefLabel'], str))
                    )
                ]
            elif (  (isinstance(val, dict))
                and ('prefLabel' in val.keys())
                and (isinstance(val['prefLabel'], str))
            ):
                item_activities = [val['prefLabel']]
        elif (isinstance(val, dict)):
            item_activities = get_item_activities(val)
        if (item_activities):
            break

    return item_activities

# --------------------------------------------------------------------------------------------------

NUM_DECIMAL_PLACES_COORDS = 6

def get_coords_counts(opportunities):
    coords_counts = {}

    for item in opportunities['items'].values():
        item_coords = get_item_coords_from_geo(item)
        if (not item_coords):
            item_coords = get_item_coords_from_postalcode(item)
        if (item_coords):
            item_coords = ','.join([str(item_coord) for item_coord in item_coords])
            if (item_coords not in coords_counts.keys()):
                coords_counts[item_coords] = 1
            else:
                coords_counts[item_coords] += 1

    return coords_counts

# --------------------------------------------------------------------------------------------------

def get_item_coords_from_geo(data):
    item_coords = []

    for key, val in data.items():
        if (    (key == 'geo')
            and (isinstance(val, dict))
            and ('latitude' in val.keys())
            and ('longitude' in val.keys())
        ):
            item_coords = [
                round(float(val['latitude']), NUM_DECIMAL_PLACES_COORDS),
                round(float(val['longitude']), NUM_DECIMAL_PLACES_COORDS)
            ]
        elif (isinstance(val, dict)):
            item_coords = get_item_coords_from_geo(val)
        if (item_coords):
            break

    return item_coords

# --------------------------------------------------------------------------------------------------

postalcodes_coords = {}
time_last_geocode = datetime.now()
def get_item_coords_from_postalcode(data):
    item_coords = []

    global time_last_geocode
    global postalcodes_coords

    for key, val in data.items():
        if (    (key == 'postalCode')
            and (isinstance(val, str))
        ):
            val_mod = val.upper().replace(' ', '')
            if (val_mod not in postalcodes_coords.keys()):
                # https://operations.osmfoundation.org/policies/nominatim/
                # Nominatim usage policy demands "an absolute maximum of 1 request per second", so if less than one
                # second has passed since the last request then wait before proceeding with the next request:
                if ((datetime.now() - time_last_geocode).seconds < 1):
                    sleep(1)
                time_last_geocode = datetime.now()
                loc = geolocator.geocode(val_mod + ',GB')
                if (    (loc is not None)
                    and (loc.latitude is not None)
                    and (loc.longitude is not None)
                ):
                    postalcodes_coords[val_mod] = [
                        round(loc.latitude, NUM_DECIMAL_PLACES_COORDS),
                        round(loc.longitude, NUM_DECIMAL_PLACES_COORDS)
                    ]
                else:
                    print('Can\'t determine coordinates for postalcode:', val)
                    postalcodes_coords[val_mod] = None
            if (postalcodes_coords[val_mod] is not None):
                item_coords = postalcodes_coords[val_mod]
        elif (isinstance(val, dict)):
            item_coords = get_item_coords_from_postalcode(val)
        if (item_coords):
            break

    return item_coords

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        get_filenames()
        analyse_opportunities()
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')