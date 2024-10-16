#READ ME from HA :)
#I'm using review.py to launch this job at the mo
#It calls read pickle and create summary functions
#I use check.py and check_summary.py to explore the results
#import nspl and import casc are 'run once a year' kind of jobs to update ref data in data-analysis bucket
#Working on get postcodes.py to get missing postcodes - will give it another few hours
#Then match to nspl.py to get a base table of opportnuties with location / deprivation
#Then need to fold back the matching into analysis job to produce cross-tab of location and activity

from read_pickle_functions import *
from create_summary_functions import *
from os import getenv

MERGE_FEEDS = getenv('MERGE_FEEDS', 'False').title()
MERGE_FEEDS = True if (MERGE_FEEDS == 'True') else False
VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False


# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    MERGE_FEEDS = True
    VERBOSE = True

    try:
        filenames_with_infostamp, filenames_without_infostamp = get_filenames()
        pairs_filenames_without_infostamp = get_pairs_filenames_without_infostamp(filenames_without_infostamp)
        pairs_filenames_with_infostamp = get_pairs_filenames_with_infostamp(pairs_filenames_without_infostamp, filenames_with_infostamp)

        print(pairs_filenames_without_infostamp[-20:])
        
        analyse_opportunities(pairs_filenames_with_infostamp, merge_feeds=MERGE_FEEDS, verbose=VERBOSE)
        create_summary()
        
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')