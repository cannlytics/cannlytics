"""
Instruments | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 8/3/2021  
Updated: 8/20/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Manage scientific instruments and measurements from the instruments.
"""
# Standard imports
import os
import environ
from datetime import datetime, timedelta

try:

    # External imports
    import pandas as pd
    import requests

    # Internal imports
    from cannlytics.firebase import (
        get_collection,
        initialize_firebase,
        update_document
    )
    from cannlytics.utils.utils import snake_case

except:
    pass

API_BASE = 'https://console.cannlytics.com'


def automatic_collection(org_id, last_modified_at, env_file='.env'):
    """Automatically collect results from scientific instruments.
    Args:
        org_id (str): The organization ID to associate with instrument results.
        env_file (str): The environment variable file, `.env` by default.
            Either a `GOOGLE_APPLICATION_CREDENTIALS` or a
            `CANNLYTICS_API_KEY` is needed to run the routine.
    Returns
        (list): A list of measurements (dict) that were collected.
    """

    # Initialize Firebase or use an API key.
    try:
        env = environ.Env()
        env.read_env(env_file)
        credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
        initialize_firebase()
    except:
        api_key = env('CANNLYTICS_API_KEY')
        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-type': 'application/json',
        }

    # Get the instruments, trying Firestore, then the API.
    try:
        ref = f'organizations/{org_id}/instruments'
        instruments = get_collection(ref)
    except:
        url = f'{API_BASE}/instruments?organization_id={org_id}'
        instruments = requests.get(url, headers=headers)
    print('INSTRUMENTS:', instruments)

    # Iterate over instruments, collecting measurements.
    measurements = []
    for instrument in instruments:

        # Identify the analysis being run and identify the import routine.
        analysis = instrument['analysis']
        if 'micro' in analysis:
            import_method = locals()['import_micro']
        elif 'metal' in analysis:
            import_method = locals()['import_heavy_metals']
        else:
            import_method = locals()['import_results']

        # Search for recently modified files in the instrument directory
        # and parse any recently modified file.
        directory = instrument['data_path']
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.xlsx'):
                    data_file = os.path.join(root, filename)
                    modifed_at = os.stat(data_file).st_mtime
                    if modifed_at >= last_modified_at:
                        samples = import_method(data_file)
                        if isinstance(samples, dict):
                            measurements.append(samples)
                        else:
                            measurements = [*measurements, *samples]
    print('Found all measurements:', measurements)

    # Upload data to Firestore.
    for measurement in measurements:
        measurement_id = measurement.get('acq_inj_time')
        if not measurement_id:
            measurement_id = str(int(datetime.now().timestamp()))
        ref = f'organizations/{org_id}/measurements/{measurement_id}'
        update_document(ref, measurement)
    
    # Return the measurements
    return measurements


def clean_column_names(df, column):
    """
    Args:
        df (DataFrame): A DataFrame with any column names.
        column (str): The column of the DataFrame to clean.
    Returns:
        (DataFrame): A DataFrame with snake_case column names.
    """
    df[column] = df[column].str.strip()
    df[column] = df[column].str.rstrip('.)]')
    df[column] = df[column].str.replace('%', 'percent', regex=True)
    df[column] = df[column].str.replace('#', 'number', regex=True)
    df[column] = df[column].str.replace('[/,]', '_', regex=True)
    df[column] = df[column].str.replace('[.,(,)]', '', regex=True)
    df[column] = df[column].str.replace("\'", '', regex=True)
    df[column] = df[column].str.replace("[[]", '_', regex=True)
    df[column] = df[column].str.replace(r"[]]", '', regex=True)
    df[column] = df[column].str.replace('β', 'beta', regex=True)
    df[column] = df[column].str.replace('Δ', 'delta', regex=True)
    df[column] = df[column].str.replace('δ', 'delta', regex=True)
    df[column] = df[column].str.replace('α', 'alpha', regex=True)
    df[column] = df[column].str.replace('__', '', regex=True)
    return df


def get_compound_dataframe(workbook_data, sheetname='Compound'):
    """ Rename the columns in the `Compound` sheet to match the required
    names. For simplicity, make a copy of the `Compound` sheet to
    handle NaN values.
    Args:
        workbook_data (dict): A dictionary of worksheet DataFrames.
        sheetname (str): The worksheet that contains the compound data.
    Returns:
        (DataFrame): A DataFrame with renamed compounds.
    """
    columns = {
        'Name':'analyte',
        'Amount': 'measurement',
        'AmtPerResp': 'amount_per_response'
    }
    workbook_data[sheetname].rename(columns=columns, inplace=True)
    compounds = workbook_data[sheetname].copy()
    criterion = (compounds.analyte.isnull()) & (compounds.measurement > 0)
    compounds.loc[criterion, 'analyte'] = 'wildcard'
    compounds.dropna(subset=['analyte'], inplace=True)
    return compounds


