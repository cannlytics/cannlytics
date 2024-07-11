"""
Get All Results | Cannabis Results
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/10/2024
Updated: 7/10/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Aggregate cannabis test data from states with permitted cannabis use:

    - Alaska
    - California
    - Connecticut
    - Florida
    - Hawaii
    - Maryland
    - Massachusetts
    - Michigan
    - Nevada
    - New York
    - Oregon
    - Rhode Island
    - Utah
    - Washington

"""
# Standard imports:
import os

# External imports:
import pandas as pd

def get_all_results(
        data_dir,
        subsets,
        ext='jsonl',
        version='latest',
        verbose=True,
    ):
    """Save all of the lab results to a single CSV file."""

    # Read all of the latest license data.
    all_data = []
    for subset in subsets:
        filename = f'{subset}-lab-results-{version}.{ext}'
        subset_data_dir = os.path.join(data_dir, subset)
        subset_data_file = os.path.join(subset_data_dir, filename)
        if os.path.exists(subset_data_file):
            if ext == 'jsonl':
                subset_data = pd.read_json(subset_data_file, lines=True)
            elif ext == 'csv':
                subset_data = pd.read_csv(subset_data_file)
            else:
                subset_data = pd.read_excel(subset_data_file)
            all_data.append(subset_data)
            if verbose:
                print('Aggregated data for', subset)
        elif verbose:
            print('No data for:', subset)

    # Save all of the licenses.
    aggregate = pd.concat(all_data)
    outfile = os.path.join(data_dir, 'all/all-results-latest.xlsx')
    outfile_csv = os.path.join(data_dir, 'all/all-results-latest.csv')
    outfile_json = os.path.join(data_dir, 'all/all-results-latest.jsonl')
    aggregate.to_excel(outfile, index=False)
    aggregate.to_csv(outfile_csv, index=False)
    aggregate.to_json(outfile_json, orient='records', lines=True)
    if verbose:
        print('Saved Excel:', outfile)
        print('Saved CSV:', outfile_csv)
        print('Saved JSON:', outfile_json)
    return aggregate

# === Test ===
# [ ] Tested: 2024-07-10 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Define subsets.
    subsets = [
        # 'all',
        # 'ak',
        # 'ca',
        # 'ct',
        # 'fl',
        'hi',
        # 'ma',
        # 'md',
        # 'mi',
        # 'nv',
        # 'ny',
        # 'or',
        # 'ri',
        'ut',
        # 'wa',
    ]

    # Get all of the results.
    data_dir = 'D://data/cannabis_results/data'
    get_all_results(
        data_dir=data_dir,
        subsets=subsets,
    )
