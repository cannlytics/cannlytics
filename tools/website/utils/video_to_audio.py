"""
Convert a Video File to an Audio File
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/4/2022
Updated: 4/4/2022
License: MIT License <https://opensource.org/licenses/MIT>

Command-line example:

    ```
    python tools/website/utils/video_to_audio.py <episode-name> <optional:volume>
    ```
"""
# Standard imports.
import sys
from typing import Optional

# External imports.
from dotenv import dotenv_values
import moviepy.editor as mp # pip install moviepy


def video_to_audio(directory: str, episode: str, volume: Optional[float] = 1):
    """Save the audio from a video as an audio file.
    Args:
        directory (str): The directory with `videos` and `audio` folders.
        episode (str): The name of the video to extract audio from.
        volume (float): A scale for the volume (optional).
    """

    # Import the video.
    clip = mp.VideoFileClip(f'{directory}/videos/{episode}.mov')

    # Optional: Increase the volume of the video.
    if volume != 1:
        clip = clip.volumex(volume)

    # Output an audio file.
    clip.audio.write_audiofile(f'{directory}/audio/{episode}.mp3')


if __name__ == '__main__':

    # Specify the video directory.
    try:
        config = dotenv_values('../../../.env')
        video_dir = config['VIDEO_DIR']
    except KeyError:
        config = dotenv_values('.env')
        video_dir = config['VIDEO_DIR']

    # Get the episode.
    episode_name = sys.argv[1]

    # Get the volume if specified.
    try:
        volume = sys.argv[2]
    except IndexError:
        volume = 1

    # Save the audio to a file.
    video_to_audio(video_dir, episode_name, volume=1)
