from read_pickle_functions import *
from create_summary_functions import *
from os import getenv

RELATIVE_FILEPATH_ANALYSIS = getenv('RELATIVE_FILEPATH_ANALYSIS', '../volume-1/data-analysis')
    
VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):

    VERBOSE = True

    try:
        #The basis of processing is a list of the filenames in data opportunities folder
        filenames_with_infostamp, filenames_without_infostamp = get_filenames()
        print(f"Number of individual feeds: {len(filenames_without_infostamp)}")
        #Files are then paired where appropriate
        pairs_filenames_without_infostamp = get_pairs_filenames_without_infostamp(filenames_without_infostamp)
        pairs_filenames_with_infostamp = get_pairs_filenames_with_infostamp(pairs_filenames_without_infostamp, filenames_with_infostamp)

        # Extract the first filenames from each sublist
        first_filenames = [pair[0] for pair in pairs_filenames_without_infostamp]
        # Create a DataFrame from the filenames
        df = pd.DataFrame({'filename': first_filenames})
        # Export the DataFrame to a CSV file
        df.to_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'exported_filenames_in.csv', index=False) 

        print(f"Number of feeds after pairing: {len(pairs_filenames_without_infostamp)}")
        
        #print(*pairs_filenames_without_infostamp[3:4], sep="\n") 
        #print(*pairs_filenames_without_infostamp[-8:-7], sep="\n") 
        #The next stage merges feeds where appropriate, then creates summary information from the feed
        #analyse_opportunities(pairs_filenames_with_infostamp[3:4], verbose=VERBOSE)
        #analyse_opportunities(pairs_filenames_with_infostamp[-8:-7], verbose=VERBOSE)
        analyse_opportunities(pairs_filenames_with_infostamp, verbose=VERBOSE)
        #Finally, an overall summary file is created for rapid visualisation in the dashboard
        create_summary()
        
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    filename = 'analysis-data.pickle'

    # Load the pickle file
    with open(RELATIVE_FILEPATH_ANALYSIS + '/' + filename, 'rb') as file_in:
        df_analysis_data = pickle.load(file_in)

    # List the columns
    print("Available columns:", df_analysis_data.columns.tolist())

    print(f"Number of rows in summary output: {len(df_analysis_data)}")
    
   # Export filenames to CSV
    df_analysis_data[['file_name', 'file_name_partner']].to_csv(RELATIVE_FILEPATH_ANALYSIS + '/' + 'exported_filenames_out.csv', index=False)

    print('Finished')