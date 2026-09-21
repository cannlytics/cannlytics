"""
AI Embeddings | Cannlytics
Copyright (c) 2024-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/8/2024
Updated: 6/12/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Embedding creation, retrieval, caching, and batch processing.
    Supports OpenAI's text-embedding-3-small and text-embedding-3-large
    models with configurable dimension reduction for Firestore vector
    search compatibility (max 2048 dimensions).

    Three-tier lookup: local JSONL cache → Firestore → OpenAI API.
    Batch API support for bulk embedding creation at 50% cost reduction.

Configuration:
    Default model:      text-embedding-3-large
    Default dimensions: 1024
    Firestore max:      2048 dimensions
    Distance metric:    dot_product (OpenAI embeddings are L2-normalized)

Cost Reference (per 1M tokens, March 2026):
    text-embedding-3-small: $0.020 ($0.010 batch)
    text-embedding-3-large: $0.130 ($0.065 batch)
    For 30K unique business names (~150K tokens):
        small: $0.0015 batch | large: $0.0098 batch
"""
# Standard imports:
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# External imports:
from openai import OpenAI
import pandas as pd

# Internal imports:
from cannlytics.auth import sha256_hmac
from cannlytics.firebase import (
    initialize_firebase,
    get_document,
    update_document,
)
from cannlytics.utils import convert_to_numeric

logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

# Firestore Enterprise vector search limit.
FIRESTORE_MAX_EMBEDDING_DIMS: int = 2048

# Default embedding configuration.
# text-embedding-3-large@1024 outperforms text-embedding-3-small@1536
# per OpenAI's published MTEB benchmarks, at half the storage cost.
DEFAULT_MODEL: str = 'text-embedding-3-large'
DEFAULT_DIMENSIONS: int = 1024

# Firestore collection for cached embeddings.
DEFAULT_EMBEDDING_COLLECTION: str = 'public/ai/embeddings'

# Batch API endpoint.
BATCH_ENDPOINT: str = '/v1/embeddings'

# ============================================================================
# Core Embedding Functions
# ============================================================================

def create_embedding(
    text: str,
    model: str = DEFAULT_MODEL,
    dimensions: Optional[int] = DEFAULT_DIMENSIONS,
    client: Optional[OpenAI] = None,
) -> list[float]:
    """Create an embedding vector for a text string.

    Args:
        text: Input text to embed.
        model: OpenAI embedding model ID.
        dimensions: Output dimension count. Must be ≤2048 for Firestore
            vector search. Pass None for the model's native dimensions
            (1536 for small, 3072 for large).
        client: OpenAI client instance (created if not provided).

    Returns:
        List of floats representing the embedding vector.

    Raises:
        ValueError: If dimensions exceeds Firestore limit.
    """
    if dimensions is not None and dimensions > FIRESTORE_MAX_EMBEDDING_DIMS:
        raise ValueError(
            f'dimensions={dimensions} exceeds Firestore max of '
            f'{FIRESTORE_MAX_EMBEDDING_DIMS}. Use dimensions≤2048 or '
            f'pass dimensions=None to skip Firestore vector search.'
        )
    if client is None:
        client = OpenAI()
    text = text.replace('\n', ' ').strip()
    if not text:
        return []

    kwargs: dict[str, Any] = {
        'input': [text],
        'model': model,
    }
    if dimensions is not None:
        kwargs['dimensions'] = dimensions
    response = client.embeddings.create(**kwargs)
    return response.data[0].embedding

