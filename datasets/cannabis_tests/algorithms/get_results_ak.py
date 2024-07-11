"""
Get Cannabis Results | Alaska
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/10/2024
Updated: 7/10/2024
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Data Source:

    - Public records request

"""
# Standard imports:
from collections import defaultdict
import glob
import os
import json

# External imports:
from cannlytics.data.coas.coas import CoADoc
from cannlytics.utils.utils import snake_case
import pandas as pd

def process_file(parser, file_path, sample_id='PackageId'):
    """Process each file and transform the data."""
    chunks = pd.read_csv(file_path, chunksize=100000, low_memory=False)
    samples = {}
    for chunk in chunks:
        for _, row in chunk.iterrows():
            sample_id_value = row[sample_id]
            if sample_id_value not in samples:
                sample = {sample_columns[key]: row[key] for key in sample_columns if key in row}
                sample['results'] = []
                samples[sample_id_value] = sample
            result = {result_columns[key]: row[key] for key in result_columns if key in row}
            name = result['name']
            result['key'] = parser.analytes.get(snake_case(name), snake_case(name))
            samples[sample_id_value]['results'].append(result)
    return samples

def aggregate_and_save_to_csv(json_dir, output_csv):
    """Aggregate and save JSON files to CSV."""
    json_files = glob.glob(os.path.join(json_dir, '*.json'))
    all_samples = []
    for json_file in json_files:
        with open(json_file, 'r') as f:
            samples = json.load(f)
            all_samples.extend(samples.values())
    df = pd.DataFrame(all_samples)
    df.to_csv(output_csv, index=False)
    return df

