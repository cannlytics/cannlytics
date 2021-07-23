"""
Upload Video | Cannlytics Website

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 5/19/2021
Updated: 6/27/2021
License: MIT License <https://opensource.org/licenses/MIT>

This script uploads a specified video and it's data to the
Cannlytics video archive.

"""
import os
import environ
from datetime import datetime

import sys
sys.path.append('../../')
from cannlytics import firebase # pylint: disable=import-error


def upload_video(api_key, bucket_name, file_name, destination, video_data):
    """Upload a video to Firebase Storage,
    get a storage URL reference for the video,
    and finally create a short link for the video.
    Args:
        api_key (str): Firebase project API key.
        bucket_name (str): The name of the strorage bucket.
        file_name (str): The path of the file to upload.
        video_data (dict): Metadata about the video.
    Returns:
        (dict): The video data updated with the storage ref and URL.
    """
    video_data['uploaded_at'] = datetime.now().isoformat()
    firebase.upload_file(bucket_name, destination, file_name, verbose=True)
    video_data['storage_url'] = firebase.get_file_url(destination, bucket_name)
    video_data['short_link'] = firebase.create_short_url(api_key, video_data['storage_url'])
    firebase.update_document(destination, video_data)
    return video_data

if __name__ == '__main__':

    # Initialize Firebase and get the Firebase project API key.
    env = environ.Env()
    env.read_env('../../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()
    api_key = firebase.get_document('admin/firebase')['web_api_key']
    bucket_name = env('FIREBASE_STORAGE_BUCKET')

    # Upload a video to Firebase storage, saving the metadata to Firestore.
    video_dir =  env('VIDEO_DIR')
    file_name = 'cannabis-data-science-episode-1'
    extension = '.mov'
    video_data = {
        'music': ['Vivaldi'],
        'category': 'Category: Science and Technology',
        'title': 'Data Wrangling | Cannabis Data Science Episode 1',
        'description': 'Join the fun, zany bunch on our first Cannabis Data Science meetup as we begin to wrangle the firehose of data that the Washington State traceability system offers to the public. Support the group: https://opencollective.com/cannlytics-company Find the data and source code: https://github.com/cannlytics/cannabis-data-science',
        'published_at': '2021-02-24',
        'video_id': 'cannabis-data-science-episode-1',
        'size': '1.21GB',
        'length': '1:03:28',
        'cover_image_url': '', # TODO: Add a cover image URL.
    }
    video_id = video_data['video_id']
    destination = f'public/cannabis_data_science/videos/{video_id}'
    full_file_name = os.path.join(video_dir, file_name + extension)
    print('Uploading video:', full_file_name, 'to', destination)
    upload_video(api_key, bucket_name, full_file_name, destination, video_data)
    print('Uploaded video:', full_file_name)
