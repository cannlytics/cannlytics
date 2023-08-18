"""
Cannabis Licenses | Get California Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/16/2022
Updated: 8/17/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect California cannabis license data.

Data Source:

    - California Department of Cannabis Control Cannabis Unified License Search
    URL: <https://search.cannabis.ca.gov/>

"""
# Standard imports.
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports.
from cannlytics.utils import camel_to_snake
from cannlytics.utils.constants import DEFAULT_HEADERS
import pandas as pd
import requests


# Specify where your data lives.
DATA_DIR = '../data/ca'


def get_licenses_ca(
        data_dir: Optional[str] = None,
        page_size: Optional[int] = 50,
        pause: Optional[float] = 0.2,
        starting_page: Optional[int] = 1,
        ending_page: Optional[int] = None,
        verbose: Optional[bool] = False,
        search: Optional[str] = '',
        **kwargs,
    ):
    """Get California cannabis license data."""

    # Define the license data API.
    base = 'https://as-cdt-pub-vip-cannabis-ww-p-002.azurewebsites.net'
    endpoint = '/licenses/filteredSearch'
    query = f'{base}{endpoint}'
    params = {'pageSize': page_size, 'searchQuery': search}

    # Iterate over all of the pages to get all of the data.
    page = int(starting_page)
    licenses = []
    iterate = True
    while(iterate):
        params['pageNumber'] = page
        response = requests.get(query, headers=DEFAULT_HEADERS, params=params)
        body = response.json()
        data = body['data']
        licenses.extend(data)
        if not body['metadata']['hasNext']:
            iterate = False
        if verbose:
            print('Recorded %i/%i pages.' % (page, body['metadata']['totalPages']))
        if ending_page is not None:
            if page == ending_page:
                iterate = False
        page += 1
        sleep(pause)

    # Standardize the licensee data.
    license_data = pd.DataFrame(licenses)
    columns = list(license_data.columns)
    columns = [camel_to_snake(x) for x in columns]
    license_data.columns = columns

    # TODO: Lookup business website and image.
    license_data['business_image_url'] = None
    license_data['business_website'] = None

    # Restrict to only active licenses.
    license_data = license_data.loc[license_data['license_status'] == 'Active']

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        date = datetime.now().strftime('%Y-%m-%d')
        license_data.to_csv(f'{data_dir}/licenses-ca-{date}.csv', index=False)
        license_data.to_csv(f'{data_dir}/licenses-ca-latest.csv', index=False)
    return license_data


# === Test ===
# [✓] Tested: 2023-08-13 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Support command line usage.
    import argparse
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--d', dest='data_dir', type=str)
        arg_parser.add_argument('--data_dir', dest='data_dir', type=str)
        # Future work: Support the rest of the arguments from the CL.
        args = arg_parser.parse_args()
    except SystemExit:
        args = {'d': DATA_DIR}

    # Get California licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    get_licenses_ca(data_dir)
