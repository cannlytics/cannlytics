"""
AI Embeddings
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/8/2024
Updated: 10/15/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json

# External imports:
from openai import OpenAI
import pandas as pd

# Internal imports:
from cannlytics.firebase import (
    initialize_firebase,
    get_document,
    update_document,
)
from cannlytics.data import create_hash
from cannlytics.utils import convert_to_numeric


#-----------------------------------------------------------------------
# Embedding Functions
#-----------------------------------------------------------------------

def create_embedding(
        text: str,
        model: str = 'text-embedding-3-small',
        client=None,
    ) -> list[float]:
    """
    Create an embedding for a given text using the specified model.
    Args:
        text (str): The input text for which to generate an embedding.
        model (str): The model to use for generating the embedding.
            Default is 'text-embedding-3-large'.
        client (Optional): An instance of the OpenAI API client. If not provided, 
            a new OpenAI client will be initialized.
    Returns:
        list: A list of float values representing the embedding of the input text.
    """
    if client is None:
        client = OpenAI()
    text = text.replace('\n', ' ').strip()
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


def get_embedding(
        text: str,
        model: str = 'text-embedding-3-small',
        db=None,
        client=None,
        cache=None,
        use_db=True,
    ) -> list[float]:
    """
    Retrieve an embedding from the local cache, Firestore, or
    create an embedding with the OpenAI API if it doesn't exist.
    Args:
        text (str): The input text for which to generate or retrieve an embedding.
        model (str): The model to use for generating the embedding. Default is 'text-embedding-3-large'.
        db (Optional): The Firestore database client. If not provided, the Firestore database will be initialized.
        client (Optional): An instance of the OpenAI API client. If not provided, a new OpenAI client will be initialized.
        cache (Optional): A cache object (Bogart) to store and retrieve embeddings. If not provided, no caching will be used.
    Returns:
        list: A list of float values representing the embedding of the input text, 
            either retrieved from Firestore or newly generated.
    """
    # Try to get the embedding from the cache first.
    text_hash = create_hash(text.strip().lower())
    if cache:
        values = cache.get(text_hash)
        if values is not None:
            return values['embedding']

    # Get the embedding from Firestore if it exists.
    if use_db:
        if db is None:
            db = initialize_firebase()
        text_ref = f'public/ai/embeddings/{text_hash}'
        doc = get_document(text_ref, database=db)
        embedding = doc.get('embedding') if doc else None
        if embedding is not None:
            return embedding

    # Generate a new embedding and save it to Firestore.
    embedding = create_embedding(text, model=model, client=client)
    values = {
        'text': text,
        'embedding': embedding,
        'model': model,
        'dimensions': len(embedding),
    }
    update_document(text_ref, values, database=db)
    if cache:
        cache.set(text_hash, values)
    return embedding


def get_results_embedding(
        results,
        standard_analytes: list,
    ) -> list[float]:
    """
    Create a results embedding from a dictionary of analyte results.
    Args:
        results (dict): A dictionary where keys are analyte names and values are concentrations.
        standard_analytes (list): A list of standard analyte names in a specific order.
    Returns:
        list: A list of float values representing the results embedding.
    """
    embedding = []
    for analyte in standard_analytes:
        value = results.get(analyte, 0.0)
        if pd.isna(value):
            value = 0.0
        elif isinstance(value, str):
            value = convert_to_numeric(value, strip=True)
            if value == '':
                value = 0.0
        embedding.append(float(value))
    return embedding


#-----------------------------------------------------------------------
# Embedding Batches
#-----------------------------------------------------------------------

def create_embedding_batch_file(
        results: pd.DataFrame,
        text_field: str,
        batch_file: str = 'batch.jsonl',
    ):
    """Create a batch file for embeddings."""
    with open(batch_file, 'w+') as f:
        for _, row in results.iterrows():
            if pd.isna(row[text_field]):
                continue
            prompt = {
                'custom_id': row['sample_id'],
                'method': 'POST',
                'url': '/v1/embeddings',
                'body': {
                    'model': 'text-embedding-3-small',
                    'input': row[text_field],
                    'encoding_format': 'float'
                }
            }
            f.write(json.dumps(prompt) + '\n')


def run_batch_job(
        client: OpenAI,
        batch_file: str,
        endpoint='/v1/embeddings',
        verbose=True,
    ):
    """Run a batch job for embeddings."""
    batch_input_file = client.files.create(
        file=open(batch_file, 'rb'),
        purpose='batch'
    )
    if verbose:
        print('Uploaded batch file:', batch_input_file.id)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    job = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint=endpoint,
        completion_window='24h',
        metadata={'description': f'Creating embeddings {timestamp}.'}
    )
    if verbose:
        print('Batch job started:', job.id)
    return job


def upload_batch_embeddings(
        batch_results_file,
        model: str = 'text-embedding-3-small',
        db=None,
        col='public/ai/embeddings',
    ):
    """Save embeddings to Firestore."""
    if db is None:
        db = initialize_firebase()
    with open(batch_results_file, 'r') as f:
        batch_results = [json.loads(line) for line in f]
    for result in batch_results:
        embedding = result['response']['data'][0]['embedding']
        text = result['response']['data'][0]['input']
        text_hash = create_hash(text.strip().lower())
        text_ref = f'{col}/{text_hash}'
        values = {
            'text': text,
            'embedding': embedding,
            'model': model,
            'dimensions': len(embedding),
        }
        update_document(text_ref, values, database=db)
