"""
Cannabis Licenses | Get All Licenses
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 4/24/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect all cannabis license data from states with permitted adult-use:

        ✓ Alaska (Selenium)
        x Arizona (Selenium)
        ✓ California
        ✓ Colorado
        ✓ Connecticut
        - Delaware
        ✓ Illinois
        ✓ Maine
        - Maryland (FIXME)
        ✓ Massachusetts
        ✓ Michigan (Selenium)
        - Missouri
        ✓ Montana
        ✓ Nevada
        ✓ New Jersey
        - New York
        x New Mexico (Selenium) (FIXME)
        ✓ Oregon
        ✓ Rhode Island
        ✓ Vermont
        ✓ Washington
"""
# Standard imports.
from datetime import datetime
import importlib
import os

# External imports.
import pandas as pd


# Specify state-specific algorithms.
ALGORITHMS = {
    'ak': 'get_licenses_ak',
    'az': 'get_licenses_az',
    'ca': 'get_licenses_ca',
    'co': 'get_licenses_co',
    'ct': 'get_licenses_ct',
    'il': 'get_licenses_il',
    'ma': 'get_licenses_ma',
    'md': 'get_licenses_md',
    'me': 'get_licenses_me',
    'mi': 'get_licenses_mi',
    'mt': 'get_licenses_mt',
    'nj': 'get_licenses_nj',
    'nm': 'get_licenses_nm',
    'nv': 'get_licenses_nv',
    'or': 'get_licenses_or',
    'ri': 'get_licenses_ri',
    'vt': 'get_licenses_vt',
    'wa': 'get_licenses_wa',
    # TODO:
    # 'ny': 'get_licenses_ny',
    # 'mo': 'get_licenses_mo',
    # 'de': 'get_licenses_de',
    # Future:
    # 'va': 'get_licenses_va',
    # Medical:
    # 'ok': 'get_licenses_ok',
    # 'fl': 'get_licenses_fl',
    # 'la': 'get_licenses_la',
    # 'ms': 'get_licenses_ms',
    # 'al': 'get_licenses_al',
    # 'oh': 'get_licenses_oh',
    # 'pa': 'get_licenses_pa',
    # 'ar': 'get_licenses_ar',
    # 'ky': 'get_licenses_ky',
    # 'ut': 'get_licenses_ut',
    # 'tx': 'get_licenses_tx',
    # 'nd': 'get_licenses_nd',
    # 'sd': 'get_licenses_sd',
    # 'mn': 'get_licenses_mn',
    # 'nh': 'get_licenses_nh',
    # 'wv': 'get_licenses_wv',
}
DATA_DIR = '../data'


def main(data_dir, env_file):
    """Collect all cannabis license data from states with permitted adult-use,
    dynamically importing modules and finding the entry point for each of the
    `ALGORITHMS`."""
    licenses = pd.DataFrame()
    for state, algorithm in ALGORITHMS.items():
        module = importlib.import_module(f'{algorithm}')
        entry_point = getattr(module, algorithm)
        try:
            print(f'Getting license data for {state.upper()}.')
            data = entry_point(data_dir, env_file=env_file)
            if not os.path.exists(f'{DATA_DIR}/{state}'):
                os.makedirs(f'{DATA_DIR}/{state}')
            timestamp = datetime.now().isoformat()[:19].replace(':', '-')
            data.to_csv(f'{DATA_DIR}/{state}/licenses-{state}-{timestamp}.csv', index=False)
            print(f'Curated {state.upper()} licenses.')
            licenses = pd.concat([licenses, data])
        except:
            print(f'Failed to aggregate {state.upper()} licenses.')
    
    # Save all of the retailers.
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    licenses.to_csv(f'{DATA_DIR}/all/licenses-{timestamp}.csv', index=False)
    return licenses


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
        args = {'d': '../data/all', 'env_file': '../.env'}
    
    # Get arguments.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')

    # Get licenses for each state.
    all_licenses = main(data_dir, env_file)
