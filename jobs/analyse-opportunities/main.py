from read_pickle_functions import *
from create_summary_functions import *

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        filenames_with_infostamp, filenames_without_infostamp = get_filenames()
        pairs_filenames_without_infostamp = get_pairs_filenames_without_infostamp(filenames_without_infostamp)
        pairs_filenames_with_infostamp = get_pairs_filenames_with_infostamp(pairs_filenames_without_infostamp, filenames_with_infostamp)
        print(pairs_filenames_without_infostamp)
        
        analyse_opportunities(pairs_filenames_with_infostamp, merge_feeds=MERGE_FEEDS, verbose=VERBOSE)
        create_summary()
        
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')