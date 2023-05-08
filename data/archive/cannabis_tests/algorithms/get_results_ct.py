"""
Cannabis Tests | Get Connecticut Test Result Data
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/8/2023
Updated: 5/6/2023
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
import pandas as pd


# Connecticut lab results API URL.
CT_RESULTS_URL = 'https://data.ct.gov/api/views/egd5-wb6r/rows.json'

# Specify where your data lives.
DATA_DIR = 'D:/data/connecticut/lab_results'
PDF_DIR = 'D:/data/connecticut/lab_results/pdfs'


def get_results_ct(url: str = CT_RESULTS_URL) -> pd.DataFrame:
    """Get all of the Connecticut test results.
    Args:
        url (str): The URL to the CSV data.
    Returns:
        df (pd.DataFrame): A Pandas DataFrame of the test results.
    """

    # Send a GET request to the URL.
    response = requests.get(url)

    # Check if the request was successful (status code 200).
    if response.status_code == 200:

        # Load the JSON data from the response.
        json_data = response.json()

        # Get the metadata to get the columns.
        metadata = json_data['meta']
        header = metadata['view']['columns']
        headers = [h['name'] for h in header]
        columns = [cannlytics.utils.snake_case(h) for h in headers]

        # Get the CSV data.
        rows = json_data['data']

        # Create a Pandas DataFrame from the columns and rows.
        df = pd.DataFrame(rows, columns=columns)
        return df
    else:
        print('Failed to fetch CT results. Status code:', response.status_code)


def download_pdfs(
        df: pd.DataFrame,
        download_path: str,
        column_name: Optional[str] = 'lab_analysis',
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
    # Iterate over the rows in the specified column
    for _, row in df.iterrows():
        pdf_url = row[column_name]
        if isinstance(pdf_url, list):
            pdf_url = pdf_url[0]

        # Create the filename from the ID.
        filename = row[id_column]
        if not filename.endswith('.pdf'):
            filename = filename + '.pdf'

        # Create the local file path for downloading the PDF.
        outfile = os.path.join(download_path, filename)

        # Continue if the PDF is already downloaded.
        if os.path.isfile(outfile) or pdf_url is None:
            continue

        # Send a GET request to download the PDF.
        try:
            response = requests.get(pdf_url)
        except:
            print(f'Failed to download PDF: {pdf_url}')
            continue

        # Check if the request was successful (status code 200).
        if response.status_code == 200:

            # Write the PDF content to the local file.
            with open(outfile, 'wb') as file:
                file.write(response.content)
            if verbose:
                print(f'Downloaded PDF: {outfile}.')
        else:
            print(f'Failed to download PDF {filename}. Status code:', response.status_code)


# === Test ===
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

    # Set the destination for the PDFs.
    download_path = args.get('pdf_dir', PDF_DIR)
    data_dir = args.get('data_dir', DATA_DIR)

    # Get the test results.
    print('Getting Connecticut test results...')
    results = get_results_ct()

    # Download the PDFs.
    print('Downloading PDFs...')
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    download_pdfs(results, download_path)

    # Save the results to Excel.
    date = datetime.now().isoformat()[:10]
    datafile = f'{data_dir}/ct-results-{date}.xlsx'
    cannlytics.utils.to_excel_with_style(results, datafile)
    print('Connecticut lab results archived:', datafile)

    # TODO: Parse the PDFs with CoADoc.

    # TODO: Parse the PDFs with CoAGPT.
