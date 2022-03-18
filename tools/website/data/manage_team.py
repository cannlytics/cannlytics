"""
Manage Team | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/26/2021
Updated: 12/26/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_team.py get_team_data
    ```

    Upload data.

    ```
    python tools/data/manage_team.py upload_team_data
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
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    config = dotenv_values('.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


def get_team_data():
    """Get team member data from Firestore."""
    ref = 'public/team/team_members'
    try:
        return get_data(REF, datafile='.datasets/team.json')
    except FileNotFoundError:
        return get_data(REF, datafile='../../.datasets/team.json')


def upload_team_data():
    """Upload team member data from local `.datasets`."""
    ref = 'public/team/team_members'
    stats_doc = 'public/team'
    try:
        upload_data('.datasets/team.json', ref, stats_doc=stats_doc)
    except FileNotFoundError:
        upload_data('../../.datasets/team.json', ref, stats_doc=stats_doc)


if __name__ == '__main__':

    # Make functions available from the command line.
    globals()[sys.argv[1]]()
