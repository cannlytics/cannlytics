"""
Test Data Import | Cannlytics
Authors:
  Keegan Skeate <keegan@cannlytics.com>
Created: 6/16/2021
Updated: 6/16/2021
"""
import os
import environ
# import pytest

import sys
sys.path.append('../../../../')
from cannlytics import firebase # pylint: disable=import-error

VERBOSE = True

if __name__ == '__main__':

    if VERBOSE:
        print('Importing data models...')

    # Initialize Firebase.
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # TODO: Upload instruments, analyses and analytes from data files
    # to Firestore.
