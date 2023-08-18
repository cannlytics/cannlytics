"""
Cannabis Licenses | Get All Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 8/17/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Collect all cannabis license data from states with permitted adult-use:

        ✓ Alaska (Requires Selenium)
        ✓ Arizona (Requires Selenium)
        ✓ California
        ✓ Colorado
        ✓ Connecticut
        ✓ Delaware
        ✓ Illinois (FIXME)
        ✓ Maine
        ✓ Maryland
        ✓ Massachusetts
        ✓ Michigan (Requires Selenium)
        ✓ Minnesota
        ✓ Missouri
        ✓ Montana
        ✓ Nevada
        ✓ New Jersey
        ✓ New York
        ✓ New Mexico (Requires Selenium) (FIXME)
        ✓ Oregon (FIXME)
        ✓ Rhode Island (FIXME)
        ✓ Vermont (FIXME)
        ✓ Washington (FIXME)
"""
# Standard imports.
from datetime import datetime
import importlib
import os
import sys

# External imports.
from cannlytics import Cannlytics
import pandas as pd


# Specify state-specific algorithms.
ALGORITHMS = {
    # 'ak': 'get_licenses_ak',
    # 'az': 'get_licenses_az',
    # 'ca': 'get_licenses_ca',
    # 'co': 'get_licenses_co',
    # 'ct': 'get_licenses_ct',
    # 'de': 'get_licenses_de',
    # 'il': 'get_licenses_il',
    # 'ma': 'get_licenses_ma',
    # 'md': 'get_licenses_md',
    # 'me': 'get_licenses_me',
    # 'mi': 'get_licenses_mi',
    # 'mo': 'get_licenses_mo',
    # 'mt': 'get_licenses_mt',
    # 'nj': 'get_licenses_nj',
    # 'nm': 'get_licenses_nm',
    'nv': 'get_licenses_nv',
    'ny': 'get_licenses_ny',
    'or': 'get_licenses_or',
    'ri': 'get_licenses_ri',
    'vt': 'get_licenses_vt',
    'wa': 'get_licenses_wa',
    # Future:
    # 'va': 'get_licenses_va',
    # 'mn': 'get_licenses_mn',
    # Medical:
    # 'al': 'get_licenses_al',
    # 'ar': 'get_licenses_ar',
    # 'fl': 'get_licenses_fl',
    # 'ky': 'get_licenses_ky',
    # 'la': 'get_licenses_la',
    # 'ms': 'get_licenses_ms',
    # 'nd': 'get_licenses_nd',
    # 'nh': 'get_licenses_nh',
    # 'oh': 'get_licenses_oh',
    # 'ok': 'get_licenses_ok',
    # 'pa': 'get_licenses_pa',
    # 'sd': 'get_licenses_sd',
    # 'tx': 'get_licenses_tx',
    # 'ut': 'get_licenses_ut',
    # 'wv': 'get_licenses_wv'
}


def main(data_dir, env_file):
    """Collect all cannabis license data from states with permitted adult-use,
    dynamically importing modules and finding the entry point for each of the
    `ALGORITHMS`."""

    # Initialize.
    licenses = pd.DataFrame()
    date = datetime.now().isoformat()[:10]
    manager = Cannlytics()

    # Add the state_modules directory to sys.path for dynamic imports
    sys.path.append(os.path.join(os.getcwd()))

    # Collect licenses for each state.
    for state, algorithm in ALGORITHMS.items():

        # Import the module and get the entry point.
        module = importlib.import_module(f'{algorithm}')
        entry_point = getattr(module, algorithm)

        # Collect licenses for the state.
        # try:
        manager.create_log(f'Getting license data for {state.upper()}.')
        data = entry_point(data_dir, env_file=env_file)
        if not os.path.exists(f'{data_dir}/{state}'):
            os.makedirs(f'{data_dir}/{state}')
        data.to_csv(f'{data_dir}/{state}/licenses-{state}-{date}.csv', index=False)
        manager.create_log(f'Collected {state.upper()} licenses.')
        licenses = pd.concat([licenses, data])
        # except:
        #     manager.create_log(f'Failed to aggregate {state.upper()} licenses.')

    # Save all of the retailers.
    licenses.to_csv(f'{data_dir}/all/licenses-{date}.csv', index=False)
    manager.create_log(f'Finished collecting licenses data.')
    return licenses


# === Test ===
# [ ] Tested:
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
        args = {'d': '../data/all', 'env_file': '../../../.env'}

    # Get arguments.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')

    # Get licenses for each state.
    all_licenses = main(data_dir, env_file)

    # TODO: Upload all CSVs to Firebase Storage.

