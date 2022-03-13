"""
Get Cannabis Data Test
Copyright (c) 2021 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 11/22/2021
Updated: 11/22/2021
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""

import sys
sys.path.append('./')
sys.path.append('../')
from ai.get_cannabis_data.main import get_cannabis_data # pylint: disable=import-error


class Context:
    """Mock Google Cloud Function context."""
    def __init__(self, event_id, timestamp, event_type, resource):
        self.event_id = event_id
        self.timestamp = timestamp
        self.event_type = event_type
        self.resource = resource


def test_get_cannabis_data():
    """Test the `get_cannabis_data` cloud function."""
    event = {
        'project': 'mock-project',
        'bucket': 'MOCK BUCKET',
        'name': 'mock/cloud/path/to/file'
    }
    context = Context(
        event_id=420420,
        timestamp='1637592291000',
        event_type='google.pubsub.topic.publish',
        resource='topic'
    )
    success = get_cannabis_data(event, context)
    assert success == 0


if __name__ == '__main__':
    test_get_cannabis_data()
