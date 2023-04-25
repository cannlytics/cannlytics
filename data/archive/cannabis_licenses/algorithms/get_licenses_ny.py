"""
Cannabis Licenses | Get New York Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/29/2022
Updated: 11/29/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect New York cannabis license data.

Data Source:

    - New York Medical Dispensaries
    URL: <https://cannabis.ny.gov/dispensing-facilities>

"""
# Standard imports:
from typing import Optional


# Specify where your data lives.
DATA_DIR = '../data/ny'
ENV_FILE = '../../../../.env'

# Specify state-specific constants.
STATE = 'NY'
NEW_YORK = {
    'licensing_authority_id': '',
    'licensing_authority': '',
    'licenses_url': '',
}


def get_licenses_ny(
        data_dir: Optional[str] = None,
        env_file: Optional[str] = '.env',
    ):
    """Get New York cannabis license data."""
    raise NotImplementedError


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
    data = get_licenses_ny(data_dir, env_file=env_file)
