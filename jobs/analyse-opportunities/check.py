import pandas as pd
import pickle
from os import getenv
import gzip

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

print(df_analysis_data[df_analysis_data['address_counts']=={}][['num_items','file_name','file_name_partner']])


#HERE - bookteq slots and facilities are not bringing through addresses
#So - the total counts with postcodes that can be matched to nspl is only 3.1 m not 5.2


# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'postcode_counts.pickle', 'rb') as file_in:
    df_pcodes = pickle.load(file_in)

#print(df_pcodes.head())
#print(len(df_pcodes))
#print(sum(df_pcodes['count']))

RELATIVE_FILEPATH_OPPORTUNITIES = getenv('RELATIVE_FILEPATH_OPPORTUNITIES', '../volume-1/data-opportunities')

#filename = 'wycliffecollege-bookteq-com-api-open-active-slots--timeFinish-2024-09-18-02-31-20-218864-UTC--timeTaken-2-514024--numItems-41224--numUrls-286--status-ERROR.pickle.gzip'
#filename = 'wycliffecollege-bookteq-com-api-open-active-facility-uses--timeFinish-2024-10-09-01-38-55-530587-UTC--timeTaken-1-468848--numItems-16--numUrls-1--status-COMPLETE.pickle.gzip'
# Load the pickle file
#with gzip.open(RELATIVE_FILEPATH_OPPORTUNITIES + '/' + filename, 'rb') as file_in:
#    test = pickle.load(file_in)

#print(test)  
# Assuming 'test['items']' is a dictionary
#print(next(iter(test['items'].items()))) 
