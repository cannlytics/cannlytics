"""
Upload Video | Cannlytics Website

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: Wed May 19 13:36:01 2021
License: MIT License <https://opensource.org/licenses/MIT>

This script uploads a specified video and it's data to the
Cannlytics video archive.

"""
from datetime import datetime

PUBLISHED_AT = '2021-02-'

if __name__ == '__main__':
    
    # Get the specified video.
    
    # Upload the video to Firebase storage.
    
    # Get a reference for the video.
    
    # Save the reference to the video and the
    # video's metadta to Firestore.
    video_data = {
        'published_at': PUBLISHED_AT
        'uploaded_at': datetime.now().isoformat()
    }
