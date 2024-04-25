

# Standard imports.
from datetime import datetime
import os

# External imports.
import pandas as pd

# Internal imports.
from cannlytics.firebase import initialize_firebase, update_documents


def upload_results(
        data: pd.DataFrame,
        collection: str = 'public/data/results',
        key: str = 'sample_hash',
        verbose: bool = False,
    ):
    """Upload test results to Firestore."""
    refs, updates = [], []
    for _, obs in data.iterrows():
        doc_id = obs[key]
        refs.append(f'{collection}/{doc_id}')
        updates.append(obs.to_dict())
    database = initialize_firebase()
    update_documents(refs, updates, database=database)
    if verbose:
        print('Uploaded %i lab results to Firestore.' % len(refs))

# TODO: Read the latest results.


# TODO: Upload COA PDFs (if they don't already exist?)



# TODO: Hash the file.


# TODO: Use local cache to avoid re-uploading duplicate files.

