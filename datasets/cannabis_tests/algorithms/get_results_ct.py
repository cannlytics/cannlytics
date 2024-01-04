"""
Cannabis Tests | Get Connecticut Test Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/8/2023
Updated: 7/3/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Data Source:

    - Connecticut Medical Marijuana Brand Registry
    URL: <https://data.ct.gov/Health-and-Human-Services/Medical-Marijuana-Brand-Registry/egd5-wb6r/data>

"""
# Standard imports:
from datetime import datetime
import os
import requests
from typing import Optional

# External imports:
import cannlytics
from cannlytics.utils import convert_to_numeric
import pandas as pd


# Connecticut lab results API URL.
CT_RESULTS_URL = 'https://data.ct.gov/api/views/egd5-wb6r/rows.json'

# Connecticut lab results fields.
CT_FIELDS = {
    'sid': 'id',
    'id': 'lab_id',
    'position': None,
    'created_at': None,
    'created_meta': None,
    'updated_at': 'data_refreshed_date',
    'updated_meta': None,
    'meta': None,
    'brand_name': 'product_name',
    'dosage_form': 'product_type',
    'producer': 'producer',
    'product_image': 'image_url',
    'label_image': 'images',
    'lab_analysis': 'lab_results_url',
    'approval_date': 'date_tested',
    'registration_number': 'traceability_id',
}
CT_CANNABINOIDS = {
    'cbg': 'cbg',
    'cbg_a': 'cbga',
    'cannabavarin_cbdv': 'cbdv',
    'cannabichromene_cbc': 'cbc',
    'cannbinol_cbn': 'cbn',
    'tetrahydrocannabivarin_thcv': 'thcv',
    'tetrahydrocannabinol_thc': 'thc',
    'tetrahydrocannabinol_acid_thca': 'thca',
    'cannabidiols_cbd': 'cbd',
    'cannabidiol_acid_cbda': 'cbda',
}
CT_TERPENES = {
    'a_pinene': 'alpha_pinene',
    'b_myrcene': 'beta_myrcene',
    'b_caryophyllene': 'beta_caryophyllene',
    'b_pinene': 'beta_pinene',
    'limonene': 'limonene',
    'ocimene': 'ocimene',
    'linalool_lin': 'linalool_lin',
    'humulene_hum': 'humulene_hum',
    'a_bisabolol': 'alpha_bisabolol',
    'a_phellandrene': 'alpha_phellandrene',
    'a_terpinene': 'alpha_terpinene',
    'b_eudesmol': 'beta_eudesmol',
    'b_terpinene': 'beta_terpinene',
    'fenchone': 'fenchone',
    'pulegol': 'pulegol',
    'borneol': 'borneol',
    'isopulegol': 'isopulegol',
    'carene': 'carene',
    'camphene': 'camphene',
    'camphor': 'camphor',
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
    'trans_b_farnesene': 'trans_beta_farnesene',
    'valencene': 'valencene',
    'a_cedrene': 'alpha_cedrene',
    'a_farnesene': 'alpha_farnesene',
    'b_farnesene': 'beta_farnesene',
    'cis_nerolidol': 'cis_nerolidol',
    'fenchol': 'fenchol',
    'trans_nerolidol': 'trans_nerolidol'
}


def flatten_results(x):
    """Flatten the results."""
    results = []
    for name, analyte in CT_CANNABINOIDS.items():
        # print(analyte, x[name])
        results.append({
            'key': analyte,
            'name': name,
            'value': convert_to_numeric(x[name]),
            'units': 'percent',
            'analysis': 'cannabinoids',
        })
    for name, analyte in CT_TERPENES.items():
        # print(analyte, x[name])
        results.append({
            'key': analyte,
            'name': name,
            'value': convert_to_numeric(x[name]),
            'units': 'percent',
            'analysis': 'terpenes',
        })
    return results


