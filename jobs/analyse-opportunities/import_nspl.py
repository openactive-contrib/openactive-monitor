import pandas as pd
import pickle
from os import getenv

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
NSPL_filename = 'NSPL21_NOV_2023_UK.csv'
NSPL_PICKLE_FILENAME = 'nspl.pickle'

nspl_df = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + NSPL_filename, dtype={'npark': 'string'})

print("Available columns:", nspl_df.columns.tolist())
print("Number of rows before filtering:", len(nspl_df))

# Filter for live postcodes
live_nspl_df = nspl_df[nspl_df['doterm'].isnull()]
print("Number of rows after filtering:", len(live_nspl_df))

# Select desired columns
selected_columns = ['pcds', 'rgn', 'imd', 'laua', 'npark', 'icb', 'lat', 'long']
live_nspl_selected_df = live_nspl_df[selected_columns]

print(live_nspl_selected_df.head())

#Save the dataframe to a pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + NSPL_PICKLE_FILENAME, 'wb') as file_out:
    pickle.dump(live_nspl_selected_df, file_out)
