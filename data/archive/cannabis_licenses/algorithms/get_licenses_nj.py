"""
Cannabis Licenses | Get New Jersey Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 9/29/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect New Jersey cannabis license data.

Data Source:

    - New Jersey Cannabis Regulatory Commission
    URL: <https://data.nj.gov/stories/s/ggm4-mprw>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Optional

# External imports.
import pandas as pd
import requests


# Specify where your data lives.
DATA_DIR = '../data/nj'

# Specify state-specific constants.
STATE = 'NJ'
NEW_JERSEY = {
    'licensing_authority_id': 'NJCRC',
    'licensing_authority': 'New Jersey Cannabis Regulatory Commission',
    'retailers': {
        'columns': {
            'name': 'business_dba_name',
            'address': 'premise_street_address',
            'town': 'premise_city',
            'state': 'premise_state',
            'zip_code': 'premise_zip_code',
            'county': 'premise_county',
            'phone_number': 'business_phone',
            'type': 'license_type',
        }
    }
}


def get_licenses_nj(
        data_dir: Optional[str] = None,
        **kwargs,
    ):
    """Get New Jersey cannabis license data."""

    # Get retailer data.
    url = 'https://data.nj.gov/resource/nv37-s2zn.json'
    response = requests.get(url)
    data = pd.DataFrame(response.json())

    # Parse the website.
    data['business_website'] = data['website'].apply(lambda x: x['url'])

    # Parse the GIS coordinates.
    data['premise_longitude'] = data['dispensary_location'].apply(
        lambda x: x['coordinates'][0]
    )
    data['premise_latitude'] = data['dispensary_location'].apply(
        lambda x: x['coordinates'][1]
    )

    # Standardize the data.
    drop_cols = ['dispensary_location', 'location', 'website']
    data.drop(columns=drop_cols, inplace=True)
    data.rename(columns=NEW_JERSEY['retailers']['columns'], inplace=True)
    data['business_legal_name'] = data['business_dba_name']
    data['licensing_authority_id'] = NEW_JERSEY['licensing_authority_id']
    data['licensing_authority'] = NEW_JERSEY['licensing_authority']
    data['license_designation'] = 'Adult-Use'
    data['premise_state'] = STATE
    data['license_status_date'] = None
    data['license_term'] = None
    data['issue_date'] = None
    data['expiration_date'] = None
    data['business_owner_name'] = None
    data['business_structure'] = None
    data['business_email'] = None
    data['activity'] = None
    data['parcel_number'] = None
    data['business_image_url'] = None
    data['id'] = None
    data['license_number'] = None
    data['license_status'] = None
    data['data_refreshed_date'] = datetime.now().isoformat()

    # Convert certain columns from upper case title case.
    cols = ['premise_city', 'premise_county', 'premise_street_address']
    for col in cols:
        data[col] = data[col].apply(lambda x: x.title().strip())

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        data.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
    return data


# === Test ===
if __name__ == '__main__':

    # Support command line usage.
    import argparse
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--d', '--data_dir', dest='data_dir', type=str)
        args = arg_parser.parse_args()
    except SystemExit:
        args = {'d': DATA_DIR}

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    data = get_licenses_nj(data_dir)
