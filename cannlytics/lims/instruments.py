"""
Instruments | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 8/3/2021  
Updated: 8/3/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Manage scientific instruments and measurements from the instruments.
"""
# Standard imports
import os
import environ

# External imports
import requests

# Internal imports
from cannlytics.firebase import (
    get_collection,
    initialize_firebase,
    update_document
)

API_BASE = 'https://console.cannlytics.com'


def automatic_collection(org_id, env_file='.env'):
    """Automatically collect results from scientific instruments.
    Args:
        org_id (str): The organization ID to associate with instrument results.
        env_file (str): The environment variable file, `.env` by default.
            Either a `GOOGLE_APPLICATION_CREDENTIALS` or a
            `CANNLYTICS_API_KEY` is needed to run the routine.
    Returns
        (list): A list of measurements (dict) that were collected.
    """

    # Initialize Firebase or use an API key.
    try:
        env = environ.Env()
        env.read_env(env_file)
        credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
        db = initialize_firebase()
    except:
        api_key = env('CANNLYTICS_API_KEY')
        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-type': 'application/json',
        }

    # Get the instruments, trying Firestore, then the API.
    try:
        ref = f'organizations/{org_id}/instruments'
        instruments = get_collection(ref)
    except:
        url = f'{API_BASE}/instruments?organization_id={org_id}'
        instruments = requests.get(url, headers=headers)

    # Iterate over instruments, collecting measurements.
    measurements = []
    for instrument in instruments:

        # Identify the analysis being run.
        analysis = instrument['analysis']

        # Get the analytes.
        try:
            ref = f'organizations/{org_id}/analytes'
            analytes = get_collection(ref, filters=[{
                'key': 'analysis', 'operation': '==', 'value': analysis
            }])
        except:
            url = f'{API_BASE}/analytes?organization_id={org_id}&analysis={analysis}'
            analytes = requests.get(url, headers=headers)

        # TODO: Search for recently modified files in the instrument directory.
        # files = sorted([os.path.join(root,f) for root,_,the_files in os.walk(path) for f in the_files if f.lower().endswith(".cpp")], key=os.path.getctime, reverse = True)
        directory = instrument['data_path']
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.xlsx'):
                    data_file = os.path.join(root, filename)

                # TODO: Read in modified file and parse it according to
                # the instrument type and analytes.


    # Upload data to Firestore.
    for measurement in measurements:
        measurement_id = measurement['measurement_id']
        ref = f'organizations/{org_id}/measurements/{measurement_id}'
        update_document(ref, measurement)
    
    # Return the measurements
    return measurements
