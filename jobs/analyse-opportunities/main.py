from analyse_opportunities_per_feed import get_filenames, get_pairs_filenames_without_infostamp, get_pairs_filenames_with_infostamp, analyse_opportunities_per_feed
from analyse_opportunities_aggregated import analyse_opportunities_aggregated
from os import getenv

VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):

    try:
        filenames_with_infostamp, filenames_without_infostamp = get_filenames()
        pairs_filenames_without_infostamp = get_pairs_filenames_without_infostamp(filenames_without_infostamp)
        pairs_filenames_with_infostamp = get_pairs_filenames_with_infostamp(pairs_filenames_without_infostamp, filenames_with_infostamp)
        analyse_opportunities_per_feed(pairs_filenames_with_infostamp, verbose=VERBOSE)
        analyse_opportunities_aggregated()
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')