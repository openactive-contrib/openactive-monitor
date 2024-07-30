# The following code up to and including get_opportunities_next_url() is a custom version of code from
# the OpenActive Python library v2.0.0. Modifications are:
# - get_catalogue_urls

import json
import requests
from bs4 import BeautifulSoup
from inspect import stack
from itertools import chain
from time import sleep

# --------------------------------------------------------------------------------------------------

SECONDS_WAIT_NEXT_DEFAULT = 0.2

# --------------------------------------------------------------------------------------------------

def set_message(message, message_type=None):
    if (message_type == 'calling'):
        print('CALLING: ' + message)
    elif (message_type == 'warning'):
        print('WARNING: ' + message)
    elif (message_type == 'error'):
        print('ERROR: ' + message)
    else:
        print(message)

# --------------------------------------------------------------------------------------------------

session = requests.Session()

# https://stackoverflow.com/a/65576055
# https://stackoverflow.com/a/72666365

# When making several requests to the same host, requests.get() can result in errors. For more robust
# behaviour, requests.Session().get() is used herein. If there are further issues, then try uncommenting
# the following code for even more supportive behaviour:

# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
# retry_strategy = Retry(
#     total=3,
#     backoff_factor=1
# )
# adapter = HTTPAdapter(max_retries=retry_strategy)
# session.mount('https://', adapter)
# session.mount('http://', adapter)

def try_requests(url, **kwargs):
    headers = kwargs.get('headers', {'User-Agent': 'OpenActive user'})
    num_tries_max = kwargs.get('num_tries_max', 10)
    seconds_wait_retry = kwargs.get('seconds_wait_retry', 1)
    verbose = kwargs.get('verbose', False)

    r = None
    num_tries = 0

    while (True):
        if (num_tries == num_tries_max):
            set_message('Max. tries ({}) reached for: {}'.format(num_tries_max, url), 'warning')
            break
        elif (num_tries > 0):
            set_message('Retrying ({}/{}): {}'.format(num_tries, num_tries_max-1, url), 'warning')
            sleep(seconds_wait_retry)
        try:
            if (verbose):
                set_message(url, 'calling')
            num_tries += 1
            r = session.get(url, headers=headers)
            # https://docs.python-requests.org/en/latest/user/advanced/
            # "Sessions can also be used as context managers [...] This will make sure the session is closed as
            # soon as the with block is exited, even if unhandled exceptions occurred."
            # r = None
            # with requests.Session() as session:
            #     r = session.get(url)
            if (r is None):
                raise Exception(f'{url}: Call failed with no response')
            elif (r.status_code != 200):
                raise Exception(f'{url}: Call failed with status code {r.status_code}')
            break
        except Exception as error:
            set_message(str(error), 'error')
            # Continue otherwise we get kicked out of the while loop. This takes us to the top of the loop:
            continue

    return r, num_tries

# --------------------------------------------------------------------------------------------------

def get_catalogue_urls(**kwargs):
    flat = kwargs.get('flat', False)
    preview = kwargs.get('preview', False)
    verbose = kwargs.get('verbose', False)

    catalogue_urls = {}

    if (not preview):
        collection_url = 'https://openactive.io/data-catalogs/data-catalog-collection.jsonld'
    else:
        collection_url = 'https://openactive.io/data-catalogs/data-catalog-collection-preview.jsonld'

    if (verbose):
        print(stack()[0].function)

    try:
        collection_page, num_tries = try_requests(collection_url, **kwargs)
        if (collection_page is None):
            raise Exception()
        elif (collection_page.status_code != 200):
            raise Exception()
        elif (any([type(i) != str for i in collection_page.json()['hasPart']])):
            raise Exception()
        catalogue_urls[collection_url] = collection_page.json()['hasPart']
    except:
        set_message('Can\'t get collection: {}'.format(collection_url), 'error')

    if (not flat):
        return catalogue_urls
    else:
        return list(chain.from_iterable(catalogue_urls.values()))

# --------------------------------------------------------------------------------------------------

def get_dataset_urls(**kwargs):
    flat = kwargs.get('flat', False)
    seconds_wait_next = kwargs.get('seconds_wait_next', SECONDS_WAIT_NEXT_DEFAULT)
    verbose = kwargs.get('verbose', False)

    dataset_urls = {}

    catalogue_urls = get_catalogue_urls(**{**kwargs, **{'flat': True}})

    if (verbose):
        print(stack()[0].function)

    for catalogue_url_idx,catalogue_url in enumerate(catalogue_urls):
        try:
            if (catalogue_url_idx != 0):
                sleep(seconds_wait_next)
            catalogue_page, num_tries = try_requests(catalogue_url, **kwargs)
            if (catalogue_page is None):
                raise Exception()
            elif (catalogue_page.status_code != 200):
                raise Exception()
            elif (any([type(i) != str for i in catalogue_page.json()['dataset']])):
                raise Exception()
            dataset_urls[catalogue_url] = catalogue_page.json()['dataset']
        except:
            set_message('Can\'t get catalogue: {}'.format(catalogue_url), 'error')

    if (not flat):
        return dataset_urls
    else:
        return list(chain.from_iterable(dataset_urls.values()))

# --------------------------------------------------------------------------------------------------

