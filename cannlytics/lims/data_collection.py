"""
Data Collection | Cannlytics
Authors:
  Keegan Skeate <keegan@cannlytics.com>
  Charles Rice <charles@ufosoftwarellc.com>
Created: 6/15/2021
Updated: 6/19/2021
"""

import pandas as pd


def get_sample_name(df):
    """Return the sample name from a dictionary.
    Converts the first column of the first sheet to lowercase.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): The sample name as a key, value pair.
    """
    df['Sheet1'].ObjClass = df['Sheet1'].ObjClass.str.lower()
    samples = dict(df['Sheet1'][df['Sheet1'].ObjClass == 'samplename'].values)
    return samples


def get_compound_df(df):
    """ rename the columns in the Compound sheet to match the required names
    for simplicty make a copy of the Compound sheet
    handle NaN values
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    df['Compound'].rename(columns = {'Name':'analyte', 'Amount':'measurement'}, inplace = True)
    df_compound = df['Compound'].copy()
    df_compound.loc[(df_compound.analyte.isnull()) & (df_compound.measurement > 0), 'analyte'] = 'wildcard'
    df_compound.dropna(subset = ['analyte'], inplace = True)
    return df_compound


def clean_special_characters(df, column_name):
    """
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    df[column_name] = df[column_name].str.strip()
    df[column_name] = df[column_name].str.rstrip('.)]')
    df[column_name] = df[column_name].str.replace('%',  'percent', regex=True)
    df[column_name] = df[column_name].str.replace('#',  'number', regex=True)
    df[column_name] = df[column_name].str.replace('[/,-]',  '_', regex=True)
    df[column_name] = df[column_name].str.replace('[.,(,)]',  '', regex=True)
    df[column_name] = df[column_name].str.replace("\'",'', regex=True)
    df[column_name] = df[column_name].str.replace("[[]",  '_', regex=True)
    df[column_name] = df[column_name].str.replace(r"[]]",  '', regex=True)
    df[column_name] = df[column_name].str.replace(' ',  '_', regex=True)
    df[column_name] = df[column_name].str.replace('β',  'beta', regex=True)
    df[column_name] = df[column_name].str.replace('Δ',  'delta', regex=True)
    df[column_name] = df[column_name].str.replace('δ',  'delta', regex=True)
    df[column_name] = df[column_name].str.replace('α',  'alpha', regex=True)
    df[column_name] = df[column_name].str.replace('__',  '', regex=True)
    df[column_name] = df[column_name].str.lower()
    return df


def import_agilent_gc_residual_solvments(file_name):
    """read in all the excel sheets at one time
    get the sample name
    get and cleanup the compound df from the compound sheet
    add the analyte names and measurements to an array of dictionaries and add that to the main array
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    df = pd.read_excel(file_name, sheet_name = None)
    samples = get_sample_name(df)
    df_compound = get_compound_df(df)
    samples['metrics'] = df_compound[['analyte', 'measurement']].to_dict('records')
    return samples


def import_agilent_gc_terpenes(file_name):
    """read in all the excel sheets at one time
    get the sample name
    get and cleanup the compound df from the compound sheet
    replace special characters
    add the analyte names and measurements to an array of dictionaries and add that to the main array
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    df = pd.read_excel(file_name, sheet_name = None)
    samples = get_sample_name(df)
    df_compound = get_compound_df(df)
    df_compound = clean_special_characters(df_compound, 'analyte')
    samples['metrics'] = df_compound[['analyte', 'measurement']].to_dict('records')
    return samples


def import_agilent_cannbinoids(file_name):
    """This is the same as residual solvents, added the function
    in case it needs to be customized.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    return import_agilent_gc_residual_solvments(file_name)


def import_metals(file_name):
    """
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """

    # read in the log sheet and summary sheets seperately to parsing easier
    log_df = pd.read_excel(file_name, sheet_name = 'Log')
    summary_df = pd.read_excel(file_name, sheet_name = 'Quant Summary')

    # drop the rows that do not contain sample ids
    log_df.dropna(subset = ['Sample Mass (g)'], inplace = True)

    # rename columns to make parsing clearer
    summary_df.rename(columns = {'Analysis':'analyte','-':'mass'}, inplace = True)

    # get list of samples
    sample_ids = log_df['Sample ID'].tolist()

    # Parse measurements.
    samples = []
    measurements = {}
    for sample_id in sample_ids:
        sample = {}
        sample[ 'sample_id' ] = sample_id
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