def get_sample_data(workbook_data, sheet_name='Sheet1'):
    """Return the sample name from a dictionary.
    Converts the first column of the first sheet to snake_case.
    Args:
        df (DataFrame): A DataFrame.
        sheet_name (str): The name of the worksheet containing the sample data.
    Returns:
        (dict): The sample data as a key and value pairs.
    """
    data = workbook_data[sheet_name]
    data['ObjClass'] = data['ObjClass'].apply(snake_case)
    return dict(data.values)


def import_heavy_metals(file_name):
    """Import heavy metal results from ICP-MS screening.
    First, reads in the log sheet and summary sheets seperately to
    make parsing easier. Drops the rows that do not contain sample ids.
    Renames columns to make parsing clearer. Get list of samples and
    then parses measurements.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (list): A list of measurements (dict).
    """
    results_data = pd.read_excel(file_name, sheet_name='Log')
    samples_data = pd.read_excel(file_name, sheet_name='Quant Summary')
    results_data.dropna(subset = ['Sample Mass (g)'], inplace=True)
    samples_data.rename(columns = {'Analysis':'analyte', '-': 'mass'}, inplace=True)
    sample_ids = results_data['Sample ID'].tolist()
    samples = []
    for sample_id in sample_ids:
        sample = {}
        result_data = results_data[results_data['Sample ID'] == sample_id]
        sample['sample_id'] = sample_id
        sample['sample_mass'] = result_data['Sample Mass (g)'].values[0]
        sample['sample_dilution'] = result_data['Sample Dilution'].values[0]
        analytes = []
        criterion = (samples_data['analyte'] == 'ID:') & (samples_data['mass'] == sample_id)
        index  = samples_data.index[criterion].tolist()
        for offset in range(index[0] + 20, index[0] + 27): # Magic numbers
            analyte = {}
            analyte['analyte'] = samples_data.iloc[offset].analyte
            analyte['measurement'] = samples_data.iloc[offset + 9].mass # Magic number
            analytes.append(analyte)
        sample['results'] = analytes
        samples.append(sample)
    return samples


def import_micro(file_name):
    """Import microbiological screening results, grouping sample results
    by well name.
    Args:
        file_name (str): The path to a qPCR data file.
    Returns:
        (list): A list of sample measurements (dictionary).
    """
    workbook_data = pd.read_excel(file_name, sheet_name=None)
    results = workbook_data['Tabular Results']
    sample_names = results['Well Name'].unique()
    columns = {
        'Dye': 'method',
        'Target': 'analyte',
        'Cq (∆R)': 'measurement',
        'Well': 'well',
        'Well Name': 'well_name',
    }
    results.rename(columns=columns, inplace=True)
    samples = []
    for sample_name in sample_names:
        sample = {'sample_name': sample_name}
        sample_data = results.loc[results['well_name'] == sample_name]
        fields = list(columns.values())
        sample['results'] = sample_data[fields].to_dict('records')
        samples.append(sample)
    return samples


def import_results(file_name, vendor='agilent', instrument='hplc'):
    """Import scientific instrument data. The routine is as follows:
        1. Read in all the excel sheets at one time.
        2. Get the sample name.
        3. Get and tidy the compound data from the compound sheet.
        4. Add the analyte names and measurements to a list of result dictionaries.
        5. Collect the data into a running list.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): A dictionary of sample results.
    """
    workbook_data = pd.read_excel(file_name, sheet_name=None)
    sample = get_sample_data(workbook_data)
    compounds = get_compound_dataframe(workbook_data)
    compounds = clean_column_names(compounds, 'analyte')
    columns = ['analyte', 'measurement', 'amount_per_response']
    sample['results'] = compounds[columns].to_dict('records')
    return sample


if __name__ == '__main__':

    import argparse

    # Declare command line arguments.
    # Get Cannlytics User API Key from .env file and specify the organization.
    parser = argparse.ArgumentParser(description='Scientific instrument data collection routine.')
    parser.add_argument('--env', action='store', dest='env_file', default=['.env'])
    parser.add_argument('--modified', action='store', dest='last_modified', default=[60])
    parser.add_argument('--org', action='store', dest='org_id', default=[''])
    args = parser.parse_args()

    # Specify the last modified time cut-off.
    last_modified_at = datetime.now() - timedelta(minutes=args.last_modified)

    # Collect data.
    automatic_collection(args.org_id, last_modified_at, env_file=args.env_file)


#-----------------------------------------------------------------------
# DRAFT
#-----------------------------------------------------------------------

from crontab import CronTab

def schedule_automatic_collection():
    """Schedule an automatic collection CRON job."""
    my_cron = CronTab(tab="""*/1 * * * * python test_cron.py""")
    # job = my_cron.new(command='python /home/roy/writeDate.py')
    # job.minute.every(1)
    my_cron.write()
