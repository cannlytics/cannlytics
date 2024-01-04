"""
Cannabis Licenses | Get Illinois Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 8/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Illinois cannabis license data.

Data Source:

    - Illinois Department of Financial and Professional Regulation
    Licensed Adult Use Cannabis Dispensaries
    URL: <https://www.idfpr.com/LicenseLookup/AdultUseDispensaries.pdf>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Optional

# External imports.
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
import pandas as pd
import pdfplumber
import requests


# Specify state-specific constants.
STATE = 'IL'
ILLINOIS = {
    'licensing_authority_id': 'IDFPR',
    'licensing_authority': 'Illinois Department of Financial and Professional Regulation',
    'retailers': {
        'url': 'https://idfpr.illinois.gov/content/dam/soi/en/web/idfpr/licenselookup/adultusedispensaries.pdf',
        'columns': [
            'business_legal_name',
            'business_dba_name',
            'address',
            'medical',
            'issue_date',
            'license_number', 
        ],
    },
    'labs': {
        'url': 'https://cannabis.illinois.gov/agencies/cannabis-idoa/cannabis-business-licensees/labs.html',
    },
    # TODO: Get cultivators.
    # https://cannabis.illinois.gov/agencies/cannabis-idoa/cannabis-business-licensees/cultivation-centers.html
    # https://cannabis.illinois.gov/agencies/cannabis-idoa/cannabis-business-licensees/craft-growers.html
    
    # TODO: Get processors.
    # https://cannabis.illinois.gov/agencies/cannabis-idoa/cannabis-business-licensees/infusers.html

    # Optional: Get transporters.
    # https://cannabis.illinois.gov/agencies/cannabis-idoa/cannabis-business-licensees/transporters.html
    
}


def get_licenses_il(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
        **kwargs,
    ):
    """Get Illinois cannabis license data."""

    # FIXME: This code needs to be re-done.

    # # Create necessary directories.
    # pdf_dir = f'{data_dir}/pdfs'
    # if not os.path.exists(data_dir): os.makedirs(data_dir)
    # if not os.path.exists(pdf_dir): os.makedirs(pdf_dir)

    # # Download the retailers PDF.
    # retailers_url = ILLINOIS['retailers']['url']
    # filename = f'{pdf_dir}/illinois_retailers.pdf'
    # response = requests.get(retailers_url)
    # with open(filename, 'wb') as f:
    #     f.write(response.content)

    # # Read the retailers PDF.
    # pdf = pdfplumber.open(filename)

    # # Get the table data, excluding the headers and removing empty cells.
    # table_data = []
    # for i, page in enumerate(pdf.pages):
    #     table = page.extract_table()
    #     if i == 0:
    #         table = table[4:]
    #         table = [c for row in table
    #             if (c := [elem for elem in row if elem is not None])]
    #     table_data += table
        
    # Standardize the data.
    # rows = [[x for x in row if x] for row in table_data]
    table_data = []
    licensee_columns = ILLINOIS['retailers']['columns']
    retailers = pd.DataFrame(table_data, columns=licensee_columns)
    retailers = retailers.assign(
        licensing_authority_id=ILLINOIS['licensing_authority_id'],
        licensing_authority=ILLINOIS['licensing_authority'],
        license_designation='Adult-Use',
        premise_state=STATE,
        license_status='Active',
        license_status_date=None,
        license_type='Commercial - Retailer',
        license_term=None,
        expiration_date=None,
        business_legal_name=retailers['business_dba_name'],
        business_owner_name=None,
        business_structure=None,
        business_email=None,
        activity=None,
        parcel_number=None,
        id=retailers['license_number'],
        business_image_url=None,
        business_website=None,
    )

    # Apply `medical` to `license_designation`
    retailers.loc[retailers['medical'] == 'Yes', 'license_designation'] = 'Adult-Use and Medicinal'
    retailers.drop(columns=['medical'], inplace=True)

    # Clean the organization names.
    retailers['business_legal_name'] = retailers['business_legal_name'].str.replace('\n', '', regex=False)
    retailers['business_dba_name'] = retailers['business_dba_name'].str.replace('*', '', regex=False)

    # # Separate address into 'street', 'city', 'state', 'zip_code', 'phone_number'.
    # streets, cities, states, zip_codes, phone_numbers = [], [], [], [], []
    # for _, row in retailers.iterrows():
    #     parts = row.address.split('\n')
    #     parts = [part.strip() for part in parts]
    #     streets.append(parts[0])
    #     phone_numbers.append(parts[-1])
    #     locales = parts[1]
    #     city_locales = locales.split(', ')
    #     state_locales = city_locales[-1].split(' ')
    #     cities.append(city_locales[0])
    #     states.append(state_locales[0])
    #     zip_codes.append(state_locales[-1])
    # retailers['premise_street_address'] = pd.Series(streets)
    # retailers['premise_city'] = pd.Series(cities)
    # retailers['premise_state'] = pd.Series(states)
    # retailers['premise_zip_code'] = pd.Series(zip_codes)
    # retailers['business_phone'] = pd.Series(phone_numbers)

    # # Convert the issue date to ISO format.
    # retailers['issue_date'] = retailers['issue_date'].apply(
    #     lambda x: pd.to_datetime(x).isoformat()
    # )

    # # Get the refreshed date.
    # date = pdf.metadata['ModDate'].replace('D:', '')
    # date = date[:4] + '-' + date[4:6] + '-' + date[6:8] + 'T' + date[8:10] + \
    #     ':' + date[10:12] + ':' + date[12:].replace("'", ':').rstrip(':')
    # retailers['data_refreshed_date'] = date

    # # Geocode licenses to get `premise_latitude` and `premise_longitude`.
    # config = dotenv_values(env_file)
    # google_maps_api_key = config['GOOGLE_MAPS_API_KEY']
    # retailers['address'] = retailers['address'].str.replace('*', '', regex=False)
    # retailers = geocode_addresses(
    #     retailers,
    #     api_key=google_maps_api_key,
    #     address_field='address',
    # )
    # drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    # retailers.drop(columns=drop_cols, inplace=True)
    # gis_cols = {
    #     'county': 'premise_county',
    #     'latitude': 'premise_latitude',
    #     'longitude': 'premise_longitude'
    # }
    # retailers.rename(columns=gis_cols, inplace=True)

    # Save and return the data.
    if data_dir is not None:
        timestamp = datetime.now().isoformat()[:19].replace(':', '-')
        retailers.to_csv(f'{data_dir}/retailers-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{timestamp}.csv', index=False)
        retailers.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)
    return retailers


def get_labs_il(url):
    """Get Illinois lab data from the Illinois website."""
    # Get the webpage.
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the website.")
        return []

    # Find the table.
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    if not table:
        print("Table not found.")
        return []

    # Extract data from each row of the table.
    lab_data = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) != 3:
            continue
        lab_name = cols[0].get_text(strip=True)
        city_state = cols[1].get_text(strip=True).split(", ")
        phone_number = cols[2].get_text(strip=True)
        lab_city = city_state[0] if len(city_state) > 0 else ''
        lab_state = city_state[1] if len(city_state) > 1 else ''
        lab_data.append({
            'lab': lab_name,
            'lab_city': lab_city,
            'lab_state': lab_state,
            'lab_phone_number': phone_number
        })
    labs = pd.DataFrame(lab_data)
    return labs.assign(
        licensing_authority_id=ILLINOIS['licensing_authority_id'],
        licensing_authority=ILLINOIS['licensing_authority'],
        license_designation='Adult-Use',
        premise_state=STATE,
        license_status='Active',
        license_status_date=None,
        license_type='Lab',
        license_term=None,
        expiration_date=None,
        business_legal_name=labs['lab'],
        id=labs.index,
    )


# === Test ===
# [✓] Tested: 2023-12-17 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = '../data/il'
    ENV_FILE = '../../../.env'

    # Support command line usage.
    import argparse
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--d', dest='data_dir', type=str)
        arg_parser.add_argument('--data_dir', dest='data_dir', type=str)
        arg_parser.add_argument('--env', dest='env_file', type=str)
        args = arg_parser.parse_args()
    except SystemExit:
        args = {'d': DATA_DIR, 'env_file': ENV_FILE}

    # Get labs.
    url = 'https://cannabis.illinois.gov/agencies/cannabis-idoa/cannabis-business-licensees/labs.html'
    labs = get_labs_il(url)
    timestamp = datetime.now().strftime('%Y-%m-%d')
    outfile = f'{DATA_DIR}/labs-{STATE.lower()}-{timestamp}.csv'
    labs.to_csv(outfile, index=False)
    print('Labs saved to:', outfile)

    # FIXME:
    # Get licenses, saving them to the specified directory.
    # data_dir = args.get('d', args.get('data_dir'))
    # env_file = args.get('env_file')
    # data = get_licenses_il(data_dir, env_file=env_file)
