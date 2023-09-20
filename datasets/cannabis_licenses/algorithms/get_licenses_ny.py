"""
Cannabis Licenses | Get New York Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/29/2022
Updated: 9/20/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect New York cannabis license data.

Data Source:

    - New York State Office of Cannabis Management
    URL: <https://cannabis.ny.gov/licensing>

"""
# Standard imports:
from datetime import datetime
import json
import os
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import pdfplumber
import requests


# Specify where your data lives.
DATA_DIR = '../data/ny'
ENV_FILE = '../../../.env'

# Specify state-specific constants.
STATE = 'NY'
NEW_YORK = {
    'licensing_authority_id': 'OCM',
    'licensing_authority': 'New York State Office of Cannabis Management',
    'cultivators': {
        'source': 'https://cannabis.ny.gov/adult-use-conditional-cultivator',
        'url': 'https://cannabis.ny.gov/list-aucc-licenses',
    },
    'retailers': {
        'source': 'https://cannabis.ny.gov/conditional-adult-use-retail-dispensary',
        'url': 'https://cannabis.ny.gov/caurd-licenses',
    },
    'processors': {
        'source': 'https://cannabis.ny.gov/adult-use-conditional-processor',
        'url': 'https://cannabis.ny.gov/list-aucp-licenses',
    },
    'labs': {
        'source': 'https://cannabis.ny.gov/cannabis-laboratories',
        'url': 'https://cannabis.ny.gov/cannabis-laboratories',
        'limits': 'https://cannabis.ny.gov/laboratory-testing-limits',
        'qc': 'https://cannabis.ny.gov/laboratory-quality-system-standard',
        'regulations': 'https://cannabis.ny.gov/part-130-cannabis-laboratories-adopted',
        'columns': {
            'Permit # (OCM-CPL-XXXX)': 'license_number',
            'Lab Name': 'business_legal_name',
            'City': 'premise_city',
            'Cannabinoids (including d-10 THC)': 'cannabinoids',
            'Filth/Foreign Material': 'foreign_matter',
            'Metals (Heavy)': 'heavy_metals',
            'Microbiology*': 'microbes',
            'Moisture Content': 'moisture_content',
            'Mycotoxins/Aflatoxins': 'mycotoxins',
            'Pesticides': 'pesticides',
            'Residual Solvents': 'residual_solvents',
            'Terpenes': 'terpenes',
            'Water Activity': 'water_activity',
        }
    },
}


def get_gis_data(df, api_key):
    """Get GIS data."""
    drop_cols = ['state', 'state_name', 'address', 'formatted_address']
    rename_cols = {
        'county': 'premise_county',
        'latitude': 'premise_latitude',
        'longitude': 'premise_longitude'
    }
    df = geocode_addresses(df, api_key=api_key, address_field='address')
    get_city = lambda x: x.split(', ')[1].split(',')[0] if STATE in str(x) else x
    get_street = lambda x: str(x).split(', ')[0]
    df['premise_city'] = df['formatted_address'].apply(get_city)
    df['premise_street_address'] = df['formatted_address'].apply(get_street)
    df.drop(columns=drop_cols, inplace=True)
    return df.rename(columns=rename_cols)


def get_retailers_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get New York cannabis retailers."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')

    # Create a dataset directory.
    dataset_dir = os.path.join(data_dir, '.datasets')
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    # Download the licenses document.
    url = NEW_YORK['retailers']['url']
    response = requests.get(url)
    pdf_file = os.path.join(dataset_dir, 'ny-retailers.pdf')
    with open(pdf_file, 'wb') as f:
        f.write(response.content)

    # Read the PDF.
    doc = pdfplumber.open(pdf_file)
    data = []
    for page in doc.pages:
        table = page.extract_table()
        if table is None:
            continue
        rows = [x for x in table if x[0] and x[0] != 'License Number' and x[0] != 'Application ID']
        data.extend(rows)

    # Close the PDF.
    doc.close()

    # Remove the empty columns.
    data = [[x for x in sublist if x is not None] for sublist in data]

    # Create a dataframe.
    columns = [
        'license_number',
        'business_legal_name',
        'county',
        'business_email',
        'business_phone',
    ]
    df = pd.DataFrame(data, columns=columns)

    # TODO: Determine active vs inactive licenses by * in `business_legal_name`.


    # TODO: Standardize the licenses.
    df['premise_state'] = STATE


    # TODO: Augment GIS data.


    # Define metadata.
    df['data_refreshed_date'] = datetime.now().isoformat()

    # Sort the columns in alphabetical order
    df.sort_index(axis=1, inplace=True)

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        date = datetime.now().isoformat()[:10]
        outfile = f'{data_dir}/retailers-{STATE.lower()}-{date}.csv'
        df.to_csv(outfile, index=False)

    # Return the data.
    return df