def get_feeds(**kwargs):
    flat = kwargs.get('flat', False)
    seconds_wait_next = kwargs.get('seconds_wait_next', SECONDS_WAIT_NEXT_DEFAULT)
    verbose = kwargs.get('verbose', False)

    feeds = {}

    dataset_urls = get_dataset_urls(**{**kwargs, **{'flat': True}})

    if (verbose):
        print(stack()[0].function)

    for dataset_url_idx,dataset_url in enumerate(dataset_urls):
        try:
            if (dataset_url_idx != 0):
                sleep(seconds_wait_next)
            dataset_page, num_tries = try_requests(dataset_url, **kwargs)
            if (dataset_page is None):
                raise Exception()
            elif (dataset_page.status_code != 200):
                raise Exception()
            soup = BeautifulSoup(dataset_page.text, 'html.parser')
            for script in soup.head.find_all('script'):
                if (    ('type' in script.attrs.keys())
                    and (script['type'] == 'application/ld+json')
                ):
                    jsonld = json.loads(script.string)
                    if ('distribution' in jsonld.keys()):
                        for feed_in in jsonld['distribution']:
                            feed_out = {}

                            try:
                                feed_out['name'] = jsonld['name']
                            except:
                                feed_out['name'] = ''
                            try:
                                feed_out['type'] = feed_in['name']
                            except:
                                feed_out['type'] = ''
                            try:
                                feed_out['url'] = feed_in['contentUrl']
                            except:
                                feed_out['url'] = ''
                            try:
                                feed_out['datasetUrl'] = dataset_url
                            except:
                                feed_out['datasetUrl'] = ''
                            try:
                                feed_out['discussionUrl'] = jsonld['discussionUrl']
                            except:
                                feed_out['discussionUrl'] = ''
                            try:
                                feed_out['licenseUrl'] = jsonld['license']
                            except:
                                feed_out['licenseUrl'] = ''
                            try:
                                feed_out['publisherName'] = jsonld['publisher']['name']
                            except:
                                feed_out['publisherName'] = ''

                            if (dataset_url not in feeds.keys()):
                                feeds[dataset_url] = []
                            feeds[dataset_url].append(feed_out)
        except:
            set_message('Can\'t get dataset: {}'.format(dataset_url), 'error')

    if (not flat):
        return feeds
    else:
        return list(chain.from_iterable(feeds.values()))

# --------------------------------------------------------------------------------------------------

# The above code should be incorporated into the OpenActive Python library. The main code of interest
# for the Google Cloud job being developed begins here.

import pickle
import sys
from datetime import datetime
from google.cloud import pubsub_v1
# from openactive import get_feeds
from os import getenv

# --------------------------------------------------------------------------------------------------

# These folders must have been made via the Google Cloud browser console under Cloud Storage for this
# project, and the volume must have been mounted via the terminal at the mount-path '/volume-1'. With
# this job called 'get-feeds', this was done as follows (note that the volume and its mount-path
# were given the same name, which didn't have to be so):
#   $ gcloud beta run jobs update get-feeds \
#   --add-volume name=volume-1,type=cloud-storage,bucket=openactive-monitor_cloudbuild \
#   --add-volume-mount volume=volume-1,mount-path=/volume-1
RELATIVE_FILEPATH_FEEDS = getenv('RELATIVE_FILEPATH_FEEDS', '../volume-1/data-feeds')

FILENAME_FEEDS = getenv('FILENAME_FEEDS', 'feeds.pickle') # Located in RELATIVE_FILEPATH_FEEDS
FILENAME_FEEDS_PREVIEW = getenv('FILENAME_FEEDS_PREVIEW', 'feeds-preview.pickle') # Located in RELATIVE_FILEPATH_FEEDS

VERBOSE = getenv('VERBOSE', 'False').title()
VERBOSE = True if (VERBOSE == 'True') else False

HEADERS = {
    'timeout': '10',
    'User-Agent': 'OpenActive admin',
    # Alternative 'User-Agent' based on laptop browser settings. Still doesn't seem to help some GCloud 403 errors though:
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'From': 'hello@openactive.io',
    'Referer': 'https://www.openactive.io',
}

print('Environment variables:')
print('RELATIVE_FILEPATH_FEEDS:', RELATIVE_FILEPATH_FEEDS)
print('FILENAME_FEEDS:', FILENAME_FEEDS)
print('FILENAME_FEEDS_PREVIEW:', FILENAME_FEEDS_PREVIEW)
print('VERBOSE:', VERBOSE)

# --------------------------------------------------------------------------------------------------

def run_get_feeds(**kwargs):
    preview = kwargs.get('preview', False)

    t1 = datetime.now()
    feeds = get_feeds(**{**kwargs, **{'flat': True}})
    t2 = datetime.now()

    with open(RELATIVE_FILEPATH_FEEDS + '/' + (FILENAME_FEEDS_PREVIEW if preview else FILENAME_FEEDS), 'wb') as file_out:
        pickle.dump(
            {
                'time_start': str(t1),
                'time_finish': str(t2),
                'time_taken': str(t2 - t1),
                'num_feeds': len(feeds),
                'feeds': feeds,
            },
            file_out
        )

# --------------------------------------------------------------------------------------------------

def run_job(name_job):
    publisher = pubsub_v1.PublisherClient()
    future = publisher.publish(
        publisher.topic_path('openactive-monitor', 'run-job'),
        name_job.encode('utf-8')
    )
    future.result()

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    # Temporarily disabled as GCloud is not getting all feeds for some reason, so just using feeds from
    # local run instead:
    # for preview in [False, True]:
    #     try:
    #         run_get_feeds(
    #             headers = HEADERS,
    #             preview = preview,
    #             verbose = VERBOSE,
    #         )
    #     except Exception as error:
    #         print('ERROR:', error)
    #         sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    try:
        run_job('get-opportunities')
    except Exception as error:
        print('ERROR:', error)
        sys.exit(1)

    # --------------------------------------------------------------------------------------------------

    print('Finished')