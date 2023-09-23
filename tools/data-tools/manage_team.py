"""
Manage Team | Cannlytics Website
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/26/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/website/data/manage_team.py get_team_data
    ```

    Upload data.

    ```
    python tools/website/data/manage_team.py upload_team_data
    ```
"""
# Standard imports
import os
import sys

# External imports
from dotenv import dotenv_values

# Internal imports
from data_management import get_data, upload_data

# Set credentials.
try:
    config = dotenv_values('../../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    config = dotenv_values('.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


def get_team_data(filename, doc, ref):
    """Get team member data from Firestore."""
    try:
        return get_data(ref, datafile=f'.datasets/website/{filename}')
    except FileNotFoundError:
        return get_data(ref, datafile=f'../../../.datasets/website/{filename}')


def upload_team_data(filename, doc, ref):
    """Upload team member data from local `.datasets`."""
    try:
        upload_data(f'.datasets/website/{filename}', ref, stats_doc=doc)
    except FileNotFoundError:
        upload_data(f'../../../.datasets/website/{filename}', ref, stats_doc=doc)


# === Test ===
if __name__ == '__main__':

        # Define references.
    FILENAME = 'team.json'
    DOC = 'public/team'
    REF = f'{DOC}/team_members'

    # Make functions available from the command line.
    globals()[sys.argv[1]](FILENAME, DOC, REF)