# === Test ===
# [✓] Tested: 2024-07-10 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    print('Curating AK results')
    data_dir = r'D:\data\public-records\Alaska\AK Lab Result Data 2016-2024\AK Lab Result Data 2016-2024'
    output_dir = r'D:\data\alaska\results\datasets'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Walk the data directory and find all `.csv`'s with TestResult.
    test_datafiles = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if 'TestResult' in file:
                test_datafile = os.path.join(root, file)
                test_datafiles.append(test_datafile)
    
    # Get package datafiles.
    package_datafiles = [os.path.join(data_dir, x) for x in os.listdir(data_dir) if 'Package' in x and '.csv' in x]

    # Each sample has the following fields:
    sample_columns = {
        'PackageId': 'package_id',
        'PackageLabel': 'package_label',
        'LabTestResultId': 'sample_id',
        'TestingFacilityId': 'lab_id',
        'LabFacilityLicenseNumber': 'lab_license_number',
        'LabFacilityName': 'lab',
        'SourcePackageId': 'source_package_id',
        'SourcePackageLabel': 'source_package_label',
        'ProductName': 'product_name',
        'ProductCategoryName': 'product_type',
        'TestPerformedDate': 'date_tested',
        'OverallPassed': 'status',
        'IsRevoked': 'revoked',
        # 'RevokedDate': 'date_revoked',
    }
    package_columns = {
        'Id': 'id',
        'FacilityId': 'facility_id',
        'TagId': 'tag_id',
        'Label': 'label',
        'SourceHarvestNames': 'source_harvest_names',
        'SourcePackageLabels': 'source_package_labels',
        'SourceProcessingJobNumbers': 'source_processing_job_numbers',
        'SourceProcessingJobNames': 'source_processing_job_names',
        'MultiHarvest': 'multi_harvest',
        'MultiPackage': 'multi_package',
        'MultiProcessingJob': 'multi_processing_job',
        'Quantity': 'quantity',
        'UnitOfMeasureName': 'unit_of_measure_name',
        'UnitOfMeasureAbbreviation': 'unit_of_measure_abbreviation',
        'UnitOfMeasureQuantityType': 'unit_of_measure_quantity_type',
        'ItemFromFacilityId': 'item_from_facility_id',
        'ItemFromFacilityLicenseNumber': 'item_from_facility_license_number',
        'ItemFromFacilityName': 'item_from_facility_name',
        'ItemFromFacilityType': 'item_from_facility_type',
        'ItemFromFacilityIsActive': 'item_from_facility_is_active',
        'PackagedDate': 'packaged_date',
        'PackagedByFacilityId': 'packaged_by_facility_id',
        'PackagedByFacilityLicenseNumber': 'packaged_by_facility_license_number',
        'PackagedByFacilityName': 'packaged_by_facility_name',
        'PackagedByFacilityType': 'packaged_by_facility_type',
        'PackagedByFacilityIsActive': 'packaged_by_facility_is_active',
        'LabTestingStateName': 'lab_testing_state_name',
        'LabTestingStateDate': 'lab_testing_state_date',
        'IsProductionBatch': 'is_production_batch',
        'IsTradeSample': 'is_trade_sample',
        'IsProcessValidationTestingSample': 'is_process_validation_testing_sample',
        'IsProficiencyTestingSample': 'is_proficiency_testing_sample',
        'ProductRequiresRemediation': 'product_requires_remediation',
        'ContainsRemediatedProduct': 'contains_remediated_product',
        'ReceivedFromManifestNumber': 'received_from_manifest_number',
        'ReceivedFromFacilityId': 'received_from_facility_id',
        'ReceivedFromFacilityLicenseNumber': 'received_from_facility_license_number',
        'ReceivedFromFacilityName': 'received_from_facility_name',
        'ReceivedFromFacilityType': 'received_from_facility_type',
        'ReceivedFromFacilityActive': 'received_from_facility_active',
        'ReceivedDateTime': 'received_date_time',
        'IsArchived': 'is_archived',
        'IsFinished': 'is_finished',
        'FinishedDate': 'finished_date',
        'LabTestResultId': 'sample_id',
        'TestingFacilityId': 'lab_id',
        'TestingFacilityName': 'lab',
        'TestingFacilityLicenseNumber': 'lab_license_number',
        'TestingFacilityType': 'lab_facility_type',
        'TestingFacilityIsActive': 'lab_facility_is_active',
        'OverallPassed': 'status',
        'TestPerformedDate': 'date_tested',
        'ProductId': 'product_id',
        'ProductName': 'product_name',
        'ProductCategoryName': 'product_category_name',
        'ProductCategoryType': 'product_category_type',
        'ProductCategoryTypeName': 'product_category_type_name',
        'QuantityType': 'quantity_type',
        'QuantityTypeName': 'quantity_type_name',
        'ItemUnitOfMeasureName': 'item_unit_of_measure_name',
        'ItemUnitOfMeasureAbbreviation': 'item_unit_of_measure_abbreviation',
        'UnitQuantity': 'unit_quantity',
        'UnitQuantityUnitOfMeasureName': 'unit_quantity_unit_of_measure_name',
        'StrainId': 'strain_id',
        'StrainName': 'strain_name',
    }

    result_columns = {
        # 'LabTestResultDocumentFileId': 'coa_id',
        # 'ResultReleased': 'released',
        # 'ResultReleaseDateTime': 'date_released',
        # 'LabTestDetailId': 'result_id',
        # 'LabTestTypeId': 'test_id',
        'TestTypeName': 'name',
        'TestPassed': 'status',
        'TestResultLevel': 'value',
        # 'TestComment': 'comment',
        # 'TestInformationalOnly': 'r_and_d',
        # 'LabTestDetailIsRevoked': 'result_revoked',
        # 'LabTestDetailRevokedDate': 'date_result_revoked'
    }

    # Process each file and periodically save the results by year
    parser = CoADoc()
    all_samples_by_year = defaultdict(dict)
    file_counter = 0
    for file in test_datafiles:
        print(f'Processing file: {file}')
        samples = process_file(parser, file)

        # FIXME: JSON encode all results.


        # Merge samples into the all_samples_by_year dictionary
        for sample_id, sample in samples.items():
            year = sample['date_tested'][:4]
            if sample_id in all_samples_by_year[year]:
                all_samples_by_year[year][sample_id]['results'].extend(sample['results'])
            else:
                all_samples_by_year[year][sample_id] = sample
        
        # Periodically save the results to avoid memory issues
        file_counter += 1
        if file_counter % 5 == 0:
            for year, samples in all_samples_by_year.items():
                output_file = os.path.join(output_dir, f'ak-lab-results-{year}-{file_counter}.json')
                with open(output_file, 'w') as f:
                    json.dump(samples, f, indent=4)
            all_samples_by_year.clear()

    # Save any remaining samples
    if all_samples_by_year:
        for year, samples in all_samples_by_year.items():
            output_file = os.path.join(output_dir, f'ak-lab-results-{year}-final.json')
            with open(output_file, 'w') as f:
                json.dump(samples, f, indent=4)

    # TODO: Combine JSON by year.

    # FIXME: Aggregate all samples and save them to a .csv
    # output_dir = r'D:\data\alaska\results\datasets'
    # output_csv = r'D:\data\alaska\results\datasets\ak-lab-results-latest.csv'
    # results = aggregate_and_save_to_csv(output_dir, output_csv)

    # TODO: Augment package data?

    # # TODO: Augment license data.
    # datafile = os.path.join(data_dir, 'AK Facility.csv')
    # license_data = pd.read_csv(datafile)
