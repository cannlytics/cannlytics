"""
Upload Dataset | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 5/30/2021
Updated: 8/22
/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
from datetime import datetime
import os
import environ

import sys
sys.path.append('../../../')
from cannlytics import firebase # pylint: disable=import-error

def upload_dataset(data):
    """Upload a given dataset to the Cannlytics data archive."""
    data['updated_at'] = datetime.now().isoformat()
    firebase.update_document(f'public/data/datasets')

if __name__ == '__main__':
    
    upload_dataset({
        
    })
