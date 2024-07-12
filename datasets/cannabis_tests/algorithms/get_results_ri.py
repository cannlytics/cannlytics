"""
Get Results Rhode Island
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/30/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Rhode Island lab result data obtained through public records requests.

Data Sources:
    
    - Public records request

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cannlytics.data import save_with_copyright
from cannlytics.utils import snake_case
from cannlytics.utils.constants import ANALYTES
import numpy as np
import pandas as pd

# Define columns.
columns = {
    'Id': 'sample_id',
    'TestingFacilityName': 'lab',
    'ItemFromFacilityLicenseNumber': 'producer_license_number',
    'SourcePackageLabels': 'label',
    'TestPerformedDate': 'date_tested',
    'TestTypeName': 'test_type',
    'TestResultLevel': 'test_result',
    'OverallPassed': 'status',
}

# Define the data types for each column.
dtype_spec = {
    'Id': str,
    'TestingFacilityName': str,
    'ItemFromFacilityLicenseNumber': str,
    'SourcePackageLabels': str,
    'TestPerformedDate': str,
    'TestTypeName': str,
    'TestResultLevel': float,
    'OverallPassed': bool,
}

def collect_data(data_dir, columns, dtype_spec):
    """Collect data from a directory of CSV and Excel files."""
    results = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if 'no data' in file.lower():
                continue
            print('Reading:', file)
            file_path = os.path.join(root, file)
            if file.endswith('.csv'):
                df = read_and_standardize_csv(file_path, columns, dtype_spec)
            elif file.endswith('.xlsx'):
                df = read_and_standardize_excel(file_path, columns)
            if not df.empty:
                results.append(df)
    return pd.concat(results, ignore_index=True)

def read_and_standardize_csv(file_path, columns, dtype_spec):
    """Read a CSV file and standardize the column names."""
    try:
        df = pd.read_csv(file_path, dtype=dtype_spec, usecols=columns.keys(), encoding='latin1')
        df.rename(columns=columns, inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def read_and_standardize_excel(file_path, columns):
    """Read an Excel file and standardize the column names."""
    try:
        df = pd.read_excel(file_path, usecols=columns.keys())
        df.rename(columns=columns, inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def extract_test_details(data):
    """Extract test_name, units, and product_type from test_type."""
    data[['test_name', 'units', 'product_type']] = data['test_type'].str.extract(r'(.+?) \((.+?)\) (.+)')
    return data

def pivot_data(data):
    """Pivot the data to get results for each sample."""
    results = data.pivot_table(
        index=['sample_id', 'producer_license_number', 'lab', 'label', 'date_tested', 'product_type'],
        columns='test_name',
        values='test_result',
        aggfunc='first'
    ).reset_index()
    results['date_tested'] = pd.to_datetime(results['date_tested'], errors='coerce')
    results['month'] = results['date_tested'].dt.to_period('M')
    results['year'] = results['date_tested'].dt.year
    return results

def augment_calculations(
        df,
        cannabinoids=None,
        terpenes=None,
        delta_9_thc='delta_9_thc',
        thca='thca',
        cbd='cbd',
        cbda='cbda',
    ):
    """Augment the DataFrame with additional calculated fields."""
    # Calculate total cannabinoids.
    if cannabinoids is not None:
        df['total_cannabinoids'] = round(df[cannabinoids].sum(axis=1), 2)

    # Calculate total terpenes.
    if terpenes is not None:
        df['total_terpenes'] = round(df[terpenes].sum(axis=1), 2)

    # Calculate the total THC to total CBD ratio.
    df['total_thc'] = round(df[delta_9_thc] + 0.877 * df[thca], 2)
    df['total_cbd'] = round(df[cbd] + 0.877 * df[cbda], 2)
    df['thc_cbd_ratio'] = round(df['total_thc'] / df['total_cbd'], 2)

    # Calculate the total cannabinoids to total terpenes ratio.
    if cannabinoids is not None and terpenes is not None:
        df['cannabinoids_terpenes_ratio'] = round(df['total_cannabinoids'] / df['total_terpenes'], 2)

    # Return the augmented data.
    return df

def standardize_analyte_names(df, analyte_mapping):
    """Standardize analyte names."""
    df.columns = [analyte_mapping.get(snake_case(col), snake_case(col)) for col in df.columns]
    return df

def combine_similar_columns(df, similar_columns):
    """Combine similar columns with different spellings or capitalization."""
    for target_col, col_variants in similar_columns.items():
        if target_col not in df.columns:
            df[target_col] = pd.NA
        for col in col_variants:
            if col in df.columns:
                df[target_col] = df[target_col].combine_first(df[col])
                df.drop(columns=[col], inplace=True)
    return df

def get_results_ri(data_dir: str, output_dir: str) -> pd.DataFrame:

    # Collect Rhode Island lab results
    data = collect_data(data_dir, columns, dtype_spec)
    print('Number of Rhode Island tests:', len(data))

    # Extract test details
    data = extract_test_details(data)

    # Pivot the data to get results for each sample.
    results = pivot_data(data)
    print('Number of Rhode Island samples:', len(results))

    # Combine similar names.
    similar_columns = {
        'total_yeast_and_mold': ['Total Yeast and MOld', 'Total Yeast and Mold'],
        '1_2_dichloroethane': ['1,2 Dichlorethane', '1,2 Dichloroethane'],
        'total_cbd': ['Total CBD'],
        'total_thc': ['Total THC'],
        '3_methylpentane': ['3 Methylpetane', '3 Methylpentane'],
        'n_methylpyrrolidone': ['N Methylpyrrolidone', 'N methylpyrrlidone'],
        'n_n_dimethylacetamide': ['N,N Dimethyacetamide', 'N,N Dimethylacetamide'],
    }
    results = combine_similar_columns(results, similar_columns)

    # Standardize the analyte names
    results = standardize_analyte_names(results, ANALYTES)
    print('Standardized analyte names.')

    # Augment additional calculated metrics.
    cannabinoids = ['cbd', 'cbda', 'delta_9_thc', 'thca']
    terpenes = [
        'alpha_bisabolol', 'alpha_humulene', 'alpha_pinene',
        'alpha_terpinene', 'beta_caryophyllene', 'beta_myrcene',
        'beta_pinene', 'caryophyllene_oxide', 'd_limonene', 'linalool',
        'nerolidol', 'other_terpenes'
    ]
    results = augment_calculations(results)
    print('Augmented fields.')

    # Sort the columns.
    non_numeric = [
        'sample_id', 'producer_license_number', 'lab', 'label',
        'date_tested', 'product_type', 'month', 'year'
    ]
    numeric_cols = results.columns.difference(non_numeric)
    numeric_cols_sorted = sorted(numeric_cols)
    results = results[non_numeric + numeric_cols_sorted]

    # # Save the results with copyright and sources sheets.
    # date = datetime.now().strftime('%Y-%m-%d')
    # if not os.path.exists(output_dir): os.makedirs(output_dir)
    # outfile = f'{output_dir}/ri-results-{date}.xlsx'
    # save_with_copyright(
    #     results,
    #     outfile,
    #     dataset_name='Rhode Island Cannabis Lab Results',
    #     author='Keegan Skeate',
    #     publisher='Cannlytics',
    #     sources=['Rhode Island Office Of Cannabis Regulation'],
    #     source_urls=['https://dbr.ri.gov/office-cannabis-regulation'],
    # )
    # print('Saved Rhode Island lab results:', outfile)

    # Save the results.
    outfile = os.path.join(output_dir, 'ri-results-latest.xlsx')
    outfile_csv = os.path.join(output_dir, 'ri-results-latest.csv')
    outfile_json = os.path.join(output_dir, 'ri-results-latest.jsonl')
    results.to_excel(outfile, index=False)
    results.to_csv(outfile_csv, index=False)
    # FIXME: This causes an OverflowError
    # results.to_json(outfile_json, orient='records', lines=True)
    print('Saved Excel:', outfile)
    print('Saved CSV:', outfile_csv)
    # print('Saved JSON:', outfile_json)

    # Return the results.
    return results

# === Test ===
# [✓] Tested: 2024-07-10 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Define where the data lives.
    data_dir = 'D://data/public-records/Rhode Island/Rhode Island'
    output_dir = 'D://data/rhode-island/results/datasets'

    # Curate results.
    get_results_ri(data_dir=data_dir, output_dir=output_dir)
