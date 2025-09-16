from analyse_opportunities_per_feed import analyse_opportunities_per_feed
from analyse_opportunities_aggregated import analyse_opportunities_aggregated
from os import getenv

VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

print('Environment variables:')
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    try:
        analyse_opportunities_per_feed(verbose=VERBOSE)
        analyse_opportunities_aggregated(verbose=VERBOSE)
    except Exception as error:
        print('ERROR:', error)

    # --------------------------------------------------------------------------------------------------

    print('\nFinished')