"""
Get Daily Cannabis Data | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 9/16/2021
Updated: 9/16/2021
License: MIT License <https://opensource.org/licenses/MIT>
Description:
    Get public cannabis data that needs to be updated daily.
"""
from get_data_ct import get_data_ct
from get_data_ma import get_data_ma

DAILY_ROUTINES = [
    # 'get_data_ct',
    'get_data_ma',
]


def get_cannabis_data_daily(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print('Initializing Get Cannabis Daily Data Routine.')

    # Run all state daily data collection routines.
    for routine in DAILY_ROUTINES:
        state = routine.replace('get_data_', '')
        print('Getting data for %s.' % state)
        try:
            eval(routine + '()')
            print('Successfully retrieved data for %s.' % state)
        except:
            print('Failed getting data for %s.' % state)
    print('Finished collecting daily data for %i states.' % len(DAILY_ROUTINES))
