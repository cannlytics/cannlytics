"""
Get Cannabis Data for Connecticut
Copyright (c) 2021 Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 9/16/2021
Updated: 9/18/2021
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>

Data Sources:
    Connecticut Medical Marijuana Brand Registry: https://data.ct.gov/Health-and-Human-Services/Medical-Marijuana-Brand-Registry/egd5-wb6r/data
    Connecticut Socrata Open Data API: https://dev.socrata.com/foundry/data.ct.gov/egd5-wb6r
"""
# Standard imports
import os

# External imports
import sys
sys.path.append('../../../../')
from cannlytics.firebase import initialize_firebase, update_document
import pandas as pd
from sodapy import Socrata


CANNABINOIDS = {
    'tetrahydrocannabinol_thc': 'thc',
    'tetrahydrocannabinol_acid_thca': 'thca',
    'cannabidiols_cbd': 'cbd',
    'cannabidiol_acid_cbda': 'cbda',
    'cbg': 'cbg',
    'cbg_a': 'cbga',
    'cannabavarin_cbdv': 'cbdv',
    'cannabichromene_cbc': 'cbc',
    'cannbinol_cbn': 'cbn',
    'tetrahydrocannabivarin_thcv': 'thcv',
}

TERPENES = {
    'a_pinene': 'a_pinene',
    'b_myrcene': 'b_myrcene',
    'b_caryophyllene': 'b_caryophyllene',
    'b_pinene': 'b_pinene',
    'limonene': 'limonene',
    'ocimene': 'ocimene',
    'linalool_lin': 'linalool',
    'humulene_hum': 'humulene',
    'b_eudesmol': 'b_eudesmol',
    'fenchone': 'fenchone',
    'camphor': 'camphor',
    'a_bisabolol': 'a_bisabolol',
    'a_phellandrene': 'a_phellandrene',
    'a_terpinene': 'a_terpinene',
    'b_terpinene': 'b_terpinene',
    'pulegol': 'pulegol',
    'borneol': 'borneol',
    'isopulegol': 'isopulegol',
    'carene': 'carene',
    'camphene': 'camphene',
    'caryophyllene_oxide': 'caryophyllene_oxide',
    'cedrol': 'cedrol',
    'eucalyptol': 'eucalyptol',
    'geraniol': 'geraniol',
    'guaiol': 'guaiol',
    'geranyl_acetate': 'geranyl_acetate',
    'isoborneol': 'isoborneol',
    'menthol': 'menthol',
    'l_fenchone': 'l_fenchone',
    'nerol': 'nerol',
    'sabinene': 'sabinene',
    'terpineol': 'terpineol',
    'terpinolene': 'terpinolene',
    'trans_b_farnesene': 'trans_b_farnesene',
    'valencene': 'valencene',
    'a_cedrene': 'a_cedrene',
    'a_farnesene': 'a_farnesene',
    'b_farnesene': 'b_farnesene',
    'cis_nerolidol': 'cis_nerolidol',
    'fenchol': 'fenchol',
    'trans_nerolidol': 'trans_nerolidol',
}

STANDARD_COLUMNS = {
    'analyte': 'analyte',
    'concentration': 'concentration',
    'brand_name': 'sample_name',
    'dosage_form': 'sample_type',
    'producer': 'organization',
    'registration_number': 'sample_id',
    'approval_date': 'tested_at',
}


def get_column_dict_value(df, column, key):
    """Return a column's dictionary values as a column. Handles missing values.
    Args:
        df (DataFrame): A DataFrame that contains a column with dictionary values.
        column (str): The column name that contains the dictionary.
        key (str): The key of the dictionary to return.
    Returns:
        (Series): A series of dictionary values from the column.
    """
    df[column] = df[column].fillna({i: {} for i in df.index})
    subdata = pd.json_normalize(df[column])
    return subdata[key]


