# -*- coding: utf-8 -*-
"""
Get Github Contributors | Cannlytics

Copyright © 2020 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 1/9/2021
Updated: 7/29/2021
License: MIT License <https://opensource.org/licenses/MIT>
Resources:
    https://pygithub.readthedocs.io/en/latest/examples/MainClass.html#get-user-by-name
"""
# Standard imports
import sys

# External imports
from github import Github

# Internal imports
sys.path.append('../../')
from cannlytics.firebase import initialize_firebase, update_document


def upload_github_contributors(org_name):
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
                update_document(f'contributors/{user.id}', data)
    return users

if __name__ == '__main__':   

    # Save all contributors.
    print('Saving contributors.')
    contributors = upload_github_contributors(org_name='Cannlytics')
    print('Saved all contributors:', len(contributors))
