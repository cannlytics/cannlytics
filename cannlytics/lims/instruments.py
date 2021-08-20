"""
Instruments | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 8/3/2021  
Updated: 8/3/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Manage scientific instruments and measurements from the instruments.
"""
# Standard imports
import os
import environ

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


def automatic_collection(org_id, env_file='.env'):
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
        db = initialize_firebase()
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

    # Iterate over instruments, collecting measurements.
    measurements = []
    for instrument in instruments:

        # Identify the analysis being run.
        analysis = instrument['analysis']

        # Get the analytes.
        try:
            ref = f'organizations/{org_id}/analytes'
            analytes = get_collection(ref, filters=[{
                'key': 'analysis', 'operation': '==', 'value': analysis
            }])
        except:
            url = f'{API_BASE}/analytes?organization_id={org_id}&analysis={analysis}'
            analytes = requests.get(url, headers=headers)

        # TODO: Search for recently modified files in the instrument directory.
        # files = sorted([os.path.join(root,f) for root,_,the_files in os.walk(path) for f in the_files if f.lower().endswith(".cpp")], key=os.path.getctime, reverse = True)
        directory = instrument['data_path']
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.xlsx'):
                    data_file = os.path.join(root, filename)

                # TODO: Read in modified file and parse it according to
                # the instrument type and analytes.
                # TODO: Use routines Charles wrote in data.py


    # Upload data to Firestore.
    for measurement in measurements:
        measurement_id = measurement['measurement_id']
        ref = f'organizations/{org_id}/measurements/{measurement_id}'
        update_document(ref, measurement)
    
    # Return the measurements
    return measurements


#-----------------------------------------------------------------------
# FIXME: Test and touch up
#-----------------------------------------------------------------------

def clean_column_names(df, column):
    """
    Args:
        df (DataFrame): A DataFrame with any column names.
    Returns:
        (DataFrame): A DataFrame with snake_case column names.
    """
    df[column] = df[column].str.strip()
    df[column] = df[column].str.rstrip('.)]')
    df[column] = df[column].str.replace('%',  'percent', regex=True)
    df[column] = df[column].str.replace('#',  'number', regex=True)
    df[column] = df[column].str.replace('[/,-]',  '_', regex=True)
    df[column] = df[column].str.replace('[.,(,)]',  '', regex=True)
    df[column] = df[column].str.replace("\'",'', regex=True)
    df[column] = df[column].str.replace("[[]",  '_', regex=True)
    df[column] = df[column].str.replace(r"[]]",  '', regex=True)
    df[column] = df[column].str.replace(' ',  '_', regex=True)
    df[column] = df[column].str.replace('β',  'beta', regex=True)
    df[column] = df[column].str.replace('Δ',  'delta', regex=True)
    df[column] = df[column].str.replace('δ',  'delta', regex=True)
    df[column] = df[column].str.replace('α',  'alpha', regex=True)
    df[column] = df[column].str.replace('__',  '', regex=True)
    df[column] = df[column].str.lower()
    return df


def get_compound_dataframe(df, sheetname='Compound'):
    """ Rename the columns in the `Compound` sheet to match the required
    names. For simplicity, make a copy of the `Compound` sheet to
    handle NaN values.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (DataFrame): A DataFrame with renamed compounds.
    """
    columns = {
        'Name':'analyte',
        'Amount': 'measurement',
    }
    df[sheetname].rename(columns=columns, inplace=True)
    compounds = df[sheetname].copy()
    criterion = (compounds.analyte.isnull()) & (compounds.measurement > 0)
    compounds.loc[criterion, 'analyte'] = 'wildcard'
    compounds.dropna(subset=['analyte'], inplace=True)
    return compounds


def get_sample_name(df, sheetname='Sheet1', var='samplename'):
    """Return the sample name from a dictionary.
    Converts the first column of the first sheet to lowercase.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): The sample name as a key, value pair.
    """
    df[sheetname].ObjClass = df[sheetname].ObjClass.str.lower()
    samples = dict(df[sheetname][df[sheetname].ObjClass == var].values)
    return samples



def import_agilent_gc_residual_solvents(file_name):
    """Read in all the excel sheets at one time, get the sample name,
    get and cleanup the compound df from the compound sheet,
    add the analyte names and measurements to an array of dictionaries,
    and add that to the main array.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): A dictionary of sample results.
    """
    df = pd.read_excel(file_name, sheet_name = None)
    samples = get_sample_name(df)
    compounds = get_compound_dataframe(df)
    samples['metrics'] = compounds[['analyte', 'measurement']].to_dict('records')
    return samples


def import_agilent_gc_terpenes(file_name):
    """Read in all the excel sheets at one time, get the sample name,
    get and cleanup the compound df from the compound sheet,
    replace special characters, add the analyte names and measurements
    to an array of dictionaries, and add that to the main array.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (list): A list of measurements (dict).
    """
    df = pd.read_excel(file_name, sheet_name = None)
    samples = get_sample_name(df)
    compounds = get_compound_dataframe(df)
    compounds = clean_column_names(compounds, 'analyte')
    samples['metrics'] = compounds[['analyte', 'measurement']].to_dict('records')
    return samples


def import_agilent_cannabinoids(file_name):
    """This is the same as residual solvents routine.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): A dictionary of sample results.
    """
    return import_agilent_gc_residual_solvents(file_name)


def import_heavy_metals(file_name):
    """
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (list): A list of measurements (dict).
    """

    # Read in the log sheet and summary sheets seperately to parsing easier.
    log_df = pd.read_excel(file_name, sheet_name = 'Log')
    summary_df = pd.read_excel(file_name, sheet_name = 'Quant Summary')

    # Drop the rows that do not contain sample ids.
    log_df.dropna(subset = ['Sample Mass (g)'], inplace = True)

    # Rename columns to make parsing clearer.
    summary_df.rename(columns = {'Analysis':'analyte','-':'mass'}, inplace = True)

    # Get list of samples.
    sample_ids = log_df['Sample ID'].tolist()

    # Parse measurements.
    samples = []
    measurements = {}
    for sample_id in sample_ids:
        sample = {}
        sample['sample_id'] = sample_id
        sample['sample_mass'] = log_df[log_df['Sample ID'] == sample_id]['Sample Mass (g)'].values[0]
        sample['sample_dilution'] = log_df[log_df['Sample ID'] == sample_id]['Sample Dilution'].values[0]

        analytes = []
        measurements['measurements'] = analytes
        index  = summary_df.index[(summary_df['analyte'] == 'ID:') & (summary_df['mass'] == sample_id)].tolist()
        for offset in range(index[0] + 20, index[0] + 27):
            analyte = {}
            analyte['analyte'] = summary_df.iloc[offset].analyte
            analyte['measurement'] = summary_df.iloc[offset+9].mass
            analytes.append(analyte)

        samples.append(sample)
        samples.append(measurements)

    return samples


#-----------------------------------------------------------------------
# SCRAP
#-----------------------------------------------------------------------

# TODO: Automatic data collection cron Job!
# Resources:
#     https://www.programmersought.com/article/6548119734/
#     https://code.tutsplus.com/tutorials/managing-cron-jobs-using-python--cms-28231
#     https://stackoverflow.com/questions/34598568/how-to-schedule-a-python-script-using-cron-job
#     https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder
#     https://www.w3resource.com/python-exercises/python-basic-exercise-64.php
#     https://stackabuse.com/scheduling-jobs-with-python-crontab
# def automated_data_collection():
#     """CRON job to periodically collect data from scientific instruments."""
    
#     print('Getting data from instruments....')

#     return NotImplementedError
