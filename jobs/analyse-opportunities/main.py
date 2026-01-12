import sys
from analyse_separate_opportunities import analyse_separate_opportunities
# from analyse_separate_opportunities_new import analyse_separate_opportunities_new
from analyse_aggregate_opportunities import analyse_aggregate_opportunities
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
        # analyse_separate_opportunities_new(verbose=VERBOSE)
        analyse_aggregate_opportunities(verbose=VERBOSE)
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')