def get_embedding(
    text: str,
    model: str = DEFAULT_MODEL,
    dimensions: Optional[int] = DEFAULT_DIMENSIONS,
    db: Any = None,
    client: Optional[OpenAI] = None,
    cache: Any = None,
    use_db: bool = True,
    verbose: bool = False,
) -> list[float]:
    """Retrieve an embedding with three-tier lookup.

    Lookup order:
        1. Local JSONL cache (Bogart) — instant, free
        2. Firestore document — fast, minimal read cost
        3. OpenAI API — creates and caches the embedding

    The cache key is a SHA-256 HMAC of the lowercased, stripped text
    concatenated with the model name and dimension count, ensuring
    that different model/dimension configurations don't collide.

    Args:
        text: Input text to embed.
        model: OpenAI embedding model ID.
        dimensions: Output dimension count (≤2048 for Firestore).
        db: Firestore client (initialized if needed and use_db=True).
        client: OpenAI client (initialized if needed).
        cache: Bogart JSONL cache instance for local caching.
        use_db: Whether to check/write Firestore (disable for offline).
        verbose: Print cache hit/miss information.

    Returns:
        Embedding vector as a list of floats.
    """
    if not text or (isinstance(text, float) and pd.isna(text)):
        return []

    # Build a cache key that includes model + dimensions to prevent
    # collisions between different embedding configurations.
    dim_str = str(dimensions) if dimensions else 'native'
    cache_key = sha256_hmac(f'{text.strip().lower()}|{model}|{dim_str}', '')

    # --- Tier 1: Local cache ---
    if cache is not None:
        cached = cache.get(cache_key)
        if cached is not None:
            embedding = cached.get('embedding')
            if isinstance(embedding, list) and len(embedding) > 0:
                if verbose:
                    logger.info('Cache hit (local): %s', cache_key[:12])
                return embedding

    # --- Tier 2: Firestore ---
    firestore_ref = f'{DEFAULT_EMBEDDING_COLLECTION}/{cache_key}'
    if use_db:
        if db is None:
            db = initialize_firebase()
        doc = get_document(firestore_ref, database=db)
        if doc:
            embedding = doc.get('embedding')
            if isinstance(embedding, list) and len(embedding) > 0:
                if verbose:
                    logger.info('Cache hit (Firestore): %s', firestore_ref)
                # Backfill local cache.
                if cache is not None:
                    cache.set(cache_key, doc)
                return embedding

    # --- Tier 3: OpenAI API ---
    embedding = create_embedding(
        text, model=model, dimensions=dimensions, client=client,
    )

    # Persist to both caches.
    values = {
        'text': text,
        'embedding': embedding,
        'model': model,
        'dimensions': len(embedding),
    }
    if use_db:
        update_document(firestore_ref, values, database=db)
    if cache is not None:
        cache.set(cache_key, values)
    if verbose:
        logger.info('Created embedding via API: %s (%d dims)', text[:40], len(embedding))
    return embedding

