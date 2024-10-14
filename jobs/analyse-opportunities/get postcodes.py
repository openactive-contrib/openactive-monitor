import pandas as pd
import pickle
from os import getenv
import json
import re
from geopy.geocoders import Nominatim
from shapely.geometry import Point, box
from shapely.ops import transform
from functools import partial
import pyproj
import geopandas as gpd  # Import geopandas
import warnings

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
filename = 'analysis.pickle'
NSPL_PICKLE_FILENAME = 'nspl.pickle'

def is_valid_uk_postcode(postcode):
    postcode = postcode.strip()
    """Checks if a given string is a valid UK postcode."""
    regex = r"^[A-Z]{1,2}[0-9]{1,2}[A-Z0-9]? ?[0-9][A-Z]{2}$"
    match = re.match(regex, postcode.upper())
    return bool(match)

# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + filename, 'rb') as file_in:
    df_analysis_data = pickle.load(file_in)

# Load the NSPL data using geopandas
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + NSPL_PICKLE_FILENAME, 'rb') as file_in:
    df_nspl = pickle.load(file_in)  # Use gpd.read_file

# Create a geometry column from lat and long
df_nspl['geometry'] = gpd.points_from_xy(df_nspl['long'], df_nspl['lat'])

# Convert to GeoDataFrame
df_nspl = gpd.GeoDataFrame(df_nspl, geometry='geometry', crs='epsg:4326')

# Create a bounding box polygon
bbox_polygon = gpd.GeoDataFrame(
    {'geometry': [box(-8.163139, 49.895171, 1.762773, 61.0000)]},
    crs='epsg:4326'
)

# Identify points outside the bounding box
points_outside_bbox = df_nspl[~df_nspl.intersects(bbox_polygon.geometry[0])]

# Print the points outside the bounding box
print(points_outside_bbox)

# Access the 'df_total_address_counts' DataFrame
address_counts_df = df_analysis_data['df_total_address_counts']

print(f"Number of rows in address_counts_df: {len(address_counts_df)}")

postcode_data = []

#Checking counts
coords_count = 0 
no_pcode = 0
pcodes = 0

for i in range(len(address_counts_df)):
    if i % 1000 == 0:
        print(i)
    #Take each address
    address_data = json.loads(address_counts_df.iloc[i]['address'])
    
    #Split into parts and look for a postcode
    postcode_found = False
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
            pcodes+=1
            postcode_found = True
            break  
    if not postcode_found:
        coords = None
        nearest_postcode = None
        # Access geocoordinates directly
        if 'geo' in address_data:
            geocoordinates = address_data['geo']
            if 'longitude' in geocoordinates and 'latitude' in geocoordinates:
                coords = (geocoordinates['longitude'], geocoordinates['latitude'])
        if coords is not None:
            # Find nearest postcode using geospatial matching
            point = Point(coords)
            if (point.x >= -8.163139) and (point.x <= 1.762773) and (point.y >= 49.895171) and (point.y <= 61.0000): 
                # Suppress the warning only for this specific operation
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    nearest_postcode = df_nspl.loc[
                        df_nspl.geometry.distance(point).idxmin()
                    ]["pcds"]
                #filtered_df = df_nspl[df_nspl['pcds'] == nearest_postcode]
                #print(filtered_df)
        if nearest_postcode is not None:
            postcode_data.append({
                'postcode': nearest_postcode,
                'count': address_counts_df.iloc[i]['count'],
                'percentage': address_counts_df.iloc[i]['percentage']
            })
            coords_count +=1
            postcode_found = True
        else:
            no_pcode+=1
            # If no postcode or coordinates found, use organizer postcode if available - but not brought through here
            # Flag as missing if no postcode or coordinates found
            postcode_data.append({
                'postcode': 'Missing',
                'count': address_counts_df.iloc[i]['count'],
                'percentage': address_counts_df.iloc[i]['percentage']
            })

postcode_df = pd.DataFrame(postcode_data)

print(f"Number of rows in postcode_df: {len(postcode_df)}")
print(f"Number of rows with no postcode: {len(address_counts_df)-len(postcode_df)}")

print(f"Number of rows with no postcode: {no_pcode}")
print(f"Number of rows with postcodes from coords: {coords_count}")
print(f"Number of rows with own poctcode {pcodes}")

print(no_pcode+coords_count+pcodes)

# Save the postcode DataFrame to a pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'postcode_counts.pickle', 'wb') as file_out:
    pickle.dump(postcode_df, file_out)
