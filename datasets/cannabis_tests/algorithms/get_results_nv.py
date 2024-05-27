"""
Get Results Nevada
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/25/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Nevada lab result data obtained through public records requests.

"""
# Standard imports:
import os
from datetime import datetime

# External imports:
import pandas as pd
from cannlytics.utils import snake_case
from cannlytics.utils.constants import ANALYTES

# Define standard columns.
columns = {
    'Id': 'sample_id',
    'PackagedByFacilityName': 'producer',
    'PackagedByFacilityLicenseNumber': 'producer_license_number',
    'LabFacilityName': 'lab',
    'LabFacilityLicenseNumber': 'lab_license_number',
    'Label': 'label',
    'PackageType': 'package_type',
    'Quantity': 'quantity',
    'UnitOfMeasureId': 'units_id',
    'UnitOfMeasureName': 'unit_of_measure_name',
    'UnitOfMeasureAbbreviation': 'unit_of_measure_abbreviation',
    'ProductName': 'product_name',
    'ProductCategoryName': 'product_type',
    'InitialLabTestingState': 'initial_lab_testing_state',
    'LabTestingState': 'lab_testing_state',
    'LabTestingStateName': 'lab_testing_state_name',
    'LabTestingStateDate': 'date_tested',
    'IsTestingSample': 'is_testing_sample',
    'IsProcessValidationTestingSample': 'is_process_validation_testing_sample',
    'ProductRequiresRemediation': 'product_requires_remediation',
    'ContainsRemediatedProduct': 'contains_remediated_product',
    'RemediationDate': 'remediation_date',
    'RemediationRecordedDateTime': 'remediation_recorded_datetime',
    'PackagedDate': 'date_packaged',
    'LabTestDetailId': 'lab_test_detail_id',
    'TestPerformedDate': 'test_performed_date',
    'LabTestResultDocumentFileId': 'lab_test_result_document_file_id',
    'OverallPassed': 'overall_passed',
    'TestTypeName': 'test_type',
    'TestPassed': 'test_passed',
    'TestResultLevel': 'test_result',
    'TestComment': 'test_comment',
    'ArchivedDate': 'archived_date',
    'FinishedDate': 'date_finished',
    'IsOnHold': 'is_on_hold'
}

# Define the data types for each column.
dtype_spec = {
    'Id': str,
    'PackagedByFacilityName': str,
    'PackagedByFacilityLicenseNumber': str,
    'LabFacilityName': str,
    'LabFacilityLicenseNumber': str,
    'Label': str,
    'PackageType': str,
    'Quantity': float,
    'UnitOfMeasureId': str,
    'UnitOfMeasureName': str,
    'UnitOfMeasureAbbreviation': str,
    'ProductName': str,
    'ProductCategoryName': str,
    'InitialLabTestingState': str,
    'LabTestingState': str,
    'LabTestingStateName': str,
    'LabTestingStateDate': str,
    'IsTestingSample': bool,
    'IsProcessValidationTestingSample': bool,
    'ProductRequiresRemediation': bool,
    'ContainsRemediatedProduct': bool,
    'RemediationDate': str,
    'RemediationRecordedDateTime': str,
    'PackagedDate': str,
    'LabTestDetailId': str,
    'TestPerformedDate': str,
    'LabTestResultDocumentFileId': str,
    'OverallPassed': bool,
    'TestTypeName': str,
    'TestPassed': bool,
    'TestResultLevel': str,
    'TestComment': str,
    'ArchivedDate': str,
    'FinishedDate': str,
    'IsOnHold': bool
}

def read_and_standardize_csv(file_path, columns, dtype_spec):
    """Read a CSV file and standardize the column names."""
    try:
        df = pd.read_csv(file_path, dtype=dtype_spec, low_memory=False)
        df.rename(columns=columns, inplace=True)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def collect_data(data_dir, columns, dtype_spec):
    """Collect data from a directory of CSV files."""
    results = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if 'no data' in file.lower():
                continue
            if file.endswith('.csv'):
                print('Reading:', file)
                file_path = os.path.join(root, file)
                df = read_and_standardize_csv(file_path, columns, dtype_spec)
                if not df.empty:
                    results.append(df)
    return pd.concat(results, ignore_index=True)

def standardize_analyte_names(df, analyte_mapping):
    """Standardize analyte names."""
    df.columns = [analyte_mapping.get(snake_case(col), snake_case(col)) for col in df.columns]
    return df

