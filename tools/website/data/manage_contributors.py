"""
Get Github Contributors | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/9/2021
Updated: 12/27/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Dependencies:

    - PyGithub: https://pygithub.readthedocs.io/en/latest/examples/MainClass.html#get-user-by-name

    ```
    pip install PyGithub
    ```

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_contributors.py get_contributor_data
    ```

    Upload data.

    ```
    python tools/data/manage_contributors.py upload_contributor_data
    ```
"""
# Standard imports.
import os
import sys

# External imports.
from dotenv import dotenv_values
from github import Github

# Internal imports.
sys.path.append('../')
sys.path.append('./')
from cannlytics.firebase import ( #pylint: disable=import-error, wrong-import-position
    initialize_firebase,
    update_document,
)
from datasets import get_dataset #pylint: disable=wrong-import-position

# Set credentials.
try:
    config = dotenv_values('../../.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    config = dotenv_values('.env')
    credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


def get_contributor_data():
    """Get contributor data from Firestore."""
    ref = 'public/contributors/contributor_data'
    try:
        return get_data(REF, datafile='.datasets/contributors.json')
    except FileNotFoundError:
        return get_data(REF, datafile='../../.datasets/contributors.json')


def upload_contributors(org_name):
    """Get Github contributors and save them to Firestore.
    Args:
        org_name (str): The name of a GitHub organization.
    Returns:
        (list): A list of users (dict).
    """
    users = []
    client = Github()
    org = client.get_organization(org_name)
    repos = org.get_repos()
    initialize_firebase()
    for repo in repos:
        contributors = repo.get_contributors()
        for user in contributors:
            if user.name not in users:
                users.append(user.name)
                data = {
                    'company': user.company,
                    'description': user.bio,
                    'name': user.name,
                    'location': user.location,
                    'image': user.avatar_url,
                    'url': user.html_url,
                    'slug': user.login,
                }
                update_document(f'public/contributors/contributor_data/{user.id}', data)
    return users


if __name__ == '__main__':

    # Make functions available from the command line.
    globals()[sys.argv[1]]()