def get_results_ct(url: str = CT_RESULTS_URL) -> pd.DataFrame:
    """Get all of the Connecticut test results.
    Args:
        url (str): The URL to the CSV data.
    Returns:
        df (pd.DataFrame): A Pandas DataFrame of the test results.
    """

    # Get the data from the OpenData API.
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        metadata = json_data['meta']
        header = metadata['view']['columns']
        headers = [h['name'] for h in header]
        columns = [cannlytics.utils.snake_case(h) for h in headers]
        rows = json_data['data']
        df = pd.DataFrame(rows, columns=columns)
    else:
        print('Failed to fetch CT results. Status code:', response.status_code)
    
    # FIXME: Standardize the results.
    # Note: The results do not match the COAs!!!
    df['results'] = df.apply(flatten_results, axis=1)

    # Drop unnecessary columns.
    drop_columns = ['meta', 'position', 'created_at', 'created_meta',
        'updated_at', 'updated_meta']
    drop_columns += list(CT_CANNABINOIDS.keys()) + list(CT_TERPENES.keys())
    df.drop(columns=drop_columns, inplace=True)

    # Rename the columns.
    df.rename(columns=CT_FIELDS, inplace=True)

    # TODO: Extract product_size, serving_size, servings_per_package, sample_weight
    # from dosage_form and standardize product type.

    # TODO: Format COA URLs.
    # coa_urls

    # Save the results to Excel.
    date = datetime.now().isoformat()[:10]
    datafile = f'{data_dir}/ct-lab-results-{date}.xlsx'
    try:
        cannlytics.utils.to_excel_with_style(df, datafile)
    except:
        df.to_excel(datafile)
    print('Connecticut lab results archived:', datafile)
    return df


def download_pdfs_ct(
        df: pd.DataFrame,
        download_path: str,
        column_name: Optional[str] = 'lab_results_url',
        id_column: Optional[str] = 'id',
        verbose: Optional[bool] = True,
    ) -> None:
    """
    Downloads all PDFs from a specified column in a Pandas DataFrame.
    Args:
        df (pandas.DataFrame): The input DataFrame containing the URLs of the PDFs.
        column_name (str): The name of the column containing the PDF URLs.
        download_path (str): The path to the directory where the PDFs will be downloaded.
    """
    for _, row in df.iterrows():
        pdf_url = row[column_name]
        if isinstance(pdf_url, list):
            pdf_url = pdf_url[0]

        # Create the filename from the ID.
        filename = row[id_column]
        if not filename.endswith('.pdf'):
            filename = filename + '.pdf'

        # Create the local file path for downloading the PDF.
        # Continue if the PDF is already downloaded.
        outfile = os.path.join(download_path, filename)
        if os.path.isfile(outfile) or pdf_url is None:
            continue

        # Download the PDF.
        try:
            response = requests.get(pdf_url)
        except:
            print(f'Failed to download PDF: {pdf_url}')
            continue
        if response.status_code == 200:
            with open(outfile, 'wb') as file:
                file.write(response.content)
            if verbose:
                print(f'Downloaded PDF: {outfile}.')
        else:
            print(f'Failed to download PDF {filename}. Status code:', response.status_code)


# === Test ===
# [✓] Tested: 2023-08-29 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Command line usage.
    import argparse
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--pdf_dir', dest='pdf_dir', type=str)
        parser.add_argument('--data_dir', dest='data_dir', type=str)
        args = parser.parse_args()
    except SystemExit:
        args = {}

    # Specify where your data lives.
    DATA_DIR = 'D:/data/connecticut/lab_results'
    PDF_DIR = 'D:/data/connecticut/lab_results/pdfs'
    stats_dir = '../data/ct'

    # Set the destination for the PDFs.
    data_dir = args.get('data_dir', DATA_DIR)
    pdf_dir = args.get('pdf_dir', os.path.join(data_dir, 'pdfs'))

    # Get the test results.
    print('Getting Connecticut test results...')
    results = get_results_ct()

    # Download the PDFs.
    print('Downloading PDFs...')
    if not os.path.exists(pdf_dir): os.makedirs(pdf_dir)
    download_pdfs_ct(results, pdf_dir)

    # Save the results to Excel.
    date = datetime.now().isoformat()[:10]
    results.to_excel(f'{stats_dir}/ct-lab-results-{date}.xlsx', index=False)
    results.to_csv(f'{stats_dir}/ct-lab-results-latest.csv', index=False)
    print('Connecticut lab results archived:', stats_dir)

    # TODO: Integrate with `analyte_results_ct.py`.
