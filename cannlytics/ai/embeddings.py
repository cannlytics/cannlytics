"""
AI Embeddings
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/8/2024
Updated: 10/21/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json
from pathlib import Path

# External imports:
from openai import OpenAI
import pandas as pd

# Internal imports:
from cannlytics.data import create_hash
from cannlytics.firebase import (
    initialize_firebase,
    get_document,
    update_document,
)
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
        verbose=False,
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
            embedding = values['embedding']
            if isinstance(embedding, list):
                if verbose:
                    print(f'Found embedding in cache: {text_hash}')
                return embedding

    # Get the embedding from Firestore if it exists.
    if use_db:
        if db is None:
            db = initialize_firebase()
        text_ref = f'public/ai/embeddings/{text_hash}'
        doc = get_document(text_ref, database=db)
        embedding = doc.get('embedding') if doc else None
        if isinstance(embedding, list):
            if verbose:
                print(f'Found embedding in Firestore: {text_ref}')
            if cache:
                cache.set(text_hash, doc)
            return embedding

    # Generate a new embedding.
    embedding = create_embedding(text, model=model, client=client)

    # Save the embedding to Firestore.
    values = {
        'text': text,
        'embedding': embedding,
        'model': model,
        'dimensions': len(embedding),
    }
    update_document(text_ref, values, database=db)
    if verbose:
        print(f'Saved embedding to Firestore: {text_ref}')
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

def create_batch_embeddings(
        results: pd.DataFrame,
        text_field: str,
        batch_file: str = 'batch.jsonl',
        custom_id: str = 'slug',
        model: str = 'text-embedding-3-small',
    ) -> str:
    """Create a batch file for embeddings.
    Args:
        results (pd.DataFrame): The results DataFrame containing the text data.
        text_field (str): The name of the text field in the results DataFrame.
        batch_file (str): The path to the batch file to create.
        custom_id (str): The name of the custom ID field in the results DataFrame.
        model (str): The model used to generate the embeddings.
    Returns:
        str: The path to the inputs file.
    """
    # Save the batch file.
    inputs = {}
    with open(batch_file, 'w') as f:
        for _, row in results.iterrows():
            if pd.isna(row[text_field]):
                continue
            prompt = {
                'custom_id': str(row[custom_id]),
                'method': 'POST',
                'url': '/v1/embeddings',
                'body': {
                    'model': model,
                    'input': row[text_field],
                    'encoding_format': 'float'
                }
            }
            f.write(json.dumps(prompt) + '\n')
            inputs[str(row[custom_id])] = row[text_field]

    # Save the inputs file.
    batch_path = Path(batch_file)
    inputs_file = batch_path.parent / f'{batch_path.stem}-inputs.json'
    with open(inputs_file, 'w') as f:
        json.dump(inputs, f, ensure_ascii=False, indent=2)

    # Return the path to the inputs file.
    return inputs_file


def run_batch_embeddings(
        client: OpenAI,
        batch_file: str,
        endpoint='/v1/embeddings',
        verbose=True,
    ):
    """Run a batch job for embeddings.
    Args:
        client (OpenAI): The OpenAI API client.
        batch_file (str): The path to the batch file.
        endpoint (str): The API endpoint to use for the batch job.
        verbose (bool): Whether to print out progress.
    Returns:
        Batch: The batch job object.
    """
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
        verbose=True,
    ):
    """Save embeddings to Firestore.
    Args:
        batch_results_file (str): The path to the batch results file.
        model (str): The model used to generate the embeddings.
        db (Optional): The Firestore database client. If not provided, the Firestore database will be initialized.
        col (str): The Firestore collection where the embeddings should be saved.
        verbose (bool): Whether to print out progress
    """
    if db is None:
        db = initialize_firebase()
    batch_path = Path(batch_results_file)
    inputs_file = batch_path.parent / f"{Path(batch_results_file).stem.replace('-results', '')}-inputs.json"
    with open(inputs_file, 'r') as f:
        inputs = json.load(f)
    with open(batch_results_file, 'r') as f:
        batch_results = [json.loads(line) for line in f]
    for result in batch_results:
        embedding = result['response']['body']['data'][0]['embedding']
        custom_id = result['custom_id']
        text = inputs[custom_id]
        text_hash = create_hash(text.strip().lower())
        text_ref = f'{col}/{text_hash}'
        values = {
            'text': text,
            'embedding': embedding,
            'model': model,
            'dimensions': len(embedding),
        }
        update_document(text_ref, values, database=db)
        if verbose:
            print(f'Saved embedding: {text}')
