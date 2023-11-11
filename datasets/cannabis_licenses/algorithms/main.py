"""
Cannabis Licenses | Get All Licenses
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/29/2022
Updated: 9/20/2023
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
        ✓ Oregon
        ✓ Rhode Island
        ✓ Vermont
        ✓ Washington
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
    'ak': 'get_licenses_ak',
    'az': 'get_licenses_az',
    'ca': 'get_licenses_ca',
    'co': 'get_licenses_co',
    'ct': 'get_licenses_ct',
    'de': 'get_licenses_de',
    'il': 'get_licenses_il',
    'ma': 'get_licenses_ma',
    'md': 'get_licenses_md',
    'me': 'get_licenses_me',
    'mi': 'get_licenses_mi',
    'mo': 'get_licenses_mo',
    'mt': 'get_licenses_mt',
    'nj': 'get_licenses_nj',
    'nm': 'get_licenses_nm',
    'nv': 'get_licenses_nv',
    'ny': 'get_licenses_ny',
    'or': 'get_licenses_or',
    'ri': 'get_licenses_ri',
    'vt': 'get_licenses_vt',
    'wa': 'get_licenses_wa',
    # Future:
    # 'va': 'get_licenses_va',
    # 'mn': 'get_licenses_mn',
    # 'oh': 'get_licenses_oh',
    # Medical:
    # 'al': 'get_licenses_al',
    # 'ar': 'get_licenses_ar',
    # 'fl': 'get_licenses_fl',
    # 'ky': 'get_licenses_ky',
    # 'la': 'get_licenses_la',
    # 'ms': 'get_licenses_ms',
    # 'nd': 'get_licenses_nd',
    # 'nh': 'get_licenses_nh',
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
    sys.path.append(os.getcwd())

    # Collect licenses for each state.
    for state, algorithm in ALGORITHMS.items():

        # Import the module and get the entry point.
        module = importlib.import_module(algorithm)
        entry_point = getattr(module, algorithm)

        # Collect licenses for the state.
        # try:
        manager.create_log(f'Getting license data for {state.upper()}.')
        data = entry_point(data_dir, env_file=env_file)
        
        state_data_dir = os.path.join(data_dir, state)
        if not os.path.exists(state_data_dir):
            os.makedirs(state_data_dir)
        
        state_data_file = os.path.join(state_data_dir, f'licenses-{state}-{date}.csv')
        data.to_csv(state_data_file, index=False)
        manager.create_log(f'Collected {state.upper()} licenses.')
        licenses = pd.concat([licenses, data])
        # except:
        #     manager.create_log(f'Failed to aggregate {state.upper()} licenses.')

    # Save all of the licenses.
    all_data_dir = os.path.join(data_dir, 'all')
    if not os.path.exists(all_data_dir):
        os.makedirs(all_data_dir)
    all_data_file = os.path.join(all_data_dir, f'licenses-{date}.csv')
    licenses.to_csv(all_data_file, index=False)
    manager.create_log(f'Finished collecting licenses data.')
    return licenses


def save_all_licenses(data_dir, version='latest'):
    """Save all of the licenses to a single CSV file."""

    # Read all of the latest license data.
    all_data = []
    states = ALGORITHMS.keys()
    for state in states:
        filename = f'licenses-{state}-{version}.csv'
        state_data_dir = os.path.join(data_dir, state)
        state_data_file = os.path.join(state_data_dir, filename)
        if os.path.exists(state_data_file):
            state_data = pd.read_csv(state_data_file)
            all_data.append(state_data)
            print('Aggregated data for', state.upper())
        else:
            print(f'No data for {state.upper()}.')

    # Save all of the licenses.
    if all_data:
        aggregate = pd.concat(all_data)
        all_data_file = os.path.join(data_dir, f'all/licenses-all-{version}.csv')
        aggregate.to_csv(all_data_file, index=False)
        print('Saved all licenses to', all_data_file)
        return aggregate
    
    # No datafiles found.
    else:
        print('No licenses to save.')
        return None


# === Test ===
# [✓] Tested: 2023-09-20 by Keegan Skeate <keegan@cannlytics>
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
        args = {'d': '../data', 'env_file': '../../../.env'}

    # Get arguments.
    data_dir = args.get('d', args.get('data_dir'))
    env_file = args.get('env_file')

    # Get licenses for each state.
    # all_licenses = main(data_dir, env_file)

    # Save all licenses.
    data_dir = '../data'
    all_licenses = save_all_licenses(data_dir)
    print('Saved %i licenses.' % len(all_licenses))

    # TODO: Upload all CSVs to Firebase Storage.

