"""
Cannabis Tests | Aggregate All Tests
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/23/2023
Updated: 9/23/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Aggregate cannabis test data from states with permitted cannabis use:

    ✓ California
    ✓ Connecticut
    ✓ Florida
    - Maryland
    ✓ Massachusetts
    ✓ Michigan
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
    'ca': 'get_results_ca',
    'ct': 'get_results_ct',
    'fl': 'get_results_fl',
    # 'md': 'get_results_md',
    'ma': 'get_results_ma',
    'mi': 'get_results_mi',
    'wa': 'get_results_wa',
    'wa-inventory': 'get_inventory_wa',
}


def main(data_dir, env_file):
    """Collect all cannabis tests."""

    # Initialize.
    all_data = pd.DataFrame()
    manager = Cannlytics()

    # Add the state_modules directory to sys.path for dynamic imports
    sys.path.append(os.getcwd())

    # Collect licenses for each state.
    for state, algorithm in ALGORITHMS.items():

        # Import the module and get the entry point.
        module = importlib.import_module(algorithm)
        entry_point = getattr(module, algorithm)

        # Collect results for the state.
        manager.create_log(f'Getting results data for {state.upper()}.')
        data = entry_point(data_dir, env_file=env_file)
        all_data = pd.concat([all_data, data])

    # Save all of the licenses.
    date = datetime.now().strftime('%Y-%m-%d')
    all_data_dir = os.path.join(data_dir, 'all')
    if not os.path.exists(all_data_dir):
        os.makedirs(all_data_dir)
    all_data.to_csv(os.path.join(all_data_dir, f'all-lab-results-{date}.csv'), index=False)
    all_data.to_csv(os.path.join(all_data_dir, f'all-lab-results-latest.csv'), index=False)
    manager.create_log(f'Finished collecting lab result data.')
    return all_data


def save_all_lab_results(data_dir, version='latest'):
    """Save all of the lab results to a single CSV file."""

    # Read all of the latest license data.
    all_data = []
    states = ALGORITHMS.keys()
    for state in states:
        filename = f'{state}-lab-results-{version}.csv'
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
        filename = f'all/all-lab-results-{version}.csv'
        all_data_file = os.path.join(data_dir, filename)
        aggregate.to_csv(all_data_file, index=False)
        print('Saved all results to', all_data_file)
        return aggregate
    
    # No datafiles found.
    else:
        print('No results to save.')
        return None


# === Test ===
# [✓] Tested: 2023-09-23 by Keegan Skeate <keegan@cannlytics>
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

    # Get results for each state.
    # aggregate = main(data_dir, env_file)

    # Save all results.
    data_dir = '../data'
    aggregate = save_all_lab_results(data_dir)
    print('Saved %i lab results.' % len(aggregate))

    # TODO: Upload all CSVs to Firebase Storage.