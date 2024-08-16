import gzip
import lzma
import pickle
import random
import sys
from datetime import datetime, timedelta
from dateutil import tz # For timezone handling
from geopy.geocoders import Nominatim
from openactive import get_item_kinds, get_item_data_types
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
RELATIVE_FILEPATH_ANALYSES = getenv('RELATIVE_FILEPATH_ANALYSES', '../volume-1/data-analysis')

FILENAME_FEEDS_SEEN = '000-feeds-seen.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAME_FEEDS_CRASHED = '000-feeds-crashed.txt' # Located in RELATIVE_FILEPATH_OPPORTUNITIES
FILENAMES_SKIP = [FILENAME_FEEDS_SEEN, FILENAME_FEEDS_CRASHED] # Filenames to skip when checking for opportunity files in RELATIVE_FILEPATH_OPPORTUNITIES
FORMAT_FILE_OPPORTUNITIES = 'pickle'
COMPRESSION_FILE_OPPORTUNITIES = getenv('COMPRESSION_FILE_OPPORTUNITIES', 'gzip').lower() # 'none' / 'gzip' / 'xz'
SUFFIX_FILENAME_OPPORTUNITIES = '.' + FORMAT_FILE_OPPORTUNITIES + (('.' + COMPRESSION_FILE_OPPORTUNITIES) if (COMPRESSION_FILE_OPPORTUNITIES != 'none') else '')
LEN_SUFFIX_FILENAME_OPPORTUNITIES = len(SUFFIX_FILENAME_OPPORTUNITIES)
FILENAME_ANALYSES = getenv('FILENAME_ANALYSES', 'analysis.pickle')
FILENAME_ANALYSES_THIS_WEEK = getenv('FILENAME_ANALYSES_THIS_WEEK', 'analyses-this-week.pickle')

print('Environment variables:')
print('RELATIVE_FILEPATH_OPPORTUNITIES:', RELATIVE_FILEPATH_OPPORTUNITIES)
print('RELATIVE_FILEPATH_ANALYSES:', RELATIVE_FILEPATH_ANALYSES)
print('COMPRESSION_FILE_OPPORTUNITIES:', COMPRESSION_FILE_OPPORTUNITIES)
print('FILENAME_ANALYSES:', FILENAME_ANALYSES)
print('FILENAME_ANALYSES_THIS_WEEK:', FILENAME_ANALYSES_THIS_WEEK)

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
    analyses = {}
    analyses_this_week = {}

    # --------------------------------------------------------------------------------------------------

    for idx_filename_without_infostamp_current, filename_without_infostamp_current in enumerate(filenames_without_infostamp):
        try:
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
                analyses[filenames_with_infostamp_current[-1]] = {
                    'status': opportunities_in['status'],
                    'num_items': len(opportunities_in['items'].keys()),
                    'num_urls': len(opportunities_in['urls']),
                    'item_kinds': get_item_kinds(opportunities_in),
                    'item_data_types': get_item_data_types(opportunities_in),
                    'activities_counts': get_activities_counts(opportunities_in),
                    'coords_counts': get_coords_counts(opportunities_in), #, filenames_with_infostamp_current[-1]), # TEMPORARY: For checking geographically localised high opportunity count spikes
                }

                items_this_week = get_items_this_week(opportunities_in)
                items_this_week_sample = dict(random.sample(list(items_this_week.items()), min(2, len(items_this_week.keys()))))

                analyses_this_week[filenames_with_infostamp_current[-1]] = {
                    'status': opportunities_in['status'],
                    'num_items': len(items_this_week.keys()),
                    'num_items_sample': len(items_this_week_sample.keys()),
                    'items_sample': items_this_week_sample,
                    'item_kinds': get_item_kinds({'items': items_this_week}),
                    'item_data_types': get_item_data_types({'items': items_this_week}),
                    'activities_counts': get_activities_counts({'items': items_this_week}),
                    'coords_counts': get_coords_counts({'items': items_this_week}),
                }

        except Exception as error:
            print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    with open(RELATIVE_FILEPATH_ANALYSES + '/' + FILENAME_ANALYSES, 'wb') as file_out:
        pickle.dump(analyses, file_out)

    with open(RELATIVE_FILEPATH_ANALYSES + '/' + FILENAME_ANALYSES_THIS_WEEK, 'wb') as file_out:
        pickle.dump(analyses_this_week, file_out)

    # TEMPORARY: For checking geographically localised high opportunity count spikes
    # global coords_check
    # with open(RELATIVE_FILEPATH_ANALYSES + '/' + 'coords_check.pickle', 'wb') as file_out:
    #     pickle.dump(coords_check, file_out)

    # print(len(analyses_this_week))
    # print(analyses_this_week)

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

# TEMPORARY: For checking geographically localised high opportunity count spikes
# coords_check = {}

def get_coords_counts(opportunities): #, filename=None)
    coords_counts = {}

    # TEMPORARY: For checking geographically localised high opportunity count spikes
    # global coords_check

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
            # TEMPORARY: For checking geographically localised high opportunity count spikes
            # if (    (filename is not None)
            #     and (item_coords == '52.069694,-2.722774')
            # ):
            #     if (filename not in coords_check.keys()):
            #         coords_check[filename] = 1
            #     else:
            #         coords_check[filename] += 1

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

def get_items_this_week(opportunities):
    items_this_week = {}

    today = datetime.now(tz=tz.UTC).date()

    for item_id, item in opportunities['items'].items():
        item_start_date = get_item_start_date(item)
        if (    (item_start_date is not None)
            and (item_start_date.date() >= today)
            and (item_start_date.date() <= today + timedelta(days=7))
        ):
            items_this_week[item_id] = item

    return items_this_week

# --------------------------------------------------------------------------------------------------

def get_item_start_date(item):
    if ('startDate' in item['data'].keys()):
        return parse_date(item['data']['startDate'])
    elif ('dateStart' in item['data'].keys()):
        return parse_date(item['data']['dateStart'])
    elif (  ('subEvent' in item['data'].keys())
        and (isinstance(item['data']['subEvent'], list))
    ):
        for subevent in item['data']['subEvent']:
            if (    (isinstance(subevent, dict))
                and ('startDate' in subevent.keys())
            ):
                return parse_date(subevent['startDate'])

    return None

# --------------------------------------------------------------------------------------------------

def parse_date(date_string):
    date_formats = [
        '%Y-%m-%dT%H:%M:%SZ', # ISO 8601 format
        '%Y-%m-%d %H:%M:%S', # Common date/time format
        '%Y-%m-%d', # Date only format
        '%Y/%m/%d', # Another common date format
        '%Y-%m-%dT%H:%M:%S.%fZ', # ISO 8601 with milliseconds
        '%Y-%m-%dT%H:%M:%S.%f', # ISO 8601 with milliseconds (no Z)
        '%Y-%m-%dT%H:%M:%S%z', # ISO 8601 with timezone offset
        '%Y-%m-%dT%H:%M:%S%Z', # ISO 8601 with timezone name
    ]

    for date_format in date_formats:
        try:
            parsed_datetime = datetime.strptime(date_string, date_format)
            # If the date string has a timezone, use it:
            if (date_format in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S%Z']):
                return parsed_datetime.astimezone(tz.UTC)
            # Otherwise, assume UTC and set the timezone:
            else:
                return parsed_datetime.replace(tzinfo=tz.UTC)
        except:
            pass

    return None

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