def get_cultivators_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get New York cannabis cultivators."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')

    # Create a dataset directory.
    dataset_dir = os.path.join(data_dir, '.datasets')
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    # Download the licenses document.
    url = NEW_YORK['cultivators']['url']
    response = requests.get(url)
    pdf_file = os.path.join(dataset_dir, 'ny-cultivators.pdf')
    with open(pdf_file, 'wb') as f:
        f.write(response.content)

    # Read the PDF.
    doc = pdfplumber.open(pdf_file)
    data = []
    for page in doc.pages:
        table = page.extract_table()
        if table is None:
            continue
        rows = [x for x in table if x[0] and x[0] != 'License Number' and x[0] != 'Application ID']
        data.extend(rows)

    # Close the PDF.
    doc.close()

    # Remove the empty columns.
    data = [[x for x in sublist if x is not None] for sublist in data]

    # Create a dataframe.
    columns = [
        'license_number',
        'business_legal_name',
        'county',
        'business_email',
        'business_phone',
    ]
    df = pd.DataFrame(data, columns=columns)



    # TODO: Standardize the data.



    # TODO: Augment GIS data.



    # # Define metadata.
    # df['data_refreshed_date'] = datetime.now().isoformat()

    # # Sort the columns in alphabetical order
    # df.sort_index(axis=1, inplace=True)

    # # Save the data.
    # if data_dir is not None:
    #     if not os.path.exists(data_dir):
    #         os.makedirs(data_dir)
    #     date = datetime.now().isoformat()[:10]
    #     outfile = f'{data_dir}/cultivators-{STATE.lower()}-{date}.csv'
    #     df.to_csv(outfile, index=False)

    # # Return the data.
    # return df


    raise NotImplementedError


def get_processors_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get New York cannabis processors."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')
    

    # TODO: Get the data from the web / PDF.



    # TODO: Standardize the data.



    # TODO: Augment GIS data.

    

    # # Define metadata.
    # df['data_refreshed_date'] = datetime.now().isoformat()

    # # Sort the columns in alphabetical order
    # df.sort_index(axis=1, inplace=True)

    # # Save the data.
    # if data_dir is not None:
    #     if not os.path.exists(data_dir):
    #         os.makedirs(data_dir)
    #     date = datetime.now().isoformat()[:10]
    #     outfile = f'{data_dir}/processors-{STATE.lower()}-{date}.csv'
    #     df.to_csv(outfile, index=False)

    # # Return the data.
    # return df

    raise NotImplementedError


def get_labs_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ) -> pd.DataFrame:
    """Get New York cannabis labs."""

    # Load the environment variables.
    config = dotenv_values(env_file)
    google_maps_api_key = config.get('GOOGLE_MAPS_API_KEY')
    if google_maps_api_key is None:
        print('Proceeding without `GOOGLE_MAPS_API_KEY`.')

    # Get the lab list from the web.
    url = NEW_YORK['labs']['source']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table.
    table = soup.find('table')

    # Get the table headers.
    data = []
    header_row = table.find('thead').find('tr')
    headers = [header.get_text(strip=True) for header in header_row.find_all('th')]
    data.append(headers)

    # Get the table rows.
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [col.get_text(strip=True) for col in cols]
        data.append(cols)

    # Format a DataFrame.
    df = pd.DataFrame(data[1:], columns=data[0])

    # Rename columns.
    df.rename(columns=NEW_YORK['labs']['columns'], inplace=True)

    # Identify analyses for each lab.
    analyses = list(df.columns[3:])
    combine_analyses = lambda x: json.dumps([n for n in analyses if x[n] == 'x'])
    df['analyses'] = df.apply(combine_analyses, axis=1)
    df.drop(columns=analyses, inplace=True)

    # Augment GIS data.
    if google_maps_api_key:
        df['address'] = df['business_legal_name'] + ', ' + df['premise_city'] + ', ' + STATE
        df = get_gis_data(df, api_key=google_maps_api_key)

    # Standardize the data.
    df = df.assign(
        id=df['license_number'].astype(str),
        business_dba_name=df['business_legal_name'],
        licensing_authority_id=NEW_YORK['licensing_authority_id'],
        licensing_authority=NEW_YORK['licensing_authority'],
        premise_state=STATE,
        license_status_date=None,
        license_type='lab',
        license_term=None,
        issue_date=None,
        expiration_date=None,
        business_structure=None,
        activity=None,
        parcel_number=None,
        business_image_url=None,
    )

    # Define metadata.
    df['data_refreshed_date'] = datetime.now().isoformat()

    # Sort the columns in alphabetical order
    df.sort_index(axis=1, inplace=True)

    # Save the data.
    if data_dir is not None:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        date = datetime.now().isoformat()[:10]
        outfile = f'{data_dir}/labs-{STATE.lower()}-{date}.csv'
        df.to_csv(outfile, index=False)

    # Return the data.
    return df


def get_medical_ny():
    """Get New York medical cannabis dispensaries."""
    raise NotImplementedError


def get_licenses_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get New York cannabis license data."""

    # Get the data for the various licenses.
    retailers = get_retailers_ny(data_dir, env_file)
    labs = get_labs_ny(data_dir, env_file)
    # FIXME: The following are not yet implemented.
    # cultivators = get_cultivators_ny(data_dir, env_file)
    # processors = get_processors_ny(data_dir, env_file)
    # Future work:
    # medical = get_medical_ny(data_dir, env_file)

    # Compile the data.
    # sets = [retailers, cultivators, processors, labs]
    sets = [retailers, labs]
    licenses = pd.concat(sets, ignore_index=True)
    licenses['premise_state'] = STATE

    # Save all of the licenses.
    if data_dir is not None:
        date = datetime.now().isoformat()[:10]
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-{date}.csv', index=False)
        licenses.to_csv(f'{data_dir}/licenses-{STATE.lower()}-latest.csv', index=False)

    # Return the licenses.
    return licenses


# === Test ===
# [✓] Tested: 2023-08-13 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

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

    # Get licenses, saving them to the specified directory.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')
    data = get_licenses_ny(data_dir, env_file=env_file)
