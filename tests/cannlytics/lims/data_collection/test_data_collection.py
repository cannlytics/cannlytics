"""
Test Data Collection | Cannlytics
Authors:
  Keegan Skeate <keegan@cannlytics.com>
  Charles Rice <charles@ufosoftwarellc.com>
Created: 6/15/2021
Updated: 6/15/2021
TODO:
    - Setup script to run as a CRON job.
"""
import os
import environ
# import pytest

import sys
sys.path.append('../../../../')
from cannlytics import firebase # pylint: disable=import-error


CONFIG = {
    "instruments": [
        {
            "name": "",
            "id": "",
            "instrument_type": "",
            "data_path": "",
            "vendor": "",
            "model": "",
        }
    ],
    "analyses": [
        {
            "name": "Cannabinoids",
            "key": "cannabinoids",
            "analytes": [
                {
                    "name": "",
                    "key": "",
                    "import_key": "",
                    "loq": 0,
                    "limit": 0,
                }
            ]

        }
    ],
}

VERBOSE = True

if __name__ == '__main__':

    if VERBOSE:
        print('Collecting instrument data...')

    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # TODO: Pull instruments, analyses and analytes from a config file
    # or from Firestore.


    # TODO: Iterate through the instruments, searching for recently
    # modified files.

    # TODO: Read in modified file and parse it according to instrument
    # vendor and analysis.

    # TODO: Upload data to Firestore.
