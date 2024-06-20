# import gzip
import lzma
import pickle
import sys
from datetime import datetime
from geopy.geocoders import Nominatim
from os import getenv, listdir
from os.path import isfile
from time import sleep

# --------------------------------------------------------------------------------------------------

geolocator = Nominatim(user_agent='OpenActive All Data Harvester', timeout=None)

# --------------------------------------------------------------------------------------------------

# FILETYPE_OPPORTUNITIES = getenv('FILETYPE_OPPORTUNITIES', 'uncompressed') # uncompressed / gzip / lzma
# if (FILETYPE_OPPORTUNITIES == 'uncompressed'):
#     FILENAME_OPPORTUNITIES_SUFFIX = '.pickle'
# elif (FILETYPE_OPPORTUNITIES == 'gzip'):
#     FILENAME_OPPORTUNITIES_SUFFIX = '.pickle.gzip'
# elif (FILETYPE_OPPORTUNITIES == 'lzma'):
#     FILENAME_OPPORTUNITIES_SUFFIX = '.pickle.xz'
FILENAME_OPPORTUNITIES_SUFFIX = '.pickle.xz'
LEN_FILENAME_OPPORTUNITIES_SUFFIX = len(FILENAME_OPPORTUNITIES_SUFFIX)
# FILENAME_ANALYSIS = 'analysis-' + FILETYPE_OPPORTUNITIES + '.pickle'
FILENAME_ANALYSIS = 'analysis.pickle'

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'analyse-opportunities', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update analyse-opportunities \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-all-data-harvester_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
# FILEPATH_RELATIVE_OPPORTUNITIES = getenv('FILEPATH_RELATIVE_OPPORTUNITIES', '../volume-1/data-opportunities-test-' + FILETYPE_OPPORTUNITIES)
FILEPATH_RELATIVE_OPPORTUNITIES = getenv('FILEPATH_RELATIVE_OPPORTUNITIES', '../volume-1/data-opportunities')
FILEPATH_RELATIVE_ANALYSIS = getenv('FILEPATH_RELATIVE_ANALYSIS', '../volume-1/data-analysis')

print('FILEPATH_RELATIVE_OPPORTUNITIES:', FILEPATH_RELATIVE_OPPORTUNITIES)
print('FILEPATH_RELATIVE_ANALYSIS:', FILEPATH_RELATIVE_ANALYSIS)

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
filenames_without_infostamp = None
def get_filenames():
    global filenames_with_infostamp
    global filenames_without_infostamp
    filenames_with_infostamp = sorted([
        i[:-LEN_FILENAME_OPPORTUNITIES_SUFFIX]
        for i in listdir(FILEPATH_RELATIVE_OPPORTUNITIES)
        if (    (isfile(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + i))
            and (len(i) > LEN_FILENAME_OPPORTUNITIES_SUFFIX)
            and (i[-LEN_FILENAME_OPPORTUNITIES_SUFFIX:] == FILENAME_OPPORTUNITIES_SUFFIX)
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

        print(datetime.now(), idx_filename_without_infostamp_current, filenames_with_infostamp_current[-1])

        # if (FILETYPE_OPPORTUNITIES == 'uncompressed'):
        #     with open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_OPPORTUNITIES_SUFFIX, 'rb') as file_in:
        #         opportunities = pickle.load(file_in)
        # elif (FILETYPE_OPPORTUNITIES == 'gzip'):
        #     with gzip.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_OPPORTUNITIES_SUFFIX, 'rb') as file_in:
        #         opportunities = pickle.load(file_in)
        # elif (FILETYPE_OPPORTUNITIES == 'lzma'):
        #     with lzma.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_OPPORTUNITIES_SUFFIX, 'rb') as file_in:
        #         opportunities = pickle.load(file_in)

        with lzma.open(FILEPATH_RELATIVE_OPPORTUNITIES + '/' + filenames_with_infostamp_current[-1] + FILENAME_OPPORTUNITIES_SUFFIX, 'rb') as file_in:
            opportunities = pickle.load(file_in)

        analysis[filenames_with_infostamp_current[-1]] = {
            'num_items': len(opportunities['items'].keys()),
            'num_urls': len(opportunities['urls']),
            'status': opportunities['status'],
            'activities_counts': get_activities_counts(opportunities),
            'coords_counts': get_coords_counts(opportunities),
        }

    # --------------------------------------------------------------------------------------------------

    with open(FILEPATH_RELATIVE_ANALYSIS + '/' + FILENAME_ANALYSIS, 'wb') as file_out:
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

NUM_DECIMAL_PLACES_COORDS = 7

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
            val = val.upper().replace(' ', '')
            if (val not in postalcodes_coords.keys()):
                if ((datetime.now() - time_last_geocode).seconds < 1):
                    sleep(1)
                time_last_geocode = datetime.now()
                loc = geolocator.geocode(val + ',GB')
                if (    (loc is not None)
                    and (loc.latitude is not None)
                    and (loc.longitude is not None)
                ):
                    postalcodes_coords[val] = [
                        round(loc.latitude, NUM_DECIMAL_PLACES_COORDS),
                        round(loc.longitude, NUM_DECIMAL_PLACES_COORDS)
                    ]
                else:
                    print('Can\'t determine coordinates for postalcode', val)
                    postalcodes_coords[val] = None
            if (postalcodes_coords[val] is not None):
                item_coords = postalcodes_coords[val]
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