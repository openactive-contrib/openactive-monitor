import pandas as pd
import geopandas as gpd
import pickle
import sys
from os import getenv
from shapely.geometry import Point, box
import time
import json
import warnings


#One option to speed up would be to check for dup'd coords before lookup

pd.set_option('display.max_colwidth', 150) 

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
ANALYSIS_FILENAME = 'analysis.pickle'
NSPL_PICKLE_FILENAME = 'nspl.pickle'

# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + ANALYSIS_FILENAME, 'rb') as file_in:
    df_analysis_data = pickle.load(file_in)

# Load the NSPL data
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + NSPL_PICKLE_FILENAME, 'rb') as file_in:
    df_nspl = pickle.load(file_in) 
print(len(df_nspl))
# For matching, exclude postcodes with invalid coords
df_nspl = df_nspl[(df_nspl['long'] >= -8.163139) & 
                  (df_nspl['long'] <= 1.762773) & 
                  (df_nspl['lat'] >= 49.895171) & 
                  (df_nspl['lat'] <= 61.0000)]
print(len(df_nspl))

# Create a geometry column from lat and long
df_nspl['geometry'] = gpd.points_from_xy(df_nspl['long'], df_nspl['lat'])

# Convert to GeoDataFrame
df_nspl = gpd.GeoDataFrame(df_nspl, geometry='geometry', crs='epsg:4326')

# Prepare a sample DataFrame for testing
#sample_size = 1000  # Adjust as needed
#address_counts_df = df_analysis_data['df_total_address_counts'].sample(sample_size)
address_counts_df = df_analysis_data['df_total_address_counts']
address_counts_df['extracted_postcode'] = address_counts_df['address'].str.extract(r'([A-Z]{1,2}[0-9]{1,2}[A-Z0-9]? ?[0-9][A-Z]{2})')

print(address_counts_df)

# Print one full row
print(address_counts_df.iloc[0]) 

# --- Method 1: Without Spatial Index ---
start_time = time.time()

def find_nearest_postcode(row):
    if pd.isna(row.extracted_postcode):  # Access using attribute notation
        # Access geocoordinates, handling nested 'geo' dictionary
        coords = None
        if hasattr(row, 'address'):  # Check if the attribute exists
            address_data = json.loads(row.address)  # Access using attribute notation
            if 'geo' in address_data:
                geocoordinates = address_data['geo']
                if 'longitude' in geocoordinates and 'latitude' in geocoordinates:
                    coords = (geocoordinates['longitude'], geocoordinates['latitude'])
        if coords is not None:
            point = Point(coords)
            # Only proceed if coords in UK bounding box
            if (point.x >= -8.163139) and (point.x <= 1.762773) and (point.y >= 49.895171) and (point.y <= 61.0000): 
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    distances = df_nspl.geometry.distance(point)
                    # Handle edge cases:
                    if not distances.empty:
                        nearest_index = distances.idxmin()
                        # Ensure nearest_index is valid:
                        if nearest_index in df_nspl.index:
                            return df_nspl.loc[nearest_index]['pcds'] 
                        else:
                            #print("No nearest postcode")
                            return row.extracted_postcode  # Access using attribute notation
        else:
            #print("No coords")
            return row.extracted_postcode  # Access using attribute notation
    else:
        return row.extracted_postcode  # Access using attribute notation


# Add a counter and progress display
total_rows = len(address_counts_df)
for i, row in enumerate(address_counts_df.itertuples(), 1):  # Start counter from 1
    address_counts_df.loc[row.Index, 'nearest_postcode'] = find_nearest_postcode(row)
    if i % 1000 == 0:
        print(f"Processed {i}/{total_rows} rows ({(i/total_rows)*100:.2f}%)")


#address_counts_df['nearest_postcode'] = address_counts_df.apply(find_nearest_postcode, axis=1)

end_time = time.time()
time_without_index = end_time - start_time
print(f"Time taken without spatial index: {time_without_index:.2f} seconds")

# Calculate and print the number of postcodes obtained
postcodes_obtained = address_counts_df['extracted_postcode'].notna().sum()
print(f"Number of postcodes extracted: {postcodes_obtained}")
postcodes_obtained = address_counts_df['nearest_postcode'].notna().sum()
print(f"Number of postcodes obtained: {postcodes_obtained}")

postcode_data = []
missing_count = 0  # Initialize count for missing postcodes

for i in range(len(address_counts_df)):
    postcode = address_counts_df.iloc[i]['nearest_postcode']
    
    # Find if postcode already exists in postcode_data
    existing_postcode = next((item for item in postcode_data if item['postcode'] == postcode), None)
    
    if existing_postcode:
        # If postcode exists, increment count
        existing_postcode['count'] += address_counts_df.iloc[i]['count']
    else:
        # If postcode doesn't exist, add it to the list
        if pd.notna(postcode):
            postcode_data.append({
                'postcode': postcode.strip(),
                'count': address_counts_df.iloc[i]['count'],
            })
        else:
            # Increment the missing count
            missing_count += address_counts_df.iloc[i]['count']

# After processing all rows, add the 'Missing' entry
postcode_data.append({
    'postcode': 'Missing',
    'count': missing_count,
})

# Create a DataFrame from the postcode data
postcode_df = pd.DataFrame(postcode_data)

# Save the postcode DataFrame to a pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'postcode_counts.pickle', 'wb') as file_out:
    pickle.dump(postcode_df, file_out)
