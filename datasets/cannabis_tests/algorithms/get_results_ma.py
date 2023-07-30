"""
Get MA Lab Result Data
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 5/30/2023
License: CC-BY 4.0 <https://huggingface.co/datasets/cannlytics/cannabis_tests/blob/main/LICENSE>

Description:

    Collect all public Massachusetts lab result data.

Data Sources:
    
    - [MCR Labs Test Results](https://reports.mcrlabs.com)

"""
# Standard imports.
from datetime import datetime
import os

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.data.coas.algorithms.mcrlabs import get_mcr_labs_test_results
from cannlytics.firebase import initialize_firebase, update_documents
from cannlytics.utils.utils import to_excel_with_style


# Specify where your data lives.
DATA_DIR = r'D:\data\massachusetts\lab_results\mcr_labs'
# DATA_DIR = r'C:\.datasets\data\massachusetts\lab_results\mcr_labs'


def upload_results(data: pd.DataFrame):
    """Upload test results to Firestore."""
    refs, updates = [], []
    for _, obs in data.iterrows():
        sample_id = obs['sample_id']
        refs.append(f'public/data/lab_results/{sample_id}')
        updates.append(obs.to_dict())
    database = initialize_firebase()
    update_documents(refs, updates, database=database)
    print('Uploaded %i lab results to Firestore!' % len(refs))


def get_results_mcrlabs(
        data_dir: str = DATA_DIR,
        starting_page: int = 1,
        pause: int = 3,
        upload: bool = False,
    ):
    """Get all of the MCR Labs test results."""

    # Get all of the results!
    all_results = get_mcr_labs_test_results(
        starting_page=starting_page,
        pause=pause,
    )

    # Save the results to Excel.
    data = pd.DataFrame(all_results)
    date = datetime.now().isoformat()[:10]
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    datafile = f'{data_dir}/ma-lab-results-{date}.xlsx'
    try:
        to_excel_with_style(data, datafile)
    except:
        data.to_excel(datafile)

    # Optionally upload the data to Firestore.
    if upload:
        upload_results(data)

    # Return the data.
    return data


# === Test ===
if __name__ == '__main__':

    # Get all of the MCR Labs test results.
    ma_results = get_results_mcrlabs(DATA_DIR)
