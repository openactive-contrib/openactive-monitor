import pandas as pd
import geopandas as gpd
import pickle
import sys
from os import getenv
from shapely.geometry import Point, box
import time
import json
import warnings

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
sample_size = 1000  # Adjust as needed
address_counts_df = df_analysis_data['df_total_address_counts'].sample(sample_size)
address_counts_df['extracted_postcode'] = address_counts_df['address'].str.extract(r'([A-Za-z]{1,2}[0-9]{1,2}[A-Za-z0-9]? ?[0-9][A-Za-z]{2})')

print(address_counts_df)

# Print one full row
print(address_counts_df.iloc[0]) 

# --- Method 1: Without Spatial Index ---
start_time = time.time()

def find_nearest_postcode(row):
    if pd.isna(row['extracted_postcode']):
        # Access geocoordinates, handling nested 'geo' dictionary
        coords = None
        if 'address' in row:
            address_data = json.loads(row['address'])
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
                            print("No nearest postcode")
                            return row['extracted_postcode']
        else:
            print("No coords")
            return row['extracted_postcode']
    else:
        return row['extracted_postcode']  # Keep the existing postcode

address_counts_df['nearest_postcode'] = address_counts_df.apply(find_nearest_postcode, axis=1)

end_time = time.time()
time_without_index = end_time - start_time
print(f"Time taken without spatial index: {time_without_index:.2f} seconds")

# --- Method 2: With Spatial Index ---
start_time = time.time()

# 2. Create spatial index
df_nspl.sindex

def find_nearest_postcode_with_index(row):
    if pd.isna(row['extracted_postcode']):
        # Access geocoordinates, handling nested 'geo' dictionary
        coords = None
        if 'address' in row:
            address_data = json.loads(row['address'])
            if 'geo' in address_data:
                geocoordinates = address_data['geo']
                if 'longitude' in geocoordinates and 'latitude' in geocoordinates:
                    # Only proceed if coords in UK bounding box
                    if (geocoordinates['longitude'] >= -8.163139) and (geocoordinates['longitude'] <= 1.762773) and (geocoordinates['latitude'] >= 49.895171) and (geocoordinates['latitude'] <= 61.0000):
                        coords = (geocoordinates['longitude'], geocoordinates['latitude'])
        if coords is not None:
            point = Point(coords)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                nearest_index = list(df_nspl.sindex.nearest(point, 1))[1][0]
                print(nearest_index)
                # Ensure nearest_index is valid:
                if nearest_index in df_nspl.index:
                    pcode = df_nspl.loc[nearest_index]['pcds']
                    print(pcode)
                    return pcode
                else:
                    print("No nearest postcode")
                    return row['extracted_postcode']
        else:
            print("No coords")
            return row['extracted_postcode'] 
    else:
        return row['extracted_postcode']  


address_counts_df['nearest_postcode_index'] = address_counts_df.apply(find_nearest_postcode_with_index, axis=1)

end_time = time.time()
time_with_index = end_time - start_time
print(f"Time taken with spatial index: {time_with_index:.2f} seconds")

# Calculate and print the number of postcodes obtained
postcodes_obtained = address_counts_df['extracted_postcode'].notna().sum()
print(f"Number of postcodes extracted: {postcodes_obtained}")
postcodes_obtained = address_counts_df['nearest_postcode'].notna().sum()
print(f"Number of postcodes obtained without index: {postcodes_obtained}")
postcodes_obtained = address_counts_df['nearest_postcode_index'].notna().sum()
print(f"Number of postcodes obtained with index: {postcodes_obtained}")

print(f"Speedup: {time_without_index / time_with_index:.2f}x faster with spatial index")


print(address_counts_df[['extracted_postcode','nearest_postcode','nearest_postcode_index']])

# Create a boolean mask to identify rows where the columns are different
different_postcodes_mask = (address_counts_df['nearest_postcode'] != address_counts_df['nearest_postcode_index']) & (address_counts_df['nearest_postcode_index'].notna())

# Use the mask to filter the DataFrame and print only the relevant rows
print(address_counts_df[different_postcodes_mask][['address', 'nearest_postcode', 'nearest_postcode_index']])
