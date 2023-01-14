"""
Retry Metrc API Calls
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/14/2023
Updated: 1/14/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
import base64
import os
import requests

# External imports.
from cannlytics.firebase import (
    # initialize_firebase,
    get_collection,
    update_documents,
)
from firebase_admin import initialize_app, firestore


# TODO: Watch metrc logs.


# TODO: Get log data.


# TODO: Retry the specific Metrc request.


# TODO: Resolve the request or increment failure count.


# TODO: On 3rd failure, email admin.


# BASE = 'https://youtube.googleapis.com/youtube/v3'
# YOUTUBE_CHANNEL_ID = 'UCDzZAV2c0pEimgLo3mUqMaw'


# def get_youtube_video_views(event, context):
#     """Get video views for YouTube channel, saving them to
#     their corresponding video data in Firestore.
#     Triggered from a message on a Cloud Pub/Sub topic.
#     Args:
#          event (dict): Event payload.
#          context (google.cloud.functions.Context): Metadata for the event.
#     """
#     pubsub_message = base64.b64decode(event['data']).decode('utf-8')
#     if pubsub_message != 'success':
#         return

#     # Get YouTube API key saved as an environment variable.
#     print('Getting API Key...')
#     api_key = os.environ.get('YOUTUBE_API_KEY')
#     if api_key is not None:
#         print('Found API key')
#     # if api_key is None:
#     #     import yaml
#     #     dir_path = os.path.dirname(os.path.realpath(__file__))
#     #     with open(f'{dir_path}/env.yaml', 'r') as env:
#     #         config = yaml.load(env, Loader=yaml.FullLoader)
#     #         api_key = config['YOUTUBE_API_KEY']
#     #         credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
#     #         os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

#     # Initialize Firebase.
#     # initialize_firebase()
#     print('Initializing Firebase')
#     try:
#         initialize_app()
#     except ValueError:
#         pass
#     database = firestore.client()
#     print('Initialized Firebase')

#     # Get all videos.
#     print('Getting all videos')
#     videos = get_collection(
#         'public/videos/video_data',
#         order_by='published_at',
#         desc=True,
#         database=database,
#     )
#     print('Found %i videos' % len(videos))

#     # Get view and like count for each video.
#     refs = []
#     updates = []
#     print('Getting views and likes...')
#     for video in videos:
#         video_id = video['id']
#         youtube_id = video['youtube_id']
#         url = f'{BASE}/videos?part=statistics&id={youtube_id}&key={api_key}'
#         response = requests.get(url)
#         data = response.json()
#         stats = data['items'][0]['statistics']
#         updates.append({
#             'views': stats['viewCount'],
#             'likes': stats['likeCount'],
#         })
#         refs.append(f'public/videos/video_data/{video_id}')

#     # Update all videos with the latest view and like count.
#     print('Found all views and likes. Preparing to update videos...')
#     update_documents(refs, updates, database=database)
#     print('Updated all %i videos with view counts.' % len(videos))
