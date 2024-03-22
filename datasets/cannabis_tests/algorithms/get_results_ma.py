"""
Get MA Lab Result Data
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 7/13/2022
Updated: 8/17/2023
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
        data_dir: str = '.',
        starting_page: int = 1,
        pause: int = 3,
        upload: bool = False,
    ):
    """Get all of the MCR Labs test results."""

    # Get all of the results.
    # FIXME: Fix the errors that are being skipped.
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

    # Save the results to CSV.
    datafile = f'{data_dir}/ma-lab-results-latest.csv'
    data.to_csv(datafile, index=False)

    # Optionally upload the data to Firestore.
    if upload:
        upload_results(data)

    # Return the data.
    return data


# === Test ===
# [✓] Tested: 2024-03-21 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    # DATA_DIR = '../data/ma'
    DATA_DIR = 'D://data/massachusetts/lab_results'

    # Get all of the MCR Labs test results.
    ma_results = get_results_mcrlabs(DATA_DIR)
