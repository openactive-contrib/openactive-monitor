import pandas as pd
import pickle
import sys
import os
import time
import json
import warnings
import matplotlib.pyplot as plt

pd.set_option('display.max_colwidth', 150) 
# Clear the terminal
os.system('cls' if os.name == 'nt' else 'clear')

RELATIVE_FILEPATH_ANALYSIS = os.getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
LAUA_FILENAME = 'laua_counts.pickle'
POP_FILENAME = 'pop2019.csv'

# Load the pickle file
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + LAUA_FILENAME, 'rb') as file_in:
    las = pickle.load(file_in)
    # Rename 'postcode' to 'pcds' in pcodes DataFrame
print(las)
print(f"LAUA in OA data:{len(las)}")

#Check for dups
print(f"Number of duplicate laua: {las['laua'].duplicated().sum()}")

# Show rows where 'count' is missing or 0
missing_or_zero_count = las[(las['count'].isnull()) | (las['count'] == 0)]
print(missing_or_zero_count)

pop = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + POP_FILENAME)
print(pop)
print(f"LAUA in Population data:{len(pop)}")
pop.rename(columns={'Code': 'laua'}, inplace=True)

# Merge the DataFrames on the 'laua' column
merged_df = pd.merge(las, pop, on='laua', how='left')

# Print the merged DataFrame
print(merged_df)

# Filter for rows where 'Name' is null or blank
filtered_df = merged_df[merged_df['Name'].isnull() | (merged_df['Name'] == '')]

# Print the filtered DataFrame
print(filtered_df)

# Drop unmatched rows
merged_df = merged_df[~merged_df['all_ages'].isnull()]

merged_df['all_ages'] = merged_df['all_ages'].str.replace(',', '').astype(int)

# Calculate 'opp' by dividing 'count' by 'All Ages'
merged_df['opp'] = merged_df['count'] / merged_df['all_ages']

# Print the updated DataFrame
output = merged_df[['Name','count','all_ages','opp']]
print(output)

# Rank 'merged_df' by 'opp' in descending order and select the top 25
top_df = merged_df.sort_values(by='opp', ascending=False)

# Print the top 25 DataFrame
print(top_df)


LDP_FILENAME = 'LDPs.csv'
ldp = pd.read_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + LDP_FILENAME)

print(f"LAUA in LDP data:{len(ldp)}")
ldp.rename(columns={'LAUA': 'laua'}, inplace=True)
ldp['LDP'] = True
print(ldp)

from scipy import stats

# Merge ldp with merged_df
merged_df = merged_df.merge(ldp[['laua', 'LDP']], on='laua', how='left')

merged_df['LDP'] = merged_df['LDP'].fillna(False)

# Separate data into two groups based on 'LDP'
ldp_true = merged_df[merged_df['LDP'] == True]['opp']
ldp_false = merged_df[merged_df['LDP'] == False]['opp']

# Perform a t-test to check for significant difference
t_statistic, p_value = stats.ttest_ind(ldp_true, ldp_false, equal_var=False)  # Use Welch's t-test if variances are unequal

# Print the results
print(f"T-statistic: {t_statistic:.2f}")
print(f"P-value: {p_value:.3f}")

# Interpret the results
alpha = 0.05  # Set your significance level
if p_value < alpha:
    print("There is a statistically significant difference in 'opp' between LDP True and LDP False groups.")
else:
    print("There is no statistically significant difference in 'opp' between LDP True and LDP False groups.")

# Calculate average 'opp' for LDP True and LDP False groups
average_opp = merged_df.groupby('LDP')['opp'].mean()

print(average_opp)

sys.exit()





#If dups, sum the counts
if pcodes['pcds'].duplicated().sum() > 0:
    pcodes = pcodes.groupby('pcds')['count'].sum().reset_index()

# Print one full row
#print(pcodes.iloc[0]) 

# Load the NSPL data
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + NSPL_PICKLE_FILENAME, 'rb') as file_in:
    df_nspl = pickle.load(file_in) 
print(f"Postcodes in NSPL data:{len(df_nspl)}")
print(df_nspl)

#Check for dups
print(f"Number of duplicate postcodes: {df_nspl['pcds'].duplicated().sum()}")

