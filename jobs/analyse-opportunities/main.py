import sys
from analyse_opportunities_per_feed import analyse_opportunities_per_feed
from analyse_opportunities_aggregated import analyse_opportunities_aggregated
from os import getenv

sys.path.append('../volume-1/common')
from settings import *

# --------------------------------------------------------------------------------------------------

VERBOSE = getenv('VERBOSE', str(ANALYSE_OPPORTUNITIES_VERBOSE)).title()
VERBOSE = True if (VERBOSE == 'True') else False

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        analyse_separate_opportunities(verbose=VERBOSE)
        analyse_aggregate_opportunities(verbose=VERBOSE)
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')