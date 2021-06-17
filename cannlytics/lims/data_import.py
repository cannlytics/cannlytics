"""
Data Import | Cannlytics
Authors:
  Keegan Skeate <keegan@cannlytics.com>
Created: 6/16/2021
Updated: 6/16/2021
TODO:
    - Import model fields from organization's settings in Firestore so
    the user can upload custom data points.
"""
import pandas as pd
from cannlytics.firebase import update_document


def import_analyses(directory):
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
        update_document(, doc_data)
        # doc_data = data.to_dict(orient='index')
        # data_ref = create_reference(db, ref)
        # data_ref.document(doc_id).set(doc_data, merge=True)
        # data_ref.set(doc_data, merge=True)

    return NotImplementedError


def import_analytes():
    """Import analytes to Firestore from a .csv or .xlsx file.
    Args:
        filename (str): The full filename of a data file.
    """

    return NotImplementedError


def import_instruments():
    """Import instruments to Firestore from a .csv or .xlsx file.
    Args:
        filename (str): The full filename of a data file.
    """

    return NotImplementedError
