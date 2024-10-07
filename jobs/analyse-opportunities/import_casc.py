#list found online at: https://www.gov.uk/government/publications/community-amateur-sports-clubs-casc-registered-with-hmrc--2
#Converted to csv via Google Sheets

import pandas as pd
import pickle
from os import getenv

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
CASC_filename = 'List_of_registered_CASC.csv'
CASC_PICKLE_FILENAME = 'casc.pickle'

casc_df = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + CASC_filename)

print("Available columns:", casc_df.columns.tolist())
print("Number of rows before filtering:", len(casc_df))
print(casc_df)

#Save the dataframe to a pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + CASC_PICKLE_FILENAME, 'wb') as file_out:
    pickle.dump(casc_df, file_out)