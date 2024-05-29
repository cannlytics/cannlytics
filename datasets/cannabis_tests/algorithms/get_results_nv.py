"""
Get Results Nevada
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/28/2024
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
    # Calculate total cannabinoids.
    df['total_cannabinoids'] = df[['cbd', 'cbda', 'cbn', 'delta_8_thc',
                                   'delta_9_thc', 'thca']].sum(axis=1)

    # Calculate total terpenes.
    terpene_columns = [
        'alpha_bisabolol', 'alpha_humulene', 'alpha_pinene', 'alpha_terpinene', 
        'terpinolene', 'beta_pinene', 'beta_caryophyllene', 'beta_myrcene', 
        'd_limonene', 'linalool', 'caryophyllene_oxide', 'other_terpenes'
    ]
    df['total_terpenes'] = df[terpene_columns].sum(axis=1)

    # Calculate the total THC to total CBD ratio.
    df['total_thc'] = round(df['delta_9_thc'] + 0.877 * df['thca'], 2)
    df['total_cbd'] = round(df['cbd'] + 0.877 * df['cbda'], 2)
    df['thc_cbd_ratio'] = round(df['total_thc'] / df['total_cbd'], 2)

    # Calculate the total cannabinoids to total terpenes ratio.
    df['cannabinoids_terpenes_ratio'] = round(df['total_cannabinoids'] / df['total_terpenes'], 2)

    # Convert dates to datetime, reconverting in case of any remaining inconsistencies.
    df['date_tested'] = pd.to_datetime(df['date_tested'], format='mixed', errors='coerce')
    df['date_tested'] = pd.to_datetime(df['date_tested'], format='mixed', errors='coerce')

    # Return the augmented data.
    return df


def combine_redundant_columns(df, product_types=None, verbose=False):
    """Combine redundant columns and extract units and product types."""
    combined_results = {}
    for col in df.columns:
        matched = False
        if product_types is not None:
            for product_type in product_types:
                if product_type in col and '(' not in col:
                    base_name = col.split(product_type)[0].strip()
                    if base_name not in combined_results:
                        combined_results[base_name] = df[col]
                        if verbose:
                            print('New column:', base_name)
                    else:
                        combined_results[base_name] = combined_results[base_name].fillna(df[col])
                        if verbose:
                            print('Combined column:', base_name)
                    matched = True
        if matched:
            continue
        if '(' in col and ')' in col:
            base_name = col.split('(')[0].strip()
            if base_name not in combined_results:
                combined_results[base_name] = df[col]
                if verbose:
                    print('New column:', base_name)
            else:
                combined_results[base_name] = combined_results[base_name].fillna(df[col])
                if verbose:
                    print('Combined column:', base_name)
        elif col not in combined_results:
            if verbose:
                print('New column:', col)
            combined_results[col] = df[col]
    return pd.DataFrame(combined_results)


def combine_similar_columns(df, similar_columns):
    """Combine similar columns with different spellings or capitalization."""
    for correct_name, similar_name in similar_columns.items():
        if correct_name in df.columns and similar_name in df.columns:
            df[similar_name] = df[similar_name].fillna(df[correct_name])
            df.drop(columns=[correct_name], inplace=True)
        elif correct_name in df.columns:
            df.rename(columns={correct_name: similar_name}, inplace=True)
    return df


def augment_metadata(results, data, columns):
    """Reattach missing columns from `data` to `results` using the first observed value."""
    for key in list(columns.keys()):
        if key not in results.columns:
            if col in data.columns:
                first_value = data[key].dropna().iloc[0] if not data[key].dropna().empty else None
                results[key] = first_value
            else:
                results[key] = None
    return results



# === Test ===
# [✓] Tested: 2024-05-27 by Keegan Skeate <keegan@cannlytics>
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
    results = combine_redundant_columns(results, product_types=product_types)
    print('Combined redundant columns.')

    # Combine similar columns.
    similar_columns = {
        'Beta Pinene': 'beta_pinene',
        'Beta-Pinene': 'beta_pinene',
        'Carophyllene Oxide': 'caryophyllene_oxide',
        'Caryophyllene Oxide': 'caryophyllene_oxide',
        'Delta 8 THC': 'delta_8_thc',
        'Delta-8 THC': 'delta_8_thc',
        'Delta 9 THC': 'delta_9_thc',
        'Delta-9 THC': 'delta_9_thc',
        'THCA': 'thca',
        'THCa': 'thca',
        'Total Yeast and Mold': 'total_yeast_and_mold',
        'Yeast and Mold': 'total_yeast_and_mold',
    }
    results = combine_similar_columns(results, similar_columns)
    print('Combined similar columns.')

    # Standardize the analyte names
    results = standardize_analyte_names(results, ANALYTES)
    print('Standardized analyte names.')

    # Drop nuisance columns.
    drop = ['']
    results = results.drop(columns=drop, errors='ignore')

    # Ensure all numeric columns are numeric.
    non_numeric = [
        'label', 'producer', 'lab', 'product_name',
        'product_type', 'date_tested', 'date_packaged', 'date_finished'
    ]
    numeric_cols = results.columns.difference(non_numeric)
    for col in numeric_cols:
        results[col] = pd.to_numeric(results[col], errors='coerce')
    print('Converted columns to numeric.')

    # Augment fields with additional calculated metrics
    results = augment_fields(results)
    print('Augmented fields.')

    # FIXME: Augment sample metadata.
    # Note: If any value is not null, then the result value is the first observed value.
    # - sample_id
    # - package_type
    # - quantity
    # - units_id
    # - unit_of_measure_name
    # - unit_of_measure_abbreviation
    # - lab_testing_state
    # - lab_testing_state_name
    # - remediation_date
    # - remediation_recorded_datetime
    # - lab_test_detail_id
    # - test_performed_date
    # - lab_test_result_document_file_id
    # - archived_date

    # FIXME: Augment boolean metadata.
    # Note: If any value is True, then the result value is True.
    # - contains_remediated_product
    # - product_requires_remediation
    # - is_on_hold
    # - is_process_validation_testing_sample
    # - is_testing_sample
    # Note: If any value is False, then the result value is False.
    # - overall_passed
    # - test_passed

    # FIXME: augment lab data:
    # - lab_license_number
    # Example:
    labs = list(results['lab'].unique())
    for lab in labs:
        lab_data = data.loc[data['lab'] == lab]
        lab_license_number = lab_data['lab_license_number'].dropna().iloc[0]
        results.loc[results['lab'] == lab, 'lab_license_number'] = lab_license_number

    # FIXME: Augment producer data:
    # - producer_license_number
    # Example:
    producers = list(results['producer'].unique())
    for producer in producers:
        producer_data = data.loc[data['producer'] == producer]
        producer_license_number = producer_data['producer_license_number'].dropna().iloc[0]
        results.loc[results['producer'] == producer, 'producer_license_number'] = producer_license_number


    #  === TODO: Augment licensee data. ===

    # Read NV license data.
    datafile = r"C:\Users\keega\Documents\cannlytics\cannlytics\datasets\cannabis_licenses\data\nv\licenses-nv-2024-05-13.csv"
    licenses = pd.read_csv(datafile, low_memory=False)

    # Save the curated results
    stats_dir = 'D://data/nevada/results/datasets'
    date = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    outfile = f'{stats_dir}/nv-results-{date}.xlsx'
    results.to_excel(outfile, index=False)
    results.to_csv(f'{stats_dir}/nv-results-latest.csv', index=False)
    print('Nevada lab results archived:', outfile)
