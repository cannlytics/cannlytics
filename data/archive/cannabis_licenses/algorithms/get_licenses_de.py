"""
Cannabis Licenses | Get Delaware Licenses
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 4/25/2023
Updated: 4/25/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect Delaware cannabis license data.

Data Source:

    - Delaware Health Care Commission
    URL: <https://dhss.delaware.gov/dhss/dph/hsp/medmarcc.html>

"""
# Standard imports:
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
import requests


# Specify where your data lives.
DATA_DIR = '../data/md'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'DE'
DELAWARE = {
    'licensing_authority_id': 'DHCC',
    'licensing_authority': 'Delaware Health Care Commission',
    'licenses_url': 'https://dhss.delaware.gov/dhss/dph/hsp/medmarcc.html',
}


def get_licenses_de(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get Delaware cannabis license data."""
    
    # Get the license webpage.
    url = DELAWARE['licenses_url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the licenses table.
    table =  soup.find('table')

    # Extract the license names.
    names = [x.text for x in table.find_all('strong') + table.find_all('b')]
    names = [x for x in names if x != 'Additional Links']

    # Extract the license websites.
    sites = [x.text for x in table.find_all('a') if x]
    sites = [x for x in sites if x.startswith('http')]

    # FIXME: Get address and phone number.

    # DEV:
    # data = []
    # columns = DELAWARE['retailers']['columns']
    # table =  soup.find('table')
    # tds = table.find_all('td')
    # sites = []
    # rows = [x.text.replace('\t', '').replace('\r', '').split('\n') for x in tds]
    # rows = [x for x in rows if x]
    # for i, row in enumerate(rows):
    #     # td = tds[i]
    #     # names = [x.text for x in td.find_all('strong') + td.find_all('b')]
    #     for n, cell in enumerate(row):
    #         if not cell:
    #             continue
    #         elif cell == 'Additional Links':
    #             break
    #         elif cell.startswith('http'):
    #             print('BUSINESS EMAIL:', cell)
    #             sites.append(cell)
    #         else:
    #             
    #             pass               
        # print(row.text.split('\n'))
        # cells = row.find_all('td')
        # obs = {}
        # for i, cell in enumerate(cells):
        #     print(cell.text)
        #     column = columns[i]
        #     obs[column] = cell.text
        # data.append(obs)


# === Test ===
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
    data = get_licenses_de(data_dir, env_file=env_file)