# Separate rows with NaN 'rgn'
merged_df_with_rgn = pd.merge(pcodes, df_nspl, on='pcds', how='left').dropna(subset=['rgn'])
merged_df_without_rgn = pd.merge(pcodes, df_nspl, on='pcds', how='left')[pd.isna(pd.merge(pcodes, df_nspl, on='pcds', how='left')['rgn'])]

print(f"{len(merged_df_without_rgn)} OA postcodes {(len(merged_df_without_rgn) / len(pcodes) * 100):.1f}% did not match to NSPL")

# Sum 'count' for rows where 'rgn' is NaN
sum_count_without_rgn = merged_df_without_rgn['count'].sum()

# Create a new DataFrame for the summed row
new_row = pd.DataFrame({'pcds': ['Missing'], 'count': [sum_count_without_rgn], 'rgn': ['No Data'], 'imd': ['No Data'], 'laua': ['No Data'], 'npark': ['No Data'], 'icb': ['No Data'], 'lat': ['No Data'], 'long': ['No Data']})
print(new_row)
# Concatenate the two DataFrames
merged_df = pd.concat([merged_df_with_rgn, new_row], ignore_index=True)

# Count postcodes in df_nspl that don't match pcodes
unmatched_pcodes = df_nspl[~df_nspl['pcds'].isin(pcodes['pcds'])]['pcds'].nunique()
# Calculate the percentage of unmatched postcodes
total_pcodes_nspl = df_nspl['pcds'].nunique()
percentage_unmatched = (unmatched_pcodes / total_pcodes_nspl) * 100

print(f"Number of postcodes in NSPL not found in OA data: {unmatched_pcodes} ({percentage_unmatched:.2f}%)")
print(f"% of postcodes in NSPL with OA data: {unmatched_pcodes} ({100-percentage_unmatched:.1f}%)")



print(f"Number of records after merge: {len(merged_df)}")
print(merged_df.head())
print(merged_df.info())
# Descriptive statistics
print(merged_df.describe(include='all'))

# Missing value summary
print(merged_df.isnull().sum())
print((merged_df.isnull().sum() / len(merged_df)) * 100)

print(merged_df['rgn'].value_counts())

# --- Exploring Outliers ---

# 1. Descriptive Statistics:
print(merged_df['count'].describe())  # Get basic statistics for the 'count' column

# 2. Box Plot:
plt.figure(figsize=(8, 6))
plt.boxplot(merged_df['count'], vert=False, patch_artist=True, showfliers=True)
plt.xlabel('Opportunity Count')
plt.title('Box Plot of Opportunity Counts')
#plt.show()

# 3. Histograms:
plt.figure(figsize=(8, 6))
plt.hist(merged_df['count'], bins=20)
plt.xlabel('Opportunity Count')
plt.ylabel('Frequency')
plt.title('Histogram of Opportunity Counts')
#plt.show()

# 4. Identifying Extreme Outliers (e.g., using IQR):
Q1 = merged_df['count'].quantile(0.25)
Q3 = merged_df['count'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR
lower_bound = Q1 - 1.5 * IQR

outliers = merged_df[(merged_df['count'] < lower_bound) | (merged_df['count'] > upper_bound)]
print("Outliers:\n", outliers)

# 5. Investigating Outliers:
# - Examine the 'outliers' DataFrame to see if there are any patterns or common characteristics among the outliers.
# - Consider plotting the outliers on a map (if you have geographic coordinates) to see if they are spatially clustered.
# - Investigate the data sources for these outliers to understand if there are any data quality issues or anomalies.

# Function to group, sum counts, and calculate coverage percentage
def group_and_sum_counts(df, column_name):
    # Group by the specified column and sum the 'count' column
    grouped_counts = df.groupby(column_name)['count'].sum().reset_index()

    # Calculate the percentage of each group in df_nspl present in pcodes
    unique_in_nspl = df_nspl[column_name].nunique()
    unique_in_merged = df[column_name].nunique() - 1
    coverage_percentage = (unique_in_merged / unique_in_nspl) * 100

    print(f"Coverage of {column_name}: {coverage_percentage:.2f}%")
    return grouped_counts

# Calculate counts for 'laua', 'npark', and 'icb'
laua_counts = group_and_sum_counts(merged_df.copy(), 'laua')
npark_counts = group_and_sum_counts(merged_df.copy(), 'npark')
icb_counts = group_and_sum_counts(merged_df.copy(), 'icb')

# Save the counts DataFrames to pickle files
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'laua_counts.pickle', 'wb') as file_out:
    pickle.dump(laua_counts, file_out)
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'npark_counts.pickle', 'wb') as file_out:
    pickle.dump(npark_counts, file_out)
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'icb_counts.pickle', 'wb') as file_out:
    pickle.dump(icb_counts, file_out)

