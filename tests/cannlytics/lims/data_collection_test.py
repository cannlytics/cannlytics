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
from cannlytics.lims.instruments import automatic_collection

# CONFIG = {
#     "instruments": [
#         {
#             "name": "",
#             "id": "",
#             "instrument_type": "",
#             "data_path": "",
#             "vendor": "",
#             "model": "",
#         }
#     ],
#     "analyses": [
#         {
#             "name": "Cannabinoids",
#             "key": "cannabinoids",
#             "analytes": [
#                 {
#                     "name": "",
#                     "key": "",
#                     "import_key": "",
#                     "loq": 0,
#                     "limit": 0,
#                 }
#             ]

#         }
#     ],
# }


if __name__ == '__main__':

    # Collect results for the test-company.
    automatic_collection('test-company', env_file='../../../.env')
