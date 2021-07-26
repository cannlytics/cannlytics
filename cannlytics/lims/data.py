"""
Data Collection | Cannlytics

Authors:  
  Keegan Skeate <keegan@cannlytics.com>  
  Charles Rice <charles@ufosoftwarellc.com>  
Created: 6/15/2021  
Updated: 7/15/2021  

Resources:
    https://www.programmersought.com/article/6548119734/
    https://code.tutsplus.com/tutorials/managing-cron-jobs-using-python--cms-28231
    https://stackoverflow.com/questions/34598568/how-to-schedule-a-python-script-using-cron-job
    https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder
    https://www.w3resource.com/python-exercises/python-basic-exercise-64.php
    https://stackabuse.com/scheduling-jobs-with-python-crontab
"""
try:

    # External imports
    import pandas as pd
    import xlwings

    # Internal imports
    from cannlytics.utils.utils import snake_case
    from cannlytics.firebase import update_document

except:
    pass # FIXME: Docs can't import.


def import_data_model(directory):
    """Import analyses to Firestore from a .csv or .xlsx file.
    Args:
        filename (str): The full filename of a data file.
    """
    analyses = pd.read_excel(directory + 'analyses.xlsx')
    analytes = pd.read_excel(directory + 'analytes.xlsx')
    for index, analysis in analyses.iterrows():
        analyte_data = []
        analyte_names = analysis.analyte_keys.split(', ')
        for analyte_key in analyte_names:
            analyte_item = analytes.loc[analytes.key == analyte_key]
            analyte_data.append(analyte_item.to_dict(orient='records'))
        analyses.at[index, 'analytes'] = analyte_data 
    analyses_data = analyses.to_dict(orient='records')
    for index, values in analyses_data.iterrows():
        doc_id = str(values.key)
        doc_data = values.to_dict()
        ref = ''
        update_document(ref, doc_data)
        # doc_data = data.to_dict(orient='index')
        # data_ref = create_reference(db, ref)
        # data_ref.document(doc_id).set(doc_data, merge=True)
        # data_ref.set(doc_data, merge=True)

    return NotImplementedError


def import_measurements():
    """Import measurements taken by scientific instruments.
    Args:

    Returns:
    """

    print('Receive a transfer...')


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
    """ Rename the columns in the Compound sheet to match the required
    names. For simplicity, make a copy of the Compound sheet to
    handle NaN values.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    columns = {'Name':'analyte', 'Amount': 'measurement'}
    df['Compound'].rename(columns=columns, inplace=True)
    df_compound = df['Compound'].copy()
    df_compound.loc[(df_compound.analyte.isnull()) & (df_compound.measurement > 0), 'analyte'] = 'wildcard'
    df_compound.dropna(subset = ['analyte'], inplace=True)
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


def import_agilent_gc_residual_solvents(file_name):
    """Read in all the excel sheets at one time, get the sample name,
    get and cleanup the compound df from the compound sheet,
    add the analyte names and measurements to an array of dictionaries,
    and add that to the main array.
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
    """Read in all the excel sheets at one time, get the sample name,
    get and cleanup the compound df from the compound sheet,
    replace special characters, add the analyte names and measurements
    to an array of dictionaries, and add that to the main array.
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


def import_agilent_cannabinoids(file_name):
    """This is the same as residual solvents routine.
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
    """
    return import_agilent_gc_residual_solvents(file_name)


def import_heavy_metals(file_name):
    """
    Args:
        df (DataFrame): A DataFrame.
    Returns:
        (dict): 
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


#-----------------------------------------------------------------------
# Helper functions
#-----------------------------------------------------------------------

def import_worksheet(filename, sheetname, range_start='A1'):
    """Read the data from a given worksheet.
    Args:
        filename (str): The name of the Excel file to read.
        range_start (str): Optional starting cell.
    Returns:
        list(dict): A list of dictionaries.
    """
    app = xlwings.App(visible=False)
    book = xlwings.Book(filename)
    sheet = book.sheets(sheetname)
    excel_data = sheet.range(range_start).expand('table').value
    keys = [snake_case(key) for key in excel_data[0]]
    data = [dict(zip(keys, values)) for values in excel_data[1:]]
    book.close()
    app.quit()
    return data
