"""
Cannabis Licenses | Get Massachusetts Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 4/23/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Massachusetts cannabis license data.

Data Source:

    - Massachusetts Cannabis Control Commission Data Catalog
    URL: <https://masscannabiscontrol.com/open-data/data-catalog/>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Optional

# External imports.
from cannlytics.data import OpenData


# Specify where your data lives.
DATA_DIR = '../data/ma'

# Specify state-specific constants.
STATE = 'MA'
MASSACHUSETTS = {
    'licensing_authority_id': 'MACCC',
    'licensing_authority': 'Massachusetts Cannabis Control Commission',
}


def get_licenses_ma(
        data_dir: Optional[str] = None,
        **kwargs,
    ):
    """Get Massachusetts cannabis license data."""

    # Get the licenses data.
    ccc = OpenData()
    licenses = ccc.get_licensees('approved')

    # Standardize the licenses data.
    licenses = licenses.assign(
        licensing_authority_id=MASSACHUSETTS['licensing_authority_id'],
        licensing_authority=MASSACHUSETTS['licensing_authority'],
        business_structure=None,
        business_email=None,
        business_owner_name=None,
        parcel_number=None,
        issue_date=None,
        expiration_date=None,
        business_image_url=None,
        business_website=None,
        business_phone=None,
    )

    # Optional: Look-up business websites for each license.

    # Save and return the data.
    if data_dir is not None:
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers = licenses.loc[licenses['license_type'].str.contains('Retailer')]
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
    return licenses


# === Test ===
if __name__ == '__main__':

    # Support command line usage.
    import argparse
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--d', dest='data_dir', type=str)
        arg_parser.add_argument('--data_dir', dest='data_dir', type=str)
        args = arg_parser.parse_args()
    except SystemExit:
        args = {'d': DATA_DIR}

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    data = get_licenses_ma(data_dir)
