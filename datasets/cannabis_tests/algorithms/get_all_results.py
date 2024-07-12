"""
Get All Results | Cannabis Results
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/10/2024
Updated: 7/11/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Aggregate cannabis test data from states with permitted cannabis use:

    - Alaska
    ✓ California
    ✓ Connecticut
    ✓ Florida
    ✓ Hawaii
    ✓ Maryland
    ✓ Massachusetts
    ✓ Michigan
    ✓ Nevada
    ✓ New York
    ✓ Oregon
    ✓ Rhode Island
    ✓ Utah
    ✓ Washington

"""
# Standard imports:
import json
import os

# External imports:
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import find_unique_analytes
import pandas as pd

def get_all_results(
        data_dir,
        subsets=None,
        ext='csv',
        version='latest',
        verbose=True,
    ):
    """Save all of the lab results to a single CSV file."""

    # Read all of the latest license data.
    all_data = []
    # Walk directory and find all -latest.csv files
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(f'{version}.{ext}'):
                file_path = os.path.join(root, file)
                print('Reading:', file_path)
                if ext == 'jsonl':
                    subset_data = pd.read_json(file_path, lines=True)
                elif ext == 'csv':
                    try:
                        subset_data = pd.read_csv(file_path)
                    except:
                        subset_data = pd.read_excel(file_path.replace('.csv', '.xlsx'))
                else:
                    subset_data = pd.read_excel(file_path)
                all_data.append(subset_data)
                # if verbose:
                #     print('Aggregated data for', file_path)

    # Merge historic MI results.
    # TODO: Separate this logic into `get_results_mi.py`
    # import ast
    # from cannlytics.data.coas import CoADoc
    # from cannlytics.utils import snake_case, convert_to_numeric
    
    # datafile = r"D:\data\cannabis_results\data\mi\mi-results-psi-labs-2022-07-12.xlsx"
    # psi_results = pd.read_excel(datafile)
    # psi_results['lab_state'] = 'MI'
    # psi_results['producer_state'] = 'MI'
    # psi_results['date'] = pd.to_datetime(psi_results['date_tested'], format='mixed', errors='coerce')
    # psi_results['week'] = psi_results['date'].dt.to_period('W').astype(str)
    # psi_results['month'] = psi_results['date'].dt.to_period('M').astype(str)
    # psi_results = psi_results.sort_values('date')

    # Add a `key` to the PSI Labs results.
    # parser = CoADoc()
    # fixed_results = []
    # for i, row in psi_results.iterrows():
    #     fixed_result = []
    #     sample_results = ast.literal_eval(row['results'])
    #     for result in sample_results:
    #         name = result['name']
    #         key = parser.analytes.get(snake_case(name), snake_case(name))
    #         value = convert_to_numeric(result['value'].replace('%', '').strip())
    #         fixed_result.append({
    #             'key': key,
    #             'name': name,
    #             'value': value,
    #             'margin_of_error': result.get('margin_of_error'),
    #             'limit': result.get('limit'),
    #             'status': result.get('status'),
    #         })
    #     fixed_results.append(json.dumps(fixed_result))
    # psi_results['results'] = fixed_results
        
    # analytes = find_unique_analytes(psi_results)
    # nuisance_analytes = [
    #     '',
    #     '1_2_dimethoxy_ethane',
    #     '2_2_dimethyl_butane',
    #     '2_3_dimethyl_butane',
    #     '3_methyl_pentane',
    #     'metrc_mi_cannabinoids_status',
    #     'metrc_mi_cannabinoids_value',
    #     'n_n_dimethylformamide',
    #     'percent_active_cbd',
    #     # TODO: Standardize these analytes.
    #     # 'xylene'
    #     # 'hexane',
    #     # 'hexanes',
    #     # 'transnerolidol_1',
    #     # 'transnerolidol_2',
    # ]
    # analytes = set(analytes) - set(nuisance_analytes)
    # analytes = sorted(list(analytes))
    # psi_results = standardize_results(psi_results, analytes)
    # outfile_csv = r'D:\data\cannabis_results\data\mi\mi-results-psi-labs-2022-07-12.csv'
    # psi_results.to_csv(outfile_csv, index=False)
    # print('Saved CSV:', outfile_csv)

    # DEV: Merge historic PSI Labs results.
    datafile = r'D:\data\cannabis_results\data\mi\mi-results-psi-labs-2022-07-12.csv'
    psi_results = pd.read_csv(datafile)
    all_data.append(psi_results)

    # OLD: Aggregate data by subset.
    # for subset in subsets:
    #     filename = f'{subset}-lab-results-{version}.{ext}'
    #     subset_data_dir = os.path.join(data_dir, subset)
    #     subset_data_file = os.path.join(subset_data_dir, filename)
    #     if os.path.exists(subset_data_file):
    #         if ext == 'jsonl':
    #             subset_data = pd.read_json(subset_data_file, lines=True)
    #         elif ext == 'csv':
    #             subset_data = pd.read_csv(subset_data_file)
    #         else:
    #             subset_data = pd.read_excel(subset_data_file)
    #         all_data.append(subset_data)
    #         if verbose:
    #             print('Aggregated data for', subset)
    #     elif verbose:
    #         print('No data for:', subset)

    # Save all of the licenses.
    aggregate = pd.concat(all_data)
    outfile = os.path.join(data_dir, 'all/all-results-latest.csv')
    aggregate.to_csv(outfile, index=False)
    if verbose:
        print('Aggregated %i results.' % len(aggregate))
        print('Saved CSV:', outfile)
        features = {x: 'string' for x in aggregate.columns}
        print('Number of features:', len(features))
        print('Features:', features)
    return aggregate

# === Test ===
# [✓] Tested: 2024-07-11 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Get all of the results.
    get_all_results(data_dir='D://data/cannabis_results/data')
