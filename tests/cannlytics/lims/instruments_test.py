"""
Test Instrument Data Collection | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 8/20/2021
Updated: 8/20/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports
from datetime import datetime, timedelta
import json
import os

# External imports
import pandas as pd

# Internal imports
import sys
sys.path.append('../../../')
from cannlytics.lims import instruments


def test_clean_column_names():
    """Test cleaning the column name of parsed DataFrame."""
    directory = r'../assets\data\instrument_data\agilent_gc_residual_solvents\sequence-1'
    filename = 'REPORT01.xls'
    data_file = os.path.join(directory, filename)
    workbook_data = pd.read_excel(data_file, sheet_name=None)
    compounds = instruments.get_compound_dataframe(workbook_data)
    compounds = instruments.clean_column_names(compounds, 'analyte')
    assert 'wildcard' in compounds.analyte.values
    return compounds


def test_get_compound_dataframe():
    """Test getting a sample's compound data."""
    directory = r'../assets\data\instrument_data\agilent_gc_residual_solvents\sequence-1'
    filename = 'REPORT01.xls'
    data_file = os.path.join(directory, filename)
    workbook_data = pd.read_excel(data_file, sheet_name=None)
    compounds = instruments.get_compound_dataframe(workbook_data)
    assert 'measurement' in compounds.columns
    return compounds


def test_get_sample_data():
    """Test getting a sample's data from a report."""
    directory = r'../assets\data\instrument_data\agilent_gc_residual_solvents\sequence-1'
    filename = 'REPORT01.xls'
    data_file = os.path.join(directory, filename)
    workbook_data = pd.read_excel(data_file, sheet_name=None)
    sample_data = instruments.get_sample_data(workbook_data)
    assert sample_data['sample_name'] == 'BLANK'
    return sample_data


def test_import_agilent_gc_residual_solvents():
    """Test parsing agilent GC residual solvent measurements."""
    directory = r'../assets\data\instrument_data\agilent_gc_residual_solvents\sequence-1'
    filename = 'REPORT01.xls'
    data_file = os.path.join(directory, filename)
    sample = instruments.import_results(data_file)
    assert sample['sample_name'] == 'BLANK'
    assert len(sample['results']) == 23
    return sample


def test_import_agilent_gc_terpenes():
    """ """
    directory = r'../assets\data\instrument_data\agilent_gc_terpenes\sequence-1'
    filename = 'REPORT01.xls'
    data_file = os.path.join(directory, filename)
    sample = instruments.import_results(data_file)
    assert sample['sample_name'] == 'CAL1'
    assert len(sample['results']) == 23
    return sample


def test_import_agilent_cannabinoids():
    """Test importing cannabinoids by Agilent HPLC."""
    directory = r'../assets\data\instrument_data\agilent_hplc_cannabinoids\sequence-1'
    filename = 'REPORT01.xls'
    data_file = os.path.join(directory, filename)
    sample = instruments.import_results(data_file)
    assert sample['sample_name'] == 'Cal 2'
    assert len(sample['results']) == 12
    return sample


def test_import_heavy_metals():
    """Test import heavy metal results."""
    directory = r'../assets\data\instrument_data\\icp_ms_heavy_metals\sequence-1'
    filename = 'Digestion Log 04202021 001.xlsx'
    data_file = os.path.join(directory, filename)
    samples = instruments.import_heavy_metals(data_file)
    assert len(samples) == 9
    return samples


def test_import_micro():
    """Test importing microbiological screening results."""
    directory = r'../assets\data\instrument_data\\qpcr_microbials\sequence-1'
    filename = 'Micro Test Data File.xlsx'
    data_file = os.path.join(directory, filename)
    samples = instruments.import_micro(data_file)
    assert len(samples) == 12
    return samples
    
if __name__ == '__main__':
    
    # Print out objects
    verbose = False
    
    # # Test supporting functions
    # sample_data = test_get_sample_data()
    # compound_data = test_get_compound_dataframe()
    # compound_data = test_clean_column_names()
    
    # # Test importing cannabinoids by Agilent HPLC.
    # cannabinoids_measurement = test_import_agilent_cannabinoids()
    # print('\nCannabinoid Measurement: ✓\n')
    # if verbose:
    #     print(json.dumps(cannabinoids_measurement, indent=4, sort_keys=True))
    
    # # Test importing terpenes by Agilent GC
    # terpenes_measurement = test_import_agilent_gc_terpenes()
    # print('\nTerpenes Measurement: ✓\n')
    # if verbose:
    #     print(json.dumps(terpenes_measurement, indent=4, sort_keys=True))
    
    # # Test importing residual solvents by Agilent GC
    # residual_solvents_measurement = test_import_agilent_gc_residual_solvents()
    # print('\nResidual Solvent Measurement: ✓\n')
    # if verbose:
    #     print(json.dumps(residual_solvents_measurement, indent=4, sort_keys=True))
    
    # # Test importing microbiological screening results.
    # micro_samples = test_import_micro()
    # print('\nMicrobe Measurements: ✓\n')
    # if verbose:
    #     print(json.dumps(micro_samples, indent=4, sort_keys=True))
    
    # Test import heavy metal results.
    heavy_metal_samples = test_import_heavy_metals()
    print('\nHeavy Metal Measurements: ✓\n')
    if verbose:
        print(json.dumps(heavy_metal_samples, indent=4, sort_keys=True))
    
    # Test automatic collection
    # org_id = 'test-company'
    # last_modified_at = datetime.now() - timedelta(minutes=60)
    # instruments.automatic_collection(org_id, last_modified_at, env_file='../../../.env')
