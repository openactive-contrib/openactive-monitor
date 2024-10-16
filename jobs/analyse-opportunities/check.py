import pandas as pd
import pickle
from os import getenv
import gzip
import sys

pd.set_option('display.max_colwidth', 150)  # Set max width to 100 characters

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
filename = 'analysis-data.pickle'

# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + filename, 'rb') as file_in:
    df_analysis_data = pickle.load(file_in)

# List the columns
print("Available columns:", df_analysis_data.columns.tolist())

# Show a sample of the 'address_counts' column
print("Sample of 'address_counts' column:")
print(df_analysis_data['address_counts'])


print(df_analysis_data[['num_items','file_name']])


print('These feeds are not empty but have no addresses - to investigate:')
address_empty = df_analysis_data['address_counts'] == {}
items_greater_than_zero = df_analysis_data['num_items'] > 0

if address_empty.empty or items_greater_than_zero.empty:
    print("One or both conditions resulted in an empty selection.")
    # Handle the empty case (e.g., return an empty DataFrame)
else:
    result = df_analysis_data[address_empty & items_greater_than_zero][['num_items', 'file_name']]
    print(result)


# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'postcode_counts.pickle', 'rb') as file_in:
    df_pcodes = pickle.load(file_in)

print(df_pcodes.head())
print(len(df_pcodes))
print(sum(df_pcodes['count']))
print("Opps with missing postcode:")
print(df_pcodes[df_pcodes['postcode'] == 'Missing']['count'].sum())

#sys.exit()


#To explore a file...

RELATIVE_FILEPATH_OPPORTUNITIES = getenv('RELATIVE_FILEPATH_OPPORTUNITIES', '../volume-1/data-opportunities')

#filename = 'wycliffecollege-bookteq-com-api-open-active-slots--timeFinish-2024-09-18-02-31-20-218864-UTC--timeTaken-2-514024--numItems-41224--numUrls-286--status-ERROR.pickle.gzip'
#filename = 'wycliffecollege-bookteq-com-api-open-active-facility-uses--timeFinish-2024-10-09-01-38-55-530587-UTC--timeTaken-1-468848--numItems-16--numUrls-1--status-COMPLETE.pickle.gzip'
filename = 'theblackprincetrust-bookteq-com-api-open-active-slots--timeFinish-2024-10-09-01-37-27-690368-UTC--timeTaken-0-422770--numItems-2302--numUrls-28--status-COMPLETE.pickle.gzip'
# Load the pickle file
with gzip.open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filename, 'rb') as file_in:
    test = pickle.load(file_in)

#print(test)  
# Assuming 'test['items']' is a dictionary
print(next(iter(test['items'].items()))) 

#FacilityUse is an id - so either matching or orphaning not working right?