"""
Data Collection | Cannlytics
Authors:
  Keegan Skeate <keegan@cannlytics.com>
  Charles Rice <charles@ufosoftwarellc.com>
Created: 6/15/2021
Updated: 6/15/2021
"""


def get_sample_name(df):

    import pandas as pd

    # convert the first column of the first sheet to lowercase
    df['Sheet1'].ObjClass = df['Sheet1'].ObjClass.str.lower()

    # put the samplename key and samplename value into a dictionary
    samples = dict(df['Sheet1'][df['Sheet1'].ObjClass == 'samplename'].values)

    return samples


def get_compound_df(df):

    import pandas as pd

   # rename the columns in the Compound sheet to match the required names
    df['Compound'].rename(columns = {'Name':'analyte', 'Amount':'measurement'}, inplace = True)

    # for simplicty make a copy of the Compound sheet
    df_compound = df['Compound'].copy()

    # handle NaN values
    df_compound.loc[(df_compound.analyte.isnull()) & (df_compound.measurement > 0), 'analyte'] = 'wildcard'
    df_compound.dropna(subset = ['analyte'], inplace = True)

    return df_compound

def clean_special_characters(df, column_name):
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

    import pandas as pd

    #read in all the excel sheets at one time
    df = pd.read_excel(file_name, sheet_name = None)

    # get the sample name
    samples = get_sample_name(df)

    # get and cleanup the compound df from the compound sheet
    df_compound = get_compound_df(df)

    # add the analyte names and measurements to an array of dictionaries and add that to the main array
    samples['metrics'] = df_compound[['analyte', 'measurement']].to_dict('records')

    return samples


def import_agilent_gc_terpenes(file_name):

    import pandas as pd

    #read in all the excel sheets at one time
    df = pd.read_excel(file_name, sheet_name = None)

    # get the sample name
    samples = get_sample_name(df)

    # get and cleanup the compound df from the compound sheet
    df_compound = get_compound_df(df)

    # replace special characters
    df_compound = clean_special_characters(df_compound, 'analyte')

    # add the analyte names and measurements to an array of dictionaries and add that to the main array
    samples['metrics'] = df_compound[['analyte', 'measurement']].to_dict('records')

    return samples

# This is the same as residual solvents, added the function in case it needs to be customized
def import_agilent_cannbinoids(file_name):
    return import_agilent_gc_residual_solvments(file_name)

print(import_agilent_cannbinoids('/Users/alienfoo/Documents/DataSets/cannlytics/cannlytics/lims/cannabinoid.xls'))