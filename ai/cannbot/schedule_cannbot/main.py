"""
CannBot | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/28/2023
Updated: 5/28/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    CannBot is an AI agent that performs automated cannabis research.

References:

    - [arXiv API Access](https://info.arxiv.org/help/api/index.html)
    - [Cannlytics GitHub Repository](https://github.com/cannlytics/cannlytics)

Notes:

    Thank you to arXiv for use of its open access interoperability.

"""
# Internal imports.
import base64
from datetime import datetime
import json
import os
import xml.etree.ElementTree as ET

from dotenv import dotenv_values

# External imports.
from cannlytics import firebase
from firebase_admin import initialize_app, firestore
import openai
import requests
import urllib, urllib.request


def get_directory_contents(path):
    """Get the contents of a directory in a GitHub repo."""
    repo_owner = 'cannlytics'
    repo_name = 'cannabis-data-science'
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}'
    response = requests.get(url)
    return response.json()


def get_latest_episode():
    """Get the latest episode of the Cannabis Data Science Meetup."""

    # Get the most recent season directory.
    seasons = get_directory_contents('')
    season_dirs = sorted([d for d in seasons if d['name'].startswith('season-') and d['type'] == 'dir'], 
                        key=lambda d: int(d['name'].split('-')[1]))
    most_recent_season = season_dirs[-1]

    # Get the most recent episode directory.
    episodes = get_directory_contents(most_recent_season['path'])
    episode_dirs = sorted([d for d in episodes if d['type'] == 'dir'],
                        key=lambda d: int(d['name'].split('-')[0]))
    most_recent_episode = episode_dirs[-1]
    return most_recent_episode


def get_directory_texts(path, file_types=['.md', '.py']):
    """Get the text from desired file types in a folder."""
    texts = []
    files = get_directory_contents(path)
    for file in files:
        ext = os.path.splitext(file['name'])[1]
        if ext in file_types:
            response = requests.get(file['download_url'])
            file_content = response.text
            texts.append(file_content)
    return texts


def element_to_dict(element):
    """Recursively convert XML elements to dictionaries."""
    data = {}
    if element.text: data[element.tag] = element.text.strip()
    else: data[element.tag] = {}
    for child in element:
        child_data = element_to_dict(child)
        if child.tag in data:
            if isinstance(data[child.tag], list): data[child.tag].append(child_data)
            else: data[child.tag] = [data[child.tag], child_data]
        else: data[child.tag] = child_data
    return data


def cannbot(event, context=None):
    """Perform automated cannabis research.
    Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # Run on successful Pub/Sub message.
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    if pubsub_message != 'success':
        return

    # Initialize Firebase.
    try:
        database = firebase.initialize_firebase()
    except:
        try:
            initialize_app()
        except ValueError:
            pass
        database = firestore.client()

    # FIXME: Initialize OpenAI.
    config = dotenv_values('../../../.env')
    openai.api_key = config['OPENAI_API_KEY']

    # Get latest Cannabis Data Science material.
    latest_episode = get_latest_episode()
    episode_texts = get_directory_texts(latest_episode['path'])

    # Get latest research articles on cannabis.
    query = 'cannabis'
    count = 5
    url = f'http://export.arxiv.org/api/query?search_query=all:"{query}"&start=0&max_results={count}&sortBy=lastUpdatedDate&sortOrder=descending'
    data = urllib.request.urlopen(url)
    xml_data = data.read().decode('utf-8')
    root = ET.fromstring(xml_data)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}

    # Iterate over the entry elements
    sources = []
    for entry in root.findall('atom:entry', namespace):
        # Retrieve the elements.
        id_element = entry.find('atom:id', namespace)
        published_element = entry.find('atom:published', namespace)
        title_element = entry.find('atom:title', namespace)
        summary_element = entry.find('atom:summary', namespace)

        # Extract the values.
        id_value = id_element.text if id_element is not None else None
        published_value = published_element.text if published_element is not None else None
        title_value = title_element.text if title_element is not None else None
        summary_value = summary_element.text if summary_element is not None else None

        # Extract the authors
        authors = []
        author_elements = entry.findall('atom:author/atom:name', namespace)
        for author_element in author_elements:
            author_name = author_element.text.strip() if author_element.text is not None else None
            if author_name:
                authors.append(author_name)

        # Record the values.
        sources.append({
            'authors': authors,
            'published_at': published_value,
            'summary': summary_value,
            'title': title_value,
            'url': id_value,
        })

    # Format the prompt.
    system_prompt = 'As a wise, deep thinking philosopher who has great technological capabilities,'
    prompt = """Reflect on the following abstracts and think of potential insights, areas for further research, or interesting facts:"""
    for source in sources:
        prompt += '\n\n' + source['summary']

    # Query OpenAI's GPT model.
    # FIXME: Handle APIConnectionError
    response = openai.ChatCompletion.create(
        model='gpt-4',
        temperature=0.2,
        max_tokens=1000,
        messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ]
    )
    content = response['choices'][0]['message']['content']  

    # Format the sources.
    message = """Hello team, CannBot here.\n\nI have found the latest cannabis-related research on arXiv:\n"""
    for source in sources:
        message += f"\nTitle: {source['title']}\n"
        message += f"Authors: {', '.join(source['authors'])}\n"
        message += f"Published At: {source['published_at']}\n"
        message += f"URL: {source['url']}\n\n"

    # Format CannBot's thoughts.  
    message += """After reflecting on it, here are my thoughts:\n\n"""
    message += content
    message += """\n\nThank you to arXiv for use of its open API. """
    message += """And thank you the Cannabis Data Science team. Please chew on my thoughts and feel free to share any ideas of your own."""

    # TODO: Get latest data from Firestore.
    # - Strains first observed in the last 30 days.
    # - Companies licensed in the last 30 days.
    # - Get summary statistics of results from the last 30 days.


    # TODO: Think about novel research ideas and ways to extend
    # existing Cannabis Data Science material and contribute to cannabis
    # research.


    # TODO: Find Python files with TODOs and FIXMEs and propose
    # solutions.


    # TODO: Save research to Firestore.
    timestamp = datetime.now().isoformat()
    doc = {
        'message': message,
        'sources': sources,
        'timestamp': timestamp,
    }
    ref = f'ai/cannbot/research/{timestamp.replace(":", "-")}'
    firebase.update_document(ref, doc)

    # Optional: Email Admin.

    # Return the message data.
    return doc


# === Test ===

if __name__ == '__main__':

    # Get CannBot to review the latest research.
    pub = {'data': base64.b64encode('success'.encode('utf-8'))}
    data = cannbot(pub)
