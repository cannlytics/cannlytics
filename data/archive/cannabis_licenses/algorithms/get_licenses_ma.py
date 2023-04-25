"""
Cannabis Licenses | Get Massachusetts Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 10/7/2022
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
    'licenses': {
        'columns': {
            'license_number': 'license_number',
            'business_name': 'business_legal_name',
            'establishment_address_1': 'premise_street_address',
            'establishment_address_2': 'premise_street_address_2',
            'establishment_city': 'premise_city',
            'establishment_zipcode': 'premise_zip_code',
            'county': 'premise_county',
            'license_type': 'license_type',
            'application_status': 'license_status',
            'lic_status': 'license_term',
            'approved_license_type': 'license_designation',
            'commence_operations_date': 'license_status_date',
            'massachusetts_business': 'id',
            'dba_name': 'business_dba_name',
            'establishment_activities': 'activity',
            'cccupdatedate': 'data_refreshed_date',
            'establishment_state': 'premise_state',
            'latitude': 'premise_latitude',
            'longitude': 'premise_longitude',
        },
        'drop': [
            'square_footage_establishment',
            'cooperative_total_canopy',
            'cooperative_cultivation_environment',
            'establishment_cultivation_environment',
            'abutters_count',
            'is_abutters_notified',
            'business_zipcode',
            'dph_rmd_number',
            'geocoded_county',
            'geocoded_address',
            'name_of_rmd',
            'priority_applicant_type',
            'rmd_priority_certification',
            'dba_registration_city',
            'county_lat',
            'county_long',
        ]
    },
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
    constants = MASSACHUSETTS['licenses']
    licenses.drop(columns=constants['drop'], inplace=True)
    licenses.rename(columns=constants['columns'], inplace=True)
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

    # Append `premise_street_address_2` to `premise_street_address`.
    cols = ['premise_street_address', 'premise_street_address_2']
    licenses['premise_street_address'] = licenses[cols].apply(
        lambda x : '{} {}'.format(x[0].strip(), x[1]).replace('nan', '').strip().replace('  ', ' '),
        axis=1,
    )
    licenses.drop(columns=['premise_street_address_2'], inplace=True)

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
