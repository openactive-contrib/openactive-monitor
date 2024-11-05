from read_pickle_functions import *
from create_summary_functions import *
from os import getenv

VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False


# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):

    VERBOSE = True

    try:
        filenames_with_infostamp, filenames_without_infostamp = get_filenames()
        pairs_filenames_without_infostamp = get_pairs_filenames_without_infostamp(filenames_without_infostamp)
        pairs_filenames_with_infostamp = get_pairs_filenames_with_infostamp(pairs_filenames_without_infostamp, filenames_with_infostamp)

        analyse_opportunities(pairs_filenames_with_infostamp,verbose=VERBOSE)
        create_summary()
        
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')