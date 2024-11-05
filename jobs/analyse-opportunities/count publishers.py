import pickle
import sys
RELATIVE_FILEPATH_FEEDS = '../volume-1/data-feeds'
RELATIVE_FILEPATH_ANALYSIS = '../volume-1/data-analysis'

def get_unique_publishers(file1, file2):

  publishers = set()

  for filename in [file1, file2]:
    with open(RELATIVE_FILEPATH_FEEDS + '/' + filename, 'rb') as f:
      data = pickle.load(f)
    for item in data['feeds']: 
        publisher = item['publisherName']
        if publisher:
          publishers.add(publisher)

  return list(publishers)

# Replace 'feeds.pickle' and 'feeds_preview.pickle' with actual file paths
publishers = get_unique_publishers('feeds.pickle', 'feeds-preview.pickle')

print(publishers)

# Write the publishers to a CSV file
with open(RELATIVE_FILEPATH_ANALYSIS + 'publishers.csv', 'w') as f:
  for publisher in publishers:
    f.write(publisher + '\n')


#I used gemini to match these as local authority, school, leisure provider, other