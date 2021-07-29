"""
Upload Video Data | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/15/2021
Updated: 7/29/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

import json
import environ
import os

import sys
root = '../../'
sys.path.append(root)
from cannlytics import firebase # pylint: disable=import-error

if __name__ == '__main__':

    # Initialize Firebase.
    env = environ.Env()
    env.read_env(f'{root}.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    
    # Read in the video data.
    directory = env('VIDEO_DIR')
    with open(f'{directory}/videos/videos.json') as f:
        data = json.load(f)

    # Upload subscription plan data to Firestore.
    for item in data:
        doc_id = item['video_id']
        ref = f'public/videos/video_data/{doc_id}'
        firebase.update_document(ref, item)
