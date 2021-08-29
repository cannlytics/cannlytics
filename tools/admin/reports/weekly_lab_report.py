"""
Weekly Lab Report | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 8/20/2021
Updated: 8/20/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports
from datetime import datetime
import os
import environ

# Internal imports
import sys
sys.path.append('../../../')
from cannlytics import firebase # pylint: disable=import-error


def create_weekly_lab_report(org_id):
    """Create a weekly lab report for lab organization owners that
    provides summary statistics and figures of their historic performance
    and forecasts for the coming week, measuring forecast errors
    of prior forecasts.

    The weekly lab report principally provides:

        - Timeseries statistics and figures for all key series.
        - Calculation of key performance indicators, including:
            * Average turnaround time per sample.
            * Number of new clients.
    
    Args:
        org_id (str): The organization ID of the company for which to prepare
            a report.
    """
    summary_stats = {}
    
    # Get a company's data models.
    data_models = firebase.get_collection(f'organizations/{org_id}/data_models')
    
    # Calculate summary statistics for each data model.
    for data_model in data_models:
        key = data_model['key']
        print(key)
        summary_stats[key] = {}
        
        # Get model data.
        data = firebase.get_collection(f'organizations/{org_id}/{key}')
        
        # Calculate model data summary statistics.
        summary_stats[key]['total'] = len(data)
        
        # TODO: Calculate daily, weekly, and monthly stats.


    # TODO: Calculate key performance indicators.
        # - Average turnaround time per sample.
        # - Number of new clients.


    # Upload the summary statistics.
    update_document(f'organizations/{org_id}/, summary_stats)
    

    # TODO: Create figures.


    # TODO: Create LaTeX tables and text.


    # Optional: Email the report.
    
    return summary_stats


if __name__ == '__main__':
    
    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    
    # Create lab report for a given company.
    org_id = 'test-company'
    summary_stats = create_weekly_lab_report(org_id)