def get_data_ct():
    """Get public cannabis data for Connecticut.
    Returns
        stats (dict): A dictionary of state statistics.
    """

    #-------------------------------------------------------------------
    # Get the data.
    #-------------------------------------------------------------------

    # Get the cannabinoid data.
    app_token = os.environ.get('APP_TOKEN', None)
    client = Socrata('data.ct.gov', app_token)
    response = client.get('egd5-wb6r', limit=15000)
    data = pd.DataFrame.from_records(response)

    # Convert values to floats, coding suspected non-detects as 0.
    for analyte in list(TERPENES.keys()) + list(CANNABINOIDS.keys()):
        data[analyte] = data[analyte].str.replace('<0.10', '0.0', regex=False)
        data[analyte] = data[analyte].str.replace('<0.1', '0.0', regex=False)
        data[analyte] = data[analyte].str.replace('<0.29', '0.0', regex=False)
        data[analyte] = data[analyte].str.replace('%', '', regex=False)
        data[analyte] = data[analyte].str.replace('-', '0.0', regex=False)
        data[analyte] = pd.to_numeric(data[analyte], errors='coerce').fillna(0.0)

    # Calculate total terpenes and total cannabinoids.
    data['total_terpenes'] = data[list(TERPENES.keys())].sum(axis=1)
    data['total_cannabinoids'] = data[list(CANNABINOIDS.keys())].sum(axis=1)

    # Clean organization name.
    data['organization'] = data['producer'].str.title().str.replace('Llc', 'LLC')

    # Rename certain columns, including analytes, for standardization.
    columns = {**STANDARD_COLUMNS, **CANNABINOIDS, **TERPENES}
    data = data.rename(columns, axis=1)

    # Get the CoA URL from the lab_analysis column.
    data['coa_url'] = get_column_dict_value(data, 'lab_analysis', 'url')

    # Get the sample image from the product_image column.
    data['image_url'] = get_column_dict_value(data, 'product_image', 'url')

    # Get the label image from the product_image column.
    data['label_url'] = get_column_dict_value(data, 'label_image', 'url')

    # Remove duplicate data.
    data.drop(['lab_analysis', 'product_image', 'label_image'], axis=1, inplace=True)

    #-------------------------------------------------------------------
    # Calculate terpene prevalence.
    #-------------------------------------------------------------------

    # Calculate the prevalence (percent of samples that contains) of each terpene.
    # Also, calculate the average for each terpene when the terpene is present.
    prevalence = {}
    analytes = pd.DataFrame(columns=STANDARD_COLUMNS.values())
    for analyte in list(TERPENES.values()):
        analyte_present_data = data.loc[data[analyte] > 0].copy(deep=True)
        prevalence[analyte] = len(analyte_present_data) / len(data)
        analyte_present_data['analyte'] = analyte
        analyte_present_data['concentration'] = analyte_present_data[analyte]
        subset = analyte_present_data[list(STANDARD_COLUMNS.values())]
        # subset = subset.rename(STANDARD_COLUMNS, axis=1)
        analytes = analytes.append(subset)

    # Create a DataFrame with statistics for each analyte.
    prevalence_stats = pd.DataFrame(
        prevalence.items(),
        columns=['analyte', 'prevalence'],
        index=prevalence.keys()
    )

    # Sort the data by the most prevelant terpene.
    prevalence_stats = prevalence_stats.sort_values('prevalence', ascending=False)
    prevalence_stats = prevalence_stats.to_dict(orient='records')

    # Add analyte name.
    analytes = []
    for item in prevalence_stats:
        item['name'] = item['analyte'] \
            .replace('_', ' ') \
            .replace(' lin', '') \
            .replace(' hum', '') \
            .title() \
            .replace('B ', 'β-') \
            .replace('A ', 'α-') \
            .replace('Trans ', 'trans-') \
            .replace('Cis ', 'cis-')
        analytes.append(item)

    # Define statistics.
    stats = {'analytes': analytes}

    #-------------------------------------------------------------------
    # Upload the data and the statistics.
    #-------------------------------------------------------------------

    # # Initialize Firebase.
    # initialize_firebase()

    # # Upload the statistics.
    # update_document('public/stats/ct/terpene_prevalence', stats)

    # # Upload the data.
    # for _, values in data.iterrows():
    #     doc_id = values['sample_id']
    #     doc_data = values.to_dict()
    #     ref = f'public/data/state_data/ct/lab_results/{doc_id}'
    #     update_document(ref, doc_data)

        # Return the statistics.
        # return stats