def get_results_embedding(
    results: dict,
    standard_analytes: list[str],
) -> list[float]:
    """Create a fixed-length numeric embedding from analyte results.

    This produces a non-neural embedding where each dimension
    corresponds to a specific analyte concentration, enabling
    chemical-profile similarity search.

    Args:
        results: Dict mapping analyte names to concentration values.
        standard_analytes: Ordered list of analyte names defining
            the embedding dimensions.

    Returns:
        List of floats (one per standard analyte, 0.0 for missing).
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

# ============================================================================
# Batch Embedding Operations
# ============================================================================

def create_batch_file(
    df: pd.DataFrame,
    text_field: str,
    batch_file: str,
    custom_id_field: str = 'id',
    model: str = DEFAULT_MODEL,
    dimensions: Optional[int] = DEFAULT_DIMENSIONS,
    cache: Any = None,
) -> tuple[str, int, int]:
    """Create a JSONL batch file for the OpenAI Batch API.

    Skips texts that already exist in the local cache, saving API cost.

    Args:
        df: DataFrame containing the text data.
        text_field: Column name containing text to embed.
        batch_file: Output path for the JSONL batch file.
        custom_id_field: Column to use as the custom_id in batch results.
        model: Embedding model ID.
        dimensions: Output dimensions (≤2048).
        cache: Optional Bogart cache to skip already-embedded texts.

    Returns:
        Tuple of (inputs_file_path, total_written, total_skipped).
    """
    batch_path = Path(batch_file)
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    inputs_file = str(batch_path.parent / f'{batch_path.stem}-inputs.json')

    dim_str = str(dimensions) if dimensions else 'native'
    inputs: dict[str, str] = {}
    written = 0
    skipped = 0

    with open(batch_file, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            text = row.get(text_field)
            if pd.isna(text) or not str(text).strip():
                continue
            text = str(text).strip()

            # Check cache to avoid re-embedding.
            if cache is not None:
                cache_key = sha256_hmac(f'{text.lower()}|{model}|{dim_str}', '')
                cached = cache.get(cache_key)
                if cached is not None and isinstance(cached.get('embedding'), list):
                    skipped += 1
                    continue

            custom_id = str(row.get(custom_id_field, f'row-{written}'))
            body: dict[str, Any] = {
                'model': model,
                'input': text,
                'encoding_format': 'float',
            }
            if dimensions is not None:
                body['dimensions'] = dimensions

            request = {
                'custom_id': custom_id,
                'method': 'POST',
                'url': BATCH_ENDPOINT,
                'body': body,
            }
            f.write(json.dumps(request, ensure_ascii=False) + '\n')
            inputs[custom_id] = text
            written += 1

    # Save the inputs mapping for result processing.
    with open(inputs_file, 'w', encoding='utf-8') as f:
        json.dump(inputs, f, ensure_ascii=False, indent=2)

    return inputs_file, written, skipped

def submit_batch_job(
    client: OpenAI,
    batch_file: str,
    verbose: bool = True,
) -> Any:
    """Submit a batch file to the OpenAI Batch API.

    Args:
        client: OpenAI client.
        batch_file: Path to the JSONL batch file.
        verbose: Print progress.

    Returns:
        The Batch job object (check .status for completion).
    """
    with open(batch_file, 'rb') as f:
        uploaded = client.files.create(file=f, purpose='batch')
    if verbose:
        logger.info('Uploaded batch file: %s', uploaded.id)

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    job = client.batches.create(
        input_file_id=uploaded.id,
        endpoint=BATCH_ENDPOINT,
        completion_window='24h',
        metadata={'description': f'Cannlytics embeddings {timestamp}'},
    )
    if verbose:
        logger.info('Batch job submitted: %s (status: %s)', job.id, job.status)
    return job

def poll_batch_job(
    client: OpenAI,
    job_id: str,
    poll_interval: int = 300,
    verbose: bool = True,
) -> Any:
    """Poll a batch job until completion.

    Args:
        client: OpenAI client.
        job_id: The batch job ID.
        poll_interval: Seconds between status checks (default 5 min).
        verbose: Print status updates.

    Returns:
        The completed Batch job object.

    Raises:
        RuntimeError: If the batch job fails or is cancelled.
    """
    from time import sleep

    while True:
        job = client.batches.retrieve(job_id)
        if verbose:
            logger.info('Job %s: %s', job_id, job.status)

        if job.status == 'completed':
            return job
        if job.status in ('failed', 'cancelled', 'expired'):
            raise RuntimeError(
                f'Batch job {job_id} ended with status: {job.status}. '
                f'Errors: {getattr(job, "errors", "unknown")}'
            )
        sleep(poll_interval)

def process_batch_results(
    client: OpenAI,
    job: Any,
    results_file: str,
    model: str = DEFAULT_MODEL,
    dimensions: Optional[int] = DEFAULT_DIMENSIONS,
    cache: Any = None,
    db: Any = None,
    upload_to_firestore: bool = True,
    verbose: bool = True,
) -> int:
    """Download and process batch embedding results.

    Saves each embedding to the local cache and optionally to Firestore.

    Args:
        client: OpenAI client.
        job: Completed Batch job object.
        results_file: Path to save the raw JSONL results.
        model: Model name (for cache key generation).
        dimensions: Dimensions used (for cache key generation).
        cache: Optional Bogart cache for local persistence.
        db: Optional Firestore client.
        upload_to_firestore: Whether to write embeddings to Firestore.
        verbose: Print progress.

    Returns:
        Number of embeddings processed.
    """
    # Download results.
    output_file_id = job.output_file_id
    if not output_file_id:
        logger.warning('No output file on completed job.')
        return 0

    content = client.files.content(output_file_id)
    results_path = Path(results_file)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    content.write_to_file(str(results_path))
    if verbose:
        logger.info('Downloaded results to %s', results_file)

    # Load the inputs mapping.
    inputs_file = results_path.parent / f'{results_path.stem.replace("-results", "")}-inputs.json'
    inputs: dict[str, str] = {}
    if inputs_file.exists():
        with open(inputs_file, 'r', encoding='utf-8') as f:
            inputs = json.load(f)

    # Process each result.
    dim_str = str(dimensions) if dimensions else 'native'
    processed = 0
    errors = 0

    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line)
            custom_id = result.get('custom_id', '')

            # Check for API errors in the result.
            response = result.get('response', {})
            if response.get('status_code') != 200:
                errors += 1
                if verbose:
                    error_body = response.get('body', {}).get('error', {})
                    logger.warning('Batch error for %s: %s', custom_id, error_body)
                continue

            embedding = response['body']['data'][0]['embedding']
            text = inputs.get(custom_id, custom_id)
            cache_key = sha256_hmac(f'{text.strip().lower()}|{model}|{dim_str}', '')

            values = {
                'text': text,
                'embedding': embedding,
                'model': model,
                'dimensions': len(embedding),
            }

            # Save to local cache.
            if cache is not None:
                cache.set(cache_key, values)

            # Save to Firestore.
            if upload_to_firestore and db is not None:
                ref = f'{DEFAULT_EMBEDDING_COLLECTION}/{cache_key}'
                update_document(ref, values, database=db)

            processed += 1

    if verbose:
        logger.info('Processed %s embeddings (%s errors)', f'{processed:,}', errors)
    return processed

# ============================================================================
# Convenience: Full Batch Pipeline
# ============================================================================

def create_embeddings_batch(
    df: pd.DataFrame,
    text_field: str,
    output_dir: str,
    custom_id_field: str = 'id',
    model: str = DEFAULT_MODEL,
    dimensions: Optional[int] = DEFAULT_DIMENSIONS,
    cache: Any = None,
    db: Any = None,
    client: Optional[OpenAI] = None,
    upload_to_firestore: bool = True,
    poll_interval: int = 300,
    verbose: bool = True,
) -> int:
    """End-to-end batch embedding creation pipeline.

    Creates the batch file (skipping cached texts), submits to OpenAI's
    Batch API, polls for completion, downloads results, and caches
    all embeddings locally and in Firestore.

    Args:
        df: DataFrame with text data.
        text_field: Column name containing text to embed.
        output_dir: Directory for batch files and results.
        custom_id_field: Column for batch custom IDs.
        model: Embedding model.
        dimensions: Output dimensions (≤2048 for Firestore).
        cache: Bogart cache instance.
        db: Firestore client.
        client: OpenAI client.
        upload_to_firestore: Write embeddings to Firestore.
        poll_interval: Seconds between batch status checks.
        verbose: Print progress.

    Returns:
        Total embeddings processed (from API + already cached).
    """
    if client is None:
        client = OpenAI()

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    field_slug = text_field.replace('_', '-')
    batch_file = str(Path(output_dir) / f'{field_slug}-embeddings-{timestamp}.jsonl')
    results_file = str(Path(output_dir) / f'{field_slug}-embeddings-{timestamp}-results.jsonl')

    # Step 1: Create batch file.
    if verbose:
        logger.info('Creating batch file for field: %s', text_field)
    inputs_file, written, skipped = create_batch_file(
        df, text_field, batch_file,
        custom_id_field=custom_id_field,
        model=model, dimensions=dimensions, cache=cache,
    )
    if verbose:
        logger.info('Batch file: %s to embed, %s cached (skipped)', f'{written:,}', f'{skipped:,}')

    if written == 0:
        if verbose:
            logger.info('All %s texts already cached.', f'{skipped:,}')
        return skipped

    # Step 2: Submit batch job.
    job = submit_batch_job(client, batch_file, verbose=verbose)

    # Step 3: Poll for completion.
    if verbose:
        logger.info('Polling every %ss...', poll_interval)
    job = poll_batch_job(client, job.id, poll_interval=poll_interval, verbose=verbose)

    # Step 4: Process results.
    processed = process_batch_results(
        client, job, results_file,
        model=model, dimensions=dimensions,
        cache=cache, db=db,
        upload_to_firestore=upload_to_firestore,
        verbose=verbose,
    )

    return processed + skipped