def augment_fields(df):
    """Augment the DataFrame with additional calculated fields."""
    # Calculate the total cannabinoids
    df['total_cannabinoids'] = df[['cbd', 'cbda', 'cbn', 'delta_8_thc', 'delta_9_thc', 'thca']].sum(axis=1)

    # Calculate the total terpenes
    terpene_columns = [
        'alpha_bisabolol', 'alpha_humulene', 'alpha_pinene', 'alpha_terpinolene', 
        'beta_pinene', 'beta_caryophyllene', 'beta_myrcene',
        # FIXME: This is a misspelling.
        # 'carophyllene_oxide', 
        'limonene', 'linalool'
    ]
    # TODO: Also include 'Other Terpenes'.
    df['total_terpenes'] = df[terpene_columns].sum(axis=1)

    # Calculate the total THC to total CBD ratio
    df['total_thc'] = df['delta_9_thc'] + 0.877 * df['thca']
    df['total_cbd'] = df['cbd'] + 0.877 * df['cbda']
    df['thc_cbd_ratio'] = df['total_thc'] / df['total_cbd']

    # Calculate the total cannabinoids to total terpenes ratio
    df['cannabinoids_terpenes_ratio'] = df['total_cannabinoids'] / df['total_terpenes']

    # Convert date_tested to datetime, reconvert in case of any remaining inconsistencies
    df['date_tested'] = pd.to_datetime(df['date_tested'], format='mixed', errors='coerce')
    df['date_tested'] = pd.to_datetime(df['date_tested'], format='mixed', errors='coerce')

    # Return the augmented data.
    return df


def combine_redundant_columns(df):
    """Combine redundant columns and extract units and product types."""
    combined_results = {}
    product_types = [
        'Infused Edible',
        'Infused Non-Edible',
        'Non-Solvent Concentrate',
        'R&D Testing',
        'Raw Plant Material',
        'Solvent Based Concentrate',
        'Sub-Contract',
        'Whole Wet Plant',
    ]
    for col in df.columns:
        matched = False
        for product_type in product_types:
            if product_type in col and '(' not in col:
                base_name = col.split(product_type)[0].strip()
                if base_name not in combined_results:
                    combined_results[base_name] = df[col]
                    print('New column:', base_name)
                else:
                    combined_results[base_name] = combined_results[base_name].fillna(df[col])
                    print('Combined column:', base_name)
                matched = True
        if matched:
            continue
        if '(' in col and ')' in col:
            base_name = col.split('(')[0].strip()
            if base_name not in combined_results:
                combined_results[base_name] = df[col]
                print('New column:', base_name)
            else:
                combined_results[base_name] = combined_results[base_name].fillna(df[col])
                print('Combined column:', base_name)
        elif col not in combined_results:
            print('New column:', col)
            combined_results[col] = df[col]
    return pd.DataFrame(combined_results)


# === Test ===
# [✓] Tested: 2024-05-25 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Collect Nevada lab results
    data_dir = r'D:\data\public-records\Nevada-001'
    data = collect_data(data_dir, columns, dtype_spec)

    # Pivot the data to get results for each package label
    results = data.pivot_table(
        index=['label', 'producer', 'lab', 'product_name', 'product_type', 'date_tested', 'date_packaged', 'date_finished'],
        columns='test_type',
        values='test_result',
        aggfunc='first'
    ).reset_index()
    print('Number of Nevada test samples:', len(results))

    # Combine redundant columns
    results = combine_redundant_columns(results)
    print('Combined redundant columns.')
    list(results.columns)

    # Standardize the analyte names
    results = standardize_analyte_names(results, ANALYTES)
    print('Standardized analyte names.')

    # Augment fields with additional calculated metrics
    results = augment_fields(results)
    print('Augmented fields.')

    # TODO: Ensure all numeric columns are numeric.
    non_numeric = [
        'label', 'producer', 'lab', 'product_name',
        'product_type', 'date_tested', 'date_packaged', 'date_finished'
    ]

    # Optional: Drop nuisance columns.
    drop = ['']
    results = results.drop(columns=drop, errors='ignore')

    # Save the curated results
    stats_dir = 'D://data/nevada/results/datasets'
    date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    outfile = f'{stats_dir}/nv-results-{date}.xlsx'
    results.to_excel(outfile, index=False)
    results.to_csv(f'{stats_dir}/nv-results-latest.csv', index=False)
    print('Nevada lab results archived:', outfile)
