"""
Upload Video Data | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 7/15/2021
Updated: 8/11/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
from dateutil import parser
import json
import environ
import os

import sys
root = '../../'
sys.path.append(root)
from cannlytics import firebase # pylint: disable=import-error


def upload_all_videos(datafile):
    """ Upload all video data.
    Args:
        datafile (str): The path to a .json file containing the video data.
    """
    # Read in the video data.
    with open(datafile) as f:
        data = json.load(f)

    # Upload subscription plan data to Firestore.
    number = 0
    for item in data:
        number += 1
        item['number'] = number
        item['published'] = parser.parse(item['published_at'])
        doc_id = item['video_id']
        ref = f'public/videos/video_data/{doc_id}'
        firebase.update_document(ref, item)
    
    # Update video statistics.
    firebase.update_document('public/videos', {'total_videos': len(data)})
    return data


def upload_latest_video(datafile):
    """ Upload the lastest video data.
    Args:
        datafile (str): The path to a .json file containing the video data.
    """
    
    # Read in the video data.
    with open(datafile) as f:
        data = json.load(f)
        
    # Get the current count of videos.
    doc = firebase.get_document('public/videos')
    number = doc['total_videos']

    # Upload subscription plan data to Firestore.
    # Only incrementing the number of videos if the video doesn't exist yet.
    for item in data[-1:]:
        doc_id = item['video_id']
        ref = f'public/videos/video_data/{doc_id}'
        existing_doc = firebase.get_document(ref)
        if not existing_doc:
            number += 1
        item['number'] = number
        item['published'] = parser.parse(item['published_at'])
        firebase.update_document(ref, item)
    
    # Update video statistics.
    firebase.update_document('public/videos', {'total_videos': len(data)})
    return data[-1]

if __name__ == '__main__':

    # Initialize Firebase.
    env = environ.Env()
    env.read_env(f'{root}.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    firebase.initialize_firebase()
    directory = env('VIDEO_DIR')
    datafile = f'{directory}/videos/videos.json'
    
    # Upload the latest video
    # print('Uploading latest video...')
    # video_data = upload_latest_video(datafile)
    # print('Uploaded video:\n', video_data)
    
    # Upload the entire video archive data.
    print('Uploading video archive data...')
    video_data = upload_all_videos(datafile)
    print('Uploaded data for all videos. Total:', len(video_data))