# Print the results
print("LAUA Counts:\n", laua_counts)
print("\nNational Park Counts:\n", npark_counts)
print("\nICB Counts:\n", icb_counts)

# Calculate counts and coverage for 'rgn' (regions)
rgn_counts = group_and_sum_counts(merged_df.copy(), 'rgn')

# Print the results for regions
print("\nRegion Counts:\n", rgn_counts)

with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'rgn_counts.pickle', 'wb') as file_out:
    pickle.dump(rgn_counts, file_out)


###########################################################################
#The 2019 IMD ranks each English LSOA from 1 (most deprived) to 32,844 (least deprived).

# Filter for English postcodes (rgn starts with 'E')
english_nspl = df_nspl[df_nspl['rgn'].str.startswith('E', na=False)]

print(f"Number of imds in 2023 nspl: {english_nspl['imd'].nunique()}")
print("Note 2019 imds are 1 to 32,844")
print(max(english_nspl['imd']))
print(min(english_nspl['imd']))

# Merge DataFrames
merged_df = pd.merge(pcodes, english_nspl, on='pcds', how='left')

print(f"Number of LAUAs in 2023 nspl: {english_nspl['laua'].nunique()}")

sys.exit()



#Group and sum to handle multiple postcodes per imd area (lsoa)
imd_counts = group_and_sum_counts(merged_df.copy(), 'imd')

# Print the results for regions
print("\nIMD Counts:\n", imd_counts)
print(len(imd_counts))
print(max(imd_counts['imd']))
print(min(imd_counts['imd']))

# Create a template DataFrame with 32844 records
imd_template = pd.DataFrame({'imd': range(1, 32845)})
# Assuming imd_template['imd'] contains the IMD values
imd_template['imd_decile'] = pd.qcut(imd_template['imd'], 10, labels=False)

# Print the updated DataFrame
print(imd_template)
print(max(imd_template['imd']))
print(min(imd_template['imd']))


# Merge the counts with the IMD template
imd_counts = pd.merge(imd_template, merged_df[['imd', 'count']], on='imd', how='left').fillna(0)
print(f"Total opps in English Regions: {imd_counts['count'].sum()}")
print(f"Number of imds after merge: {imd_counts['imd'].nunique()}")

print(imd_counts)

# Calculate the total number of IMDs in each decile
total_imds_per_decile = imd_counts.groupby('imd_decile')['imd'].nunique().reset_index(name='total_imd_count')

print(total_imds_per_decile)

# Group by decile and sum the counts
imd_decile_counts = imd_counts.groupby('imd_decile')['count'].sum().reset_index()

# Calculate the percentage of counts in each decile
total_count = imd_decile_counts['count'].sum()
imd_decile_counts['percentage'] = (imd_decile_counts['count'] / total_count) * 100

print(imd_decile_counts)

# Save to pickle
with open(RELATIVE_FILEPATH_ANALYSIS + '/' + 'imd_decile_counts_england.pickle', 'wb') as file_out:
    pickle.dump(imd_decile_counts, file_out)

# Group by decile and count IMDs with counts > 0
imd_decile_coverage = imd_counts[imd_counts['count'] > 0].groupby('imd_decile')['imd'].nunique().reset_index(name='imd_count')

# Calculate the total number of IMDs in each decile
total_imds_per_decile = imd_counts.groupby('imd_decile')['imd'].nunique().reset_index(name='total_imd_count')

# Merge the two DataFrames on 'imd_decile'
imd_decile_coverage = pd.merge(imd_decile_coverage, total_imds_per_decile, on='imd_decile')

# Calculate the percentage of IMDs with counts > 0 in each decile
imd_decile_coverage['percentage'] = (imd_decile_coverage['imd_count'] / imd_decile_coverage['total_imd_count']) * 100

# Print the result
print(imd_decile_coverage)

# Save to CSV
imd_decile_coverage.to_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'imd_decile_coverage_england.csv', index=False) 

