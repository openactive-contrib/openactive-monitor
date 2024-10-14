import pandas as pd
import pickle
from os import getenv
import json
import re

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
filename = 'analysis.pickle'
NSPL_PICKLE_FILENAME = 'nspl.pickle'

def is_valid_uk_postcode(postcode):
    postcode = postcode.strip()
    """Checks if a given string is a valid UK postcode."""
    regex = r"^[A-Z]{1,2}[0-9]{1,2}[A-Z0-9]? ?[0-9][A-Z]{2}$"
    match = re.match(regex, postcode.upper())
    return bool(match)

#Moving towards creating a postcode for each record, from coords if necessary for nspl matching
#4 positions:
#1) Item has postcode and coords - use postcode
#2) Item has postcode no coords - use postcode
#3) Item has coords no postcode - find nearest centroid and use that postcode
#4) Item has no postcode no coords - if not online event, use an organiser postcode, otherwise flag as missing

# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + filename, 'rb') as file_in:
    df_analysis_data = pickle.load(file_in)

with open(RELATIVE_FILEPATH_ANALYSIS + '/' + NSPL_PICKLE_FILENAME, 'rb') as file_in:
    df_nspl = pickle.load(file_in)


# Access the 'df_total_address_counts' DataFrame
address_counts_df = df_analysis_data['df_total_address_counts']

print(f"Number of rows in address_counts_df: {len(address_counts_df)}")

postcode_data = []
for i in range(len(address_counts_df)):
    address_data = json.loads(address_counts_df.iloc[i]['address'])
    parts = []
    for key, value in address_data.items():
        if isinstance(value, str):
            parts.extend(value.split(','))
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    parts.extend(sub_value.split(','))           
    for part in parts:
        if is_valid_uk_postcode(part):
            postcode_data.append({
                'postcode': part.strip(),
                'count': address_counts_df.iloc[i]['count'],
                'percentage': address_counts_df.iloc[i]['percentage']
            })
            # Skip to the next address (outer loop)
            break  # Exit the inner loop
    
            

postcode_df = pd.DataFrame(postcode_data)

print(f"Number of rows in postcode_df: {len(postcode_df)}")
print(f"Number of rows with no postcode: {len(address_counts_df)-len(postcode_df)}")

# Save the postcode DataFrame to a pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'postcode_counts.pickle', 'wb') as file_out:
    pickle.dump(postcode_df, file_out)



