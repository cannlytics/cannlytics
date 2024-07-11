"""
Get Results Nevada
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/25/2024
Updated: 5/30/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Curate Nevada lab result data obtained through public records requests.

Data Sources:
    
    - Public records request

"""
# Standard imports:
from glob import glob
import os

# External imports:
from cannlytics.utils import snake_case
from cannlytics.utils.constants import ANALYTES
import pandas as pd

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
    for target_col, col_variants in similar_columns.items():
        if target_col not in df.columns:
            df[target_col] = pd.NA
        for col in col_variants:
            if col in df.columns:
                df[target_col] = df[target_col].combine_first(df[col])
                df.drop(columns=[col], inplace=True)
    return df

def augment_metadata(results, data, sample_columns, boolean_columns,):
    """Reattach missing columns from `data` to `results`."""
    for col in sample_columns:
        if col not in results.columns:
            results[col] = results['label'].map(data.drop_duplicates('label').set_index('label')[col])
    for col in boolean_columns:
        if col not in results.columns:
            results[col] = results['label'].map(data.groupby('label')[col].transform(lambda x: any(x) if x.name in ['overall_passed', 'test_passed'] else all(x)))
    return results

def get_results_nv(
        data_dir: str,
        output_dir: str,
        licenses_dir: str,
        labs_dir: str,
    ) -> pd.DataFrame:
    """Get results for Oregon."""

    # === Read the results ===

    # Collect Nevada lab results
    data = collect_data(data_dir, columns, dtype_spec)

    # === Standardize the results ===

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
        'beta_pinene': ['Beta Pinene', 'Beta-Pinene'],
        'caryophyllene_oxide': ['Carophyllene Oxide', 'Caryophyllene Oxide'],
        'delta_8_thc': ['Delta 8 THC', 'Delta-8 THC'],
        'delta_9_thc': ['Delta 9 THC', 'Delta-9 THC'],
        'thca': ['THCA', 'THCa'],
        'total_yeast_and_mold': ['Total Yeast and Mold', 'Yeast and Mold']
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

    # Augment metadata.
    sample_columns = [
        'sample_id', 'package_type', 'quantity', 'units_id', 'unit_of_measure_name',
        'unit_of_measure_abbreviation', 'lab_testing_state', 'lab_testing_state_name',
        'remediation_date', 'remediation_recorded_datetime', 'lab_test_detail_id',
        'test_performed_date', 'lab_test_result_document_file_id', 'archived_date',
        'lab_license_number', 'producer_license_number'
    ]
    boolean_columns = [
        'contains_remediated_product', 'product_requires_remediation', 'is_on_hold',
        'is_process_validation_testing_sample', 'is_testing_sample', 'overall_passed', 'test_passed'
    ]
    results = augment_metadata(results, data, sample_columns, boolean_columns)
    print('Augmented metadata.')

    # Augment additional calculated metrics.
    cannabinoids = ['cbd', 'cbda', 'cbn', 'delta_8_thc', 'delta_9_thc', 'thca']
    terpenes = [
        'alpha_bisabolol', 'alpha_humulene', 'alpha_pinene', 'alpha_terpinene', 
        'terpinolene', 'beta_pinene', 'beta_caryophyllene', 'beta_myrcene', 
        'd_limonene', 'linalool', 'caryophyllene_oxide', 'other_terpenes'
    ]
    results = augment_calculations(results, cannabinoids, terpenes)
    print('Augmented fields.')

    # Convert dates to datetime and ensure they are timezone unaware.
    date_columns = [
        'date_tested', 'test_performed_date', 'date_packaged',
        'date_finished', 'remediation_date', 'archived_date'
    ]
    for col in date_columns:
        if col in results.columns:
            results[col] = pd.to_datetime(results[col], errors='coerce').dt.tz_localize(None)

    #  === Augment licensee data. ===

    # Read NV lab license data.
    lab_columns = {
        'CEID': 'lab_id',
        'premise_county': 'lab_county',
        'premise_state': 'lab_state',
    }
    lab_licenses = pd.read_csv(labs_dir, low_memory=False)
    lab_licenses['license_number'] = lab_licenses['license_number'].astype(str)
    lab_licenses.set_index('license_number', inplace=True)
    lab_licenses.rename(columns=lab_columns, inplace=True)

    # Read NV licenses.
    license_columns = {
        'CEID': 'producer_id',
        'license_type': 'producer_license_type',
        'premise_county': 'producer_county',
        'premise_state': 'producer_state',
        'business_legal_name': 'producer_legal_name',
    }
    license_files = sorted(
        glob(os.path.join(licenses_dir, '*licenses*.csv')),
        key=os.path.getmtime,
        reverse=True
    )
    all_licenses = pd.concat(
        (pd.read_csv(file, low_memory=False) for file in license_files),
        ignore_index=True
    )
    all_licenses['license_number'] = all_licenses['license_number'].astype(str)
    all_licenses = all_licenses.drop_duplicates(subset='license_number', keep='first')
    all_licenses.set_index('license_number', inplace=True)
    all_licenses.rename(columns=license_columns, inplace=True)

    # Augment lab license data.
    labs = list(results['lab_license_number'].unique())
    for lab in labs:
        if lab in lab_licenses.index:
            license_data = lab_licenses.loc[lab]
            for key in lab_columns.values():
                if key in lab_licenses.columns:
                    # FIXME: Does this need to be changed?
                    results[key] = results['lab_license_number'].map(lab_licenses[key])
                    # results[key] = results['lab_license_number'].map(license_data[key])

    # Augment producer license data.
    producers = list(results['producer_license_number'].unique())
    for producer in producers:
        if producer in all_licenses.index:
            license_data = all_licenses.loc[producer]
            for key in license_columns.values():
                if key in all_licenses.columns:
                    # FIXME: Does this need to be changed?
                    results[key] = results['producer_license_number'].map(all_licenses[key])
                    # results[key] = results['lab_license_number'].map(license_data[key])

    # === Save the results. ===

    # Sort the columns.
    non_numeric_cols = non_numeric + sample_columns + boolean_columns + date_columns
    non_numeric_cols += list(lab_columns.values()) + list(license_columns.values())
    numeric_cols = [col for col in results.columns if col not in non_numeric_cols]
    numeric_cols_sorted = sorted(numeric_cols)
    results = results[non_numeric_cols + numeric_cols_sorted]

    # # Save the results with copyright and sources sheets.
    # stats_dir = 'D://data/nevada/results/datasets'
    # date = datetime.now().strftime('%Y-%m-%d')
    # if not os.path.exists(stats_dir): os.makedirs(stats_dir)
    # outfile = f'{stats_dir}/nv-results-{date}.xlsx'
    # save_with_copyright(
    #     results,
    #     outfile,
    #     dataset_name='Nevada Cannabis Lab Results',
    #     author='Keegan Skeate',
    #     publisher='Cannlytics',
    #     sources=['Nevada Cannabis Compliance Board'],
    #     source_urls=['https://ccb.nv.gov/'],
    # )
    # print('Saved Nevada lab results:', outfile)

    # Save the results.
    outfile = os.path.join(output_dir, 'nv-results-latest.xlsx')
    outfile_csv = os.path.join(output_dir, 'nv-results-latest.csv')
    outfile_json = os.path.join(output_dir, 'nv-results-latest.jsonl')
    results.to_excel(outfile, index=False)
    results.to_csv(outfile_csv, index=False)
    results.to_json(outfile_json, orient='records', lines=True)
    print('Saved Excel:', outfile)
    print('Saved CSV:', outfile_csv)
    print('Saved JSON:', outfile_json)

    # Return the results.
    return results

# === Test ===
# [✓] Tested: 2024-07-10 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Define where the data lives.
    data_dir = 'D://data/public-records/Nevada-001'
    licenses_dir = r"C:\Users\keega\Documents\cannlytics\cannlytics\datasets\cannabis_licenses\data\nv"
    labs_dir = r"C:\Users\keega\Documents\cannlytics\cannlytics\datasets\cannabis_licenses\data\nv\labs-nv-2023-12-17T11-41-34.csv"
    output_dir = 'D://data/nevada/results/datasets'

    # Curate results.
    get_results_nv(
        data_dir=data_dir,
        output_dir=output_dir,
        licenses_dir=licenses_dir,
        labs_dir=labs_dir,
    )
