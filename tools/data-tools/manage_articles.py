"""
Manage Articles | Cannlytics Website
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/26/2021
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Command-line examples:

    Get and save data.

    ```
    python tools/data/manage_articles.py get_article_data
    ```

    Upload data.

    ```
    python tools/data/manage_articles.py upload_article_data
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


def get_article_data():
    """Get article data from Firestore."""
    ref = 'public/articles/article_data'
    try:
        return get_data(ref, datafile='.datasets/articles.json')
    except FileNotFoundError:
        return get_data(ref, datafile='../../.datasets/articles.json')


def upload_article_data():
    """Upload article data from local `.datasets`."""
    ref = 'public/articles/article_data'
    stats_doc = 'public/articles'
    try:
        upload_data('.datasets/articles.json', ref, stats_doc=stats_doc)
    except FileNotFoundError:
        upload_data('../../.datasets/articles.json', ref, stats_doc=stats_doc)


# === Test ===
if __name__ == '__main__':

    # Make functions available from the command line.
    globals()[sys.argv[1]]()
