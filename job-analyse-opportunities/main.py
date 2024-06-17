# import gzip
import lzma
import pickle
import sys
from datetime import datetime
from os import getenv, listdir
from os.path import isfile

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
        '--'.join(i.split('--')[:-5])
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
            if ('--'.join(filename_with_infostamp.split('--')[:-5]) == filename_without_infostamp_current)
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
            'status': opportunities['status'],
            'num_urls': len(opportunities['urls']),
            'num_items': len(opportunities['items'].keys()),
        }

    # --------------------------------------------------------------------------------------------------

    with open(FILEPATH_RELATIVE_ANALYSIS + '/' + FILENAME_ANALYSIS, 'wb') as file_out:
        pickle.dump(analysis, file_out)

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        get_filenames()
        analyse_opportunities()
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)