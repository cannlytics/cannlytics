"""
Get Daily Cannabis Data | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 9/16/2021
Updated: 9/16/2021
License: MIT License <https://opensource.org/licenses/MIT>
Description:
    Get public cannabis data that needs to be updated daily.
"""
# Standard imports
# import base64

# Internal imports
from get_data_ct import get_data_ct


def get_cannabis_data_daily(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    # if pubsub_message != 'success':
    #     return

    # Get state daily data.
    get_data_ct()
