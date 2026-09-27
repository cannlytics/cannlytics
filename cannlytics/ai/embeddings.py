"""
AI Embeddings | Cannlytics
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/8/2024
Updated: 9/21/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Embedding creation, retrieval, caching, batch processing, and the
    vector arithmetic to use the results. Two providers are supported:

    - OpenAI (``text-embedding-3-small``, ``text-embedding-3-large``):
      text, with the Batch API for bulk jobs at half price.
    - Gemini (``gemini-embedding-001`` for text; ``gemini-embedding-2``
      for text, images, audio, video, and PDFs in one vector space).

    The provider is chosen by the model name, and its SDK is imported
    on first use, so either provider works without the other installed.

        from cannlytics.ai import create_embedding, create_pdf_embedding

        vector = create_embedding('Blue Dream', model='gemini-embedding-2')
        coa = create_pdf_embedding('coa.pdf')      # one vector per COA
        coa['embedding'], coa['page_embeddings'], coa['pdf_hash']

    Text lookup is three-tier: local JSONL cache, then Firestore, then
    the provider. Firestore is optional and needs the ``firebase``
    extra only when ``use_db=True``.

Configuration:
    Default text model:       text-embedding-3-large at 1024 dimensions
    Default multimodal model: gemini-embedding-2 at 1536 dimensions
    Firestore vector maximum: 2048 dimensions
    Distance metric:          dot product (vectors are L2-normalized)

    Embedding spaces are incompatible across models. Vectors from two
    models can never be compared; re-embed when changing model.

Environment:
    OPENAI_API_KEY                       read by the OpenAI SDK
    GEMINI_API_KEY or GOOGLE_API_KEY     read by the Google GenAI SDK
"""
# Standard imports:
from __future__ import annotations

import hashlib
import hmac
import io
import json
import logging
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Union
from collections.abc import Iterable, Sequence

# External imports:
import numpy as np
import pandas as pd

# Internal imports:
from cannlytics.utils import convert_to_numeric
from cannlytics.utils.hashing import hash_bytes, hash_json

logger = logging.getLogger(__name__)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Constants                                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

# Firestore vector search limit.
FIRESTORE_MAX_EMBEDDING_DIMS: int = 2048

# Default text embedding configuration. text-embedding-3-large at 1024
# outperforms text-embedding-3-small at 1536 on OpenAI's published MTEB
# results, at two-thirds of the storage.
DEFAULT_MODEL: str = 'text-embedding-3-large'
DEFAULT_DIMENSIONS: int = 1024

# Default file embedding configuration. 1536 is the largest size Google
# recommends that still fits a Firestore vector field.
DEFAULT_MULTIMODAL_MODEL: str = 'gemini-embedding-2'
DEFAULT_MULTIMODAL_DIMENSIONS: int = 1536

# Firestore collection for cached embeddings.
DEFAULT_EMBEDDING_COLLECTION: str = 'public/ai/embeddings'

# OpenAI Batch API endpoint.
BATCH_ENDPOINT: str = '/v1/embeddings'

# Texts per request. OpenAI accepts 2,048 inputs per call; Gemini's
# ceiling is not stated in its embeddings guide, so stay conservative.
OPENAI_MAX_INPUTS: int = 1000
GEMINI_MAX_INPUTS: int = 100

# Gemini accepts one PDF of at most six pages per request and
# recommends one page per request for the best quality.
GEMINI_MAX_PDF_PAGES: int = 6

# Known models. An unknown model still works: its provider is inferred
# from its name and its dimensions are passed through unvalidated, so a
# new model never needs a package release.
EMBEDDING_MODELS: dict[str, dict[str, Any]] = {
    'text-embedding-3-small': {
        'provider': 'openai',
        'native_dimensions': 1536,
        'min_dimensions': 1,
        'max_dimensions': 1536,
        'modalities': ('text',),
        'task_style': None,
        'normalize_truncated': False,
    },
    'text-embedding-3-large': {
        'provider': 'openai',
        'native_dimensions': 3072,
        'min_dimensions': 1,
        'max_dimensions': 3072,
        'modalities': ('text',),
        'task_style': None,
        'normalize_truncated': False,
    },
    'gemini-embedding-001': {
        'provider': 'gemini',
        'native_dimensions': 3072,
        'min_dimensions': 128,
        'max_dimensions': 3072,
        'modalities': ('text',),
        'task_style': 'config',
        # Only the native 3072 dimensions arrive normalized.
        'normalize_truncated': True,
    },
    'gemini-embedding-2': {
        'provider': 'gemini',
        'native_dimensions': 3072,
        'min_dimensions': 128,
        'max_dimensions': 3072,
        'modalities': ('text', 'image', 'audio', 'video', 'pdf'),
        'task_style': 'prompt',
        'normalize_truncated': False,
    },
}

# Task hints. Gemini Embedding 001 takes `task_type` in its config;
# Gemini Embedding 2 takes an instruction in the prompt; OpenAI has no
# task concept and ignores the hint.
EMBEDDING_TASKS: dict[str, dict[str, str]] = {
    'search_query': {
        'task_type': 'RETRIEVAL_QUERY',
        'prompt': 'task: search result | query: {content}',
    },
    'search_document': {
        'task_type': 'RETRIEVAL_DOCUMENT',
        'prompt': 'title: {title} | text: {content}',
    },
    'question_answering': {
        'task_type': 'QUESTION_ANSWERING',
        'prompt': 'task: question answering | query: {content}',
    },
    'fact_checking': {
        'task_type': 'FACT_VERIFICATION',
        'prompt': 'task: fact checking | query: {content}',
    },
    'code_retrieval': {
        'task_type': 'CODE_RETRIEVAL_QUERY',
        'prompt': 'task: code retrieval | query: {content}',
    },
    'classification': {
        'task_type': 'CLASSIFICATION',
        'prompt': 'task: classification | query: {content}',
    },
    'clustering': {
        'task_type': 'CLUSTERING',
        'prompt': 'task: clustering | query: {content}',
    },
    'similarity': {
        'task_type': 'SEMANTIC_SIMILARITY',
        'prompt': 'task: sentence similarity | query: {content}',
    },
}

# File types Gemini Embedding 2 accepts, by extension.
MIME_TYPES: dict[str, str] = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.pdf': 'application/pdf',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
}

Vector = list[float]
FileSource = Union[str, 'os.PathLike[str]', bytes]

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Optional services, imported on first use                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def _firebase() -> Any:
    """Import the Firestore helpers (needs the `firebase` extra)."""
    try:
        from cannlytics import firebase
    except ImportError as error:
        raise ImportError(
            'Caching embeddings in Firestore requires the `firebase` extra. '
            'Install it with:\n\n    pip install "cannlytics[firebase]"\n\n'
            'or pass use_db=False.'
        ) from error
    return firebase

def initialize_firebase(*args: Any, **kwargs: Any) -> Any:
    """Initialize Firestore. Resolved lazily; see ``cannlytics.firebase``."""
    return _firebase().initialize_firebase(*args, **kwargs)

def get_document(*args: Any, **kwargs: Any) -> Any:
    """Read a Firestore document. Resolved lazily."""
    return _firebase().get_document(*args, **kwargs)

def update_document(*args: Any, **kwargs: Any) -> Any:
    """Write a Firestore document. Resolved lazily."""
    return _firebase().update_document(*args, **kwargs)

def get_embedding_provider(model: str) -> str:
    """Name the provider that serves a model.

    Args:
        model: An embedding model ID.

    Returns:
        ``'openai'`` or ``'gemini'``.

    Raises:
        ValueError: If the model is unknown and its name gives no hint.
    """
    if model in EMBEDDING_MODELS:
        return EMBEDDING_MODELS[model]['provider']
    name = model.lower().split('/')[-1]
    if name.startswith(('gemini', 'text-embedding-00', 'embedding-00')):
        return 'gemini'
    if name.startswith('text-embedding'):
        return 'openai'
    raise ValueError(
        f'Cannot infer the provider of embedding model {model!r}. '
        f'Known models: {sorted(EMBEDDING_MODELS)}.'
    )

def create_embedding_client(provider: str = 'openai', api_key: str | None = None) -> Any:
    """Create a provider SDK client.

    Args:
        provider: ``'openai'`` or ``'gemini'``.
        api_key: The API key. Defaults to the SDK's own environment
            variable (``OPENAI_API_KEY``; ``GEMINI_API_KEY`` or
            ``GOOGLE_API_KEY``).

    Returns:
        An ``openai.OpenAI`` or ``google.genai.Client`` instance.

    Raises:
        ImportError: If the provider's SDK is not installed.
        ValueError: If the provider is unknown.
    """
    kwargs = {'api_key': api_key} if api_key else {}
    try:
        if provider == 'openai':
            from openai import OpenAI
            return OpenAI(**kwargs)
        if provider == 'gemini':
            from google import genai
            return genai.Client(**kwargs)
    except ImportError as error:
        raise ImportError(
            f'{provider} embeddings require the `ai` extra. Install it with:'
            '\n\n    pip install "cannlytics[ai]"\n'
        ) from error
    raise ValueError(f"Unknown embedding provider: {provider!r}. Use 'openai' or 'gemini'.")

def _genai_types() -> Any:
    """Import ``google.genai.types`` (needs the `ai` extra)."""
    try:
        from google.genai import types
    except ImportError as error:
        raise ImportError(
            'Gemini embeddings require the `ai` extra. Install it with:'
            '\n\n    pip install "cannlytics[ai]"\n'
        ) from error
    return types

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Validation, keys, and task prompts                               ║
# ╚══════════════════════════════════════════════════════════════════╝

def _validate_dimensions(model: str, dimensions: int | None) -> None:
    """Reject a dimension count the model cannot produce."""
    spec = EMBEDDING_MODELS.get(model)
    if spec is None or dimensions is None:
        return
    if not spec['min_dimensions'] <= dimensions <= spec['max_dimensions']:
        raise ValueError(
            f'{model} supports {spec["min_dimensions"]} to '
            f'{spec["max_dimensions"]} dimensions, got {dimensions}.'
        )

def _validate_firestore_dimensions(model: str, dimensions: int | None) -> None:
    """Reject a vector too large for a Firestore vector field."""
    size = dimensions
    if size is None:
        size = EMBEDDING_MODELS.get(model, {}).get('native_dimensions')
    if size is not None and size > FIRESTORE_MAX_EMBEDDING_DIMS:
        raise ValueError(
            f'{size} dimensions exceeds the Firestore maximum of '
            f'{FIRESTORE_MAX_EMBEDDING_DIMS}. Pass dimensions<='
            f'{FIRESTORE_MAX_EMBEDDING_DIMS}, or use_db=False.'
        )

def _validate_task(task: str | None) -> None:
    if task is not None and task not in EMBEDDING_TASKS:
        raise ValueError(f'Unknown task: {task!r}. Options: {sorted(EMBEDDING_TASKS)}.')

def format_task_prompt(text: str, task: str | None, title: str | None = None) -> str:
    """Add a Gemini Embedding 2 task instruction to a text.

    Use the same task for the stored side and the query side of a
    comparison. Retrieval is the asymmetric case: documents are embedded
    with ``'search_document'`` and queries with ``'search_query'``.

    Args:
        text: The content to embed.
        task: A key of ``EMBEDDING_TASKS``, or ``None`` for no change.
        title: Document title for ``'search_document'``.

    Returns:
        The formatted prompt.

    Raises:
        ValueError: If the task is unknown.
    """
    _validate_task(task)
    if task is None:
        return text
    return EMBEDDING_TASKS[task]['prompt'].format(content=text, title=title or 'none')

def _normalize_text(text: str) -> str:
    return text.strip().lower()

def embedding_key(
        content: str,
        model: str,
        dimensions: int | None,
        task: str | None = None,
        kind: str = 'text',
    ) -> str:
    """Compute the cache key (SHA-256) of an embedding.

    The key covers everything that changes the vector: the content, the
    model, the dimension count, and the task. For text, ``content`` is
    the stripped, lowercased string. For a file it is the SHA-256 of
    the file's bytes, so a COA's embedding key derives from its
    ``pdf_hash``.

    Args:
        content: Normalized text, or a file's SHA-256.
        model: The embedding model ID.
        dimensions: The output dimension count, or ``None`` for native.
        task: The task hint, if any.
        kind: ``'text'`` or ``'file'``.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    return hash_json({
        'content': content,
        'dimensions': dimensions if dimensions else 'native',
        'kind': kind,
        'model': model,
        'task': task or '',
        'version': 1,
    })

def legacy_embedding_key(text: str, model: str, dimensions: int | None) -> str:
    """Compute the cache key embeddings were stored under before 1.0.0.

    The original key was ``sha256_hmac(f'{text}|{model}|{dims}', '')``:
    an HMAC keyed by the text with an empty message. It is reproduced
    exactly so that existing local and Firestore caches still hit.

    Args:
        text: The text that was embedded.
        model: The embedding model ID.
        dimensions: The output dimension count, or ``None`` for native.

    Returns:
        Hex-encoded HMAC-SHA256 digest.
    """
    dim_str = str(dimensions) if dimensions else 'native'
    secret = f'{_normalize_text(text)}|{model}|{dim_str}'
    return hmac.new(secret.encode('utf-8'), b'', hashlib.sha256).hexdigest()

def _text_keys(
        text: str,
        model: str,
        dimensions: int | None,
        task: str | None,
        legacy_keys: bool,
    ) -> list[str]:
    """List the keys a text embedding may be cached under, canonical first."""
    keys = [embedding_key(_normalize_text(text), model, dimensions, task=task)]
    if legacy_keys and task is None:
        keys.append(legacy_embedding_key(text, model, dimensions))
    return keys

def _cached_embedding(record: Any) -> Vector | None:
    """Return the vector in a cache record, if it holds a usable one."""
    if isinstance(record, dict):
        embedding = record.get('embedding')
        if isinstance(embedding, list) and embedding:
            return embedding
    return None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Vector arithmetic                                                ║
# ╚══════════════════════════════════════════════════════════════════╝

def normalize_embedding(embedding: Sequence[float]) -> Vector:
    """Scale a vector to unit length, so dot product equals cosine.

    Args:
        embedding: The vector.

    Returns:
        The unit vector. A zero vector is returned unchanged.
    """
    vector = np.asarray(embedding, dtype=float)
    norm = np.linalg.norm(vector)
    return (vector / norm if norm else vector).tolist()

def aggregate_embeddings(
        embeddings: Sequence[Sequence[float]],
        weights: Sequence[float] | None = None,
        normalize: bool = True,
    ) -> Vector:
    """Combine several vectors into one by (weighted) averaging.

    This is how page embeddings become a document embedding, and how
    several photos of a strain become one strain embedding.

    Args:
        embeddings: Vectors of equal length.
        weights: One weight per vector. Defaults to equal weights.
        normalize: Rescale the average to unit length.

    Returns:
        The combined vector, or ``[]`` if no vectors were given.

    Raises:
        ValueError: If the vectors differ in length.
    """
    vectors = [v for v in embeddings if v is not None and len(v)]
    if not vectors:
        return []
    if len({len(v) for v in vectors}) > 1:
        raise ValueError('Embeddings must share one dimension count to be aggregated.')
    if weights is not None and len(weights) != len(vectors):
        raise ValueError('Provide one weight per non-empty embedding.')
    mean = np.average(np.asarray(vectors, dtype=float), axis=0, weights=weights)
    return normalize_embedding(mean) if normalize else mean.tolist()

def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Calculate the cosine similarity of two vectors (-1 to 1)."""
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)
    return float(x @ y / denominator) if denominator else 0.0

def find_similar(
        query: Sequence[float],
        embeddings: Sequence[Sequence[float]],
        k: int = 5,
    ) -> list[tuple[int, float]]:
    """Rank stored vectors by cosine similarity to a query vector.

    Exact search, suited to tens of thousands of vectors in memory. Use
    a vector index (Firestore ``find_nearest``) beyond that.

    Args:
        query: The query vector.
        embeddings: The stored vectors, one per row.
        k: How many matches to return.

    Returns:
        ``(row index, similarity)`` pairs, most similar first.
    """
    matrix = np.asarray(embeddings, dtype=float)
    if matrix.size == 0:
        return []
    vector = np.asarray(query, dtype=float)
    norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(vector)
    with np.errstate(divide='ignore', invalid='ignore'):
        scores = np.where(norms > 0, matrix @ vector / norms, 0.0)
    order = np.argsort(-scores, kind='stable')[:k]
    return [(int(i), float(scores[i])) for i in order]

def project_embeddings(
        embeddings: Sequence[Sequence[float]],
        n_components: int = 2,
    ) -> tuple[np.ndarray, np.ndarray]:
    """Project vectors to 2-D or 3-D with PCA, for plotting.

    Computed with a singular value decomposition, so it needs no
    machine-learning dependency. Components are sign-normalized, which
    makes the projection reproducible from run to run.

    Args:
        embeddings: The vectors, one per row.
        n_components: Output dimensions (2 or 3 for a plot).

    Returns:
        The coordinates (rows x ``n_components``) and the share of
        variance each component explains.

    Raises:
        ValueError: If there are fewer rows or columns than components.
    """
    matrix = np.asarray(embeddings, dtype=float)
    if matrix.ndim != 2 or min(matrix.shape) < n_components:
        raise ValueError(
            f'Need at least {n_components} vectors of at least '
            f'{n_components} dimensions, got shape {matrix.shape}.'
        )
    centered = matrix - matrix.mean(axis=0)
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    # Fix each component's sign by its largest loading.
    signs = np.sign(vt[np.arange(len(vt)), np.abs(vt).argmax(axis=1)])
    signs[signs == 0] = 1.0
    coordinates = (u * s * signs)[:, :n_components]
    variance = s ** 2
    total = variance.sum()
    explained = variance[:n_components] / total if total else np.zeros(n_components)
    return coordinates, explained

def score_outliers(
        embeddings: Sequence[Sequence[float]],
        groups: Sequence[Any] | None = None,
    ) -> np.ndarray:
    """Score how unusual each vector is within its group.

    Each vector's cosine distance to its group's centroid is converted
    to a robust z-score (median and MAD, so the outliers being hunted do
    not distort the scale). Grouping COA embeddings by lab asks "which
    of this lab's COAs do not look like this lab's COAs", which is how
    an R&D or otherwise non-standard certificate stands out. Distances
    are one-sided, so a few ordinary documents stray past 3.5; rank by
    score and review from the top rather than applying a hard cut-off.

    Args:
        embeddings: The vectors, one per row.
        groups: One label per row. Defaults to a single group.

    Returns:
        One score per row. A group too small or too uniform to have a
        scale scores ``0.0``.
    """
    matrix = np.asarray(embeddings, dtype=float)
    scores = np.zeros(len(matrix))
    if matrix.size == 0:
        return scores
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    unit = np.divide(matrix, norms, out=np.zeros_like(matrix), where=norms > 0)
    labels = np.zeros(len(matrix), dtype=int) if groups is None else np.asarray(groups)
    for label in pd.unique(labels):
        rows = np.flatnonzero(labels == label)
        centroid = unit[rows].mean(axis=0)
        centroid_norm = np.linalg.norm(centroid)
        if len(rows) < 3 or not centroid_norm:
            continue
        distances = 1.0 - unit[rows] @ (centroid / centroid_norm)
        median = np.median(distances)
        mad = np.median(np.abs(distances - median))
        if mad > 0:
            # 0.6745 scales the MAD to a standard deviation under normality.
            scores[rows] = 0.6745 * (distances - median) / mad
    return scores

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Provider calls                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

def _embed_openai(client: Any, model: str, texts: list[str], dimensions: int | None) -> list[Vector]:
    kwargs: dict[str, Any] = {'input': texts, 'model': model}
    if dimensions is not None:
        kwargs['dimensions'] = dimensions
    response = client.embeddings.create(**kwargs)
    return [list(item.embedding) for item in response.data]

def _embed_gemini(
        client: Any,
        model: str,
        contents: Any,
        dimensions: int | None,
        task_type: str | None = None,
    ) -> list[Vector]:
    types = _genai_types()
    options: dict[str, Any] = {}
    if dimensions is not None:
        options['output_dimensionality'] = dimensions
    if task_type is not None:
        options['task_type'] = task_type
    config = types.EmbedContentConfig(**options) if options else None
    result = client.models.embed_content(model=model, contents=contents, config=config)
    vectors = [list(item.values) for item in result.embeddings]
    spec = EMBEDDING_MODELS.get(model, {})
    truncated = dimensions is not None and dimensions != spec.get('native_dimensions')
    if truncated and spec.get('normalize_truncated'):
        vectors = [normalize_embedding(vector) for vector in vectors]
    return vectors

def _embed_texts(
        texts: list[str],
        model: str,
        dimensions: int | None,
        client: Any,
        task: str | None,
        title: str | None,
    ) -> list[Vector]:
    """Embed non-empty, cleaned texts in one request."""
    provider = get_embedding_provider(model)
    if provider == 'openai':
        return _embed_openai(client, model, texts, dimensions)
    style = EMBEDDING_MODELS.get(model, {}).get('task_style', 'prompt')
    if style == 'config':
        task_type = EMBEDDING_TASKS[task]['task_type'] if task else None
        return _embed_gemini(client, model, texts, dimensions, task_type=task_type)
    # Gemini Embedding 2 merges bare inputs into ONE vector; wrapping
    # each text in its own Content keeps one vector per text.
    types = _genai_types()
    contents = [
        types.Content(parts=[types.Part.from_text(text=format_task_prompt(text, task, title))])
        for text in texts
    ]
    return _embed_gemini(client, model, contents, dimensions)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Text embeddings                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

def create_embedding(
        text: str,
        model: str = DEFAULT_MODEL,
        dimensions: int | None = DEFAULT_DIMENSIONS,
        client: Any = None,
        task: str | None = None,
        title: str | None = None,
    ) -> Vector:
    """Create an embedding vector for a text string.

    Args:
        text: Input text to embed.
        model: Embedding model ID; it selects the provider.
        dimensions: Output dimension count. Pass ``None`` for the
            model's native size.
        client: Provider SDK client (created if not provided).
        task: What the vector is for; a key of ``EMBEDDING_TASKS``.
            Improves Gemini embeddings; ignored by OpenAI.
        title: Document title, used with ``task='search_document'``.

    Returns:
        The embedding vector, or ``[]`` for blank text.

    Raises:
        ValueError: If the model cannot produce ``dimensions``, or the
            task is unknown.
    """
    vectors = create_embeddings(
        [text], model=model, dimensions=dimensions, client=client, task=task, title=title,
    )
    return vectors[0]

def create_embeddings(
        texts: Iterable[str],
        model: str = DEFAULT_MODEL,
        dimensions: int | None = DEFAULT_DIMENSIONS,
        client: Any = None,
        task: str | None = None,
        title: str | None = None,
    ) -> list[Vector]:
    """Create one embedding per text, batching requests.

    Args:
        texts: Input texts.
        model: Embedding model ID; it selects the provider.
        dimensions: Output dimension count, or ``None`` for native.
        client: Provider SDK client (created if not provided).
        task: What the vectors are for; a key of ``EMBEDDING_TASKS``.
        title: Document title, used with ``task='search_document'``.

    Returns:
        One vector per input, in order. Blank inputs yield ``[]``.

    Raises:
        ValueError: If the model cannot produce ``dimensions``, or the
            task is unknown.
    """
    _validate_dimensions(model, dimensions)
    _validate_task(task)
    cleaned = [text.replace('\n', ' ').strip() if isinstance(text, str) else '' for text in texts]
    vectors: list[Vector] = [[] for _ in cleaned]
    todo = [i for i, text in enumerate(cleaned) if text]
    if not todo:
        return vectors
    provider = get_embedding_provider(model)
    if client is None:
        client = create_embedding_client(provider)
    step = OPENAI_MAX_INPUTS if provider == 'openai' else GEMINI_MAX_INPUTS
    for start in range(0, len(todo), step):
        rows = todo[start:start + step]
        batch = _embed_texts([cleaned[i] for i in rows], model, dimensions, client, task, title)
        if len(batch) != len(rows):
            raise RuntimeError(f'{model} returned {len(batch)} embeddings for {len(rows)} texts.')
        for i, vector in zip(rows, batch, strict=True):
            vectors[i] = vector
    return vectors

def get_embedding(
        text: str,
        model: str = DEFAULT_MODEL,
        dimensions: int | None = DEFAULT_DIMENSIONS,
        db: Any = None,
        client: Any = None,
        cache: Any = None,
        use_db: bool = True,
        verbose: bool = False,
        task: str | None = None,
        title: str | None = None,
        legacy_keys: bool = True,
    ) -> Vector:
    """Retrieve an embedding with three-tier lookup.

    Lookup order:
        1. Local JSONL cache (Bogart): instant, free
        2. Firestore document: fast, minimal read cost
        3. The provider API: creates and caches the embedding

    The cache key is the SHA-256 of the lowercased, stripped text with
    the model, dimension count, and task (see ``embedding_key``), so
    different configurations never collide.

    Args:
        text: Input text to embed.
        model: Embedding model ID; it selects the provider.
        dimensions: Output dimension count (<=2048 for Firestore).
        db: Firestore client (initialized if needed and use_db=True).
        client: Provider SDK client (initialized if needed).
        cache: Bogart JSONL cache instance for local caching.
        use_db: Whether to check/write Firestore (disable for offline).
        verbose: Log cache hit/miss information.
        task: What the vector is for; a key of ``EMBEDDING_TASKS``.
        title: Document title, used with ``task='search_document'``.
        legacy_keys: Also look under the pre-1.0.0 cache key, so that
            existing caches still hit. New entries always use the
            SHA-256 key.

    Returns:
        Embedding vector as a list of floats.

    Raises:
        ValueError: If ``use_db`` and the vector exceeds Firestore's
            2,048-dimension limit.
        ImportError: If ``use_db`` without the `firebase` extra.
    """
    if not text or (isinstance(text, float) and pd.isna(text)):
        return []
    if use_db:
        _validate_firestore_dimensions(model, dimensions)
    keys = _text_keys(text, model, dimensions, task, legacy_keys)
    cache_key = keys[0]

    # --- Tier 1: Local cache ---
    if cache is not None:
        for key in keys:
            embedding = _cached_embedding(cache.get(key))
            if embedding is not None:
                if verbose:
                    logger.info('Cache hit (local): %s', key[:12])
                return embedding

    # --- Tier 2: Firestore ---
    if use_db:
        if db is None:
            db = initialize_firebase()
        for key in keys:
            ref = f'{DEFAULT_EMBEDDING_COLLECTION}/{key}'
            doc = get_document(ref, database=db)
            embedding = _cached_embedding(doc)
            if embedding is not None:
                if verbose:
                    logger.info('Cache hit (Firestore): %s', ref)
                if cache is not None:
                    cache.set(cache_key, doc)
                return embedding

    # --- Tier 3: Provider API ---
    embedding = create_embedding(
        text, model=model, dimensions=dimensions, client=client, task=task, title=title,
    )

    # Persist to both caches.
    values = {
        'text': text,
        'embedding': embedding,
        'model': model,
        'dimensions': len(embedding),
    }
    if task:
        values['task'] = task
    if use_db:
        update_document(f'{DEFAULT_EMBEDDING_COLLECTION}/{cache_key}', values, database=db)
    if cache is not None:
        cache.set(cache_key, values)
    if verbose:
        logger.info('Created embedding via API: %s (%d dims)', text[:40], len(embedding))
    return embedding

def get_results_embedding(
        results: dict,
        standard_analytes: list[str],
    ) -> Vector:
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

# ╔══════════════════════════════════════════════════════════════════╗
# ║ File embeddings: images, PDFs, audio, video                      ║
# ╚══════════════════════════════════════════════════════════════════╝

def _read_source(source: FileSource, mime_type: str | None) -> tuple[bytes, str]:
    """Return a file's bytes and MIME type."""
    if isinstance(source, (bytes, bytearray)):
        if not mime_type:
            raise ValueError('mime_type is required when the source is bytes.')
        return bytes(source), mime_type
    path = Path(source)
    if mime_type is None:
        mime_type = MIME_TYPES.get(path.suffix.lower())
        if mime_type is None:
            raise ValueError(
                f'Cannot embed a {path.suffix or "extensionless"} file. '
                f'Supported: {sorted(MIME_TYPES)}. Pass mime_type to override.'
            )
    return path.read_bytes(), mime_type

def _pdf_reader(data: bytes) -> Any:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise ImportError(
            'Embedding PDFs requires `pypdf` from the `ai` extra. '
            'Install it with:\n\n    pip install "cannlytics[ai]"\n'
        ) from error
    return PdfReader(io.BytesIO(data))

def count_pdf_pages(data: bytes) -> int:
    """Count the pages of a PDF held in memory (needs ``pypdf``)."""
    return len(_pdf_reader(data).pages)

def split_pdf_pages(data: bytes, max_pages: int | None = None) -> list[bytes]:
    """Split a PDF into single-page PDFs, in memory.

    Nothing is written to disk. Gemini recommends one page per request
    for the best embedding quality, and silently truncates any request
    over 8,192 tokens, which a dense multi-page COA exceeds.

    Args:
        data: The PDF's bytes.
        max_pages: Keep only the first ``max_pages`` pages.

    Returns:
        One single-page PDF per page, in order.
    """
    pages = _pdf_reader(data).pages
    from pypdf import PdfWriter
    count = len(pages) if max_pages is None else min(max_pages, len(pages))
    documents = []
    for index in range(count):
        writer = PdfWriter()
        writer.add_page(pages[index])
        buffer = io.BytesIO()
        writer.write(buffer)
        documents.append(buffer.getvalue())
    return documents

def create_file_embedding(
        source: FileSource,
        mime_type: str | None = None,
        model: str = DEFAULT_MULTIMODAL_MODEL,
        dimensions: int | None = DEFAULT_MULTIMODAL_DIMENSIONS,
        client: Any = None,
        text: str | None = None,
    ) -> Vector:
    """Create an embedding for an image, PDF, audio, or video file.

    Files and text share one vector space, so a photo of a flower can be
    compared with another photo, with a strain description, or with a
    COA. Limits per request (Gemini Embedding 2): PNG or JPEG images;
    one PDF of at most six pages; MP3 or WAV audio up to 180 seconds;
    MP4 or MOV video up to 120 seconds; 8,192 tokens in total. For a
    whole COA use ``create_pdf_embedding``, which handles any length.

    Args:
        source: A file path, or the file's bytes.
        mime_type: The file's MIME type. Inferred from a path's
            extension; required for bytes.
        model: A multimodal embedding model ID.
        dimensions: Output dimension count, or ``None`` for native.
        client: ``google.genai.Client`` (created if not provided).
        text: Optional caption, merged with the file into ONE vector.
            Do not include a task instruction here.

    Returns:
        The embedding vector.

    Raises:
        ValueError: If the model cannot embed this kind of file, or a
            PDF exceeds the page limit.
    """
    _validate_dimensions(model, dimensions)
    data, mime_type = _read_source(source, mime_type)
    modality = 'pdf' if mime_type == 'application/pdf' else mime_type.split('/')[0]
    spec = EMBEDDING_MODELS.get(model)
    if get_embedding_provider(model) != 'gemini' or (spec and modality not in spec['modalities']):
        raise ValueError(
            f'{model} cannot embed {mime_type}. Use a multimodal model such '
            f'as {DEFAULT_MULTIMODAL_MODEL!r}.'
        )
    if modality == 'pdf':
        pages = count_pdf_pages(data)
        if pages > GEMINI_MAX_PDF_PAGES:
            raise ValueError(
                f'This PDF has {pages} pages; one request accepts at most '
                f'{GEMINI_MAX_PDF_PAGES}. Use create_pdf_embedding.'
            )
    if client is None:
        client = create_embedding_client('gemini')
    types = _genai_types()
    part = types.Part.from_bytes(data=data, mime_type=mime_type)
    contents = [text, part] if text else [part]
    return _embed_gemini(client, model, contents, dimensions)[0]

def create_pdf_embedding(
        source: FileSource,
        model: str = DEFAULT_MULTIMODAL_MODEL,
        dimensions: int | None = DEFAULT_MULTIMODAL_DIMENSIONS,
        client: Any = None,
        cache: Any = None,
        max_pages: int | None = None,
        weights: Sequence[float] | None = None,
    ) -> dict[str, Any]:
    """Create a document embedding for a PDF of any length, such as a COA.

    Each page is embedded on its own (the quality Google recommends,
    and immune to the silent 8,192-token truncation), then the page
    vectors are averaged and re-normalized into one document vector.
    The page vectors are returned too: page one of a COA is the lab's
    cover sheet and the strongest fingerprint of who issued it.

    Records are keyed by the PDF's SHA-256, the same value as
    ``pdf_hash`` in the results data, so embeddings join to lab results.

    Args:
        source: A PDF path, or the PDF's bytes.
        model: A multimodal embedding model ID.
        dimensions: Output dimension count, or ``None`` for native.
        client: ``google.genai.Client`` (created if not provided).
        cache: Bogart cache. A PDF already embedded costs nothing.
        max_pages: Embed only the first ``max_pages`` pages.
        weights: One weight per embedded page, for the average.

    Returns:
        A record with ``pdf_hash``, ``embedding``, ``page_embeddings``,
        ``pages`` (pages embedded), ``total_pages``, ``model``, and
        ``dimensions``.
    """
    _validate_dimensions(model, dimensions)
    data, _ = _read_source(source, 'application/pdf')
    pdf_hash = hash_bytes(data)
    cache_key = embedding_key(f'{pdf_hash}|{max_pages or "all"}', model, dimensions, kind='file')
    if cache is not None:
        record = cache.get(cache_key)
        if _cached_embedding(record) is not None:
            return record
    total_pages = count_pdf_pages(data)
    if client is None:
        client = create_embedding_client('gemini')
    page_embeddings = [
        create_file_embedding(
            page, mime_type='application/pdf', model=model, dimensions=dimensions, client=client,
        )
        for page in split_pdf_pages(data, max_pages=max_pages)
    ]
    embedding = aggregate_embeddings(page_embeddings, weights=weights)
    record = {
        'pdf_hash': pdf_hash,
        'embedding': embedding,
        'page_embeddings': page_embeddings,
        'pages': len(page_embeddings),
        'total_pages': total_pages,
        'model': model,
        'dimensions': len(embedding),
    }
    if cache is not None:
        cache.set(cache_key, record)
    return record

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Batch embedding operations (OpenAI Batch API)                    ║
# ╚══════════════════════════════════════════════════════════════════╝

def _require_openai_batch(model: str) -> None:
    if get_embedding_provider(model) != 'openai':
        raise ValueError(
            f'Batch jobs are implemented for OpenAI models only, not {model!r}. '
            'Use create_embeddings for Gemini.'
        )

def create_batch_file(
        df: pd.DataFrame,
        text_field: str,
        batch_file: str,
        custom_id_field: str = 'id',
        model: str = DEFAULT_MODEL,
        dimensions: int | None = DEFAULT_DIMENSIONS,
        cache: Any = None,
        legacy_keys: bool = True,
    ) -> tuple[str, int, int]:
    """Create a JSONL batch file for the OpenAI Batch API.

    Skips texts that already exist in the local cache, saving API cost.

    Args:
        df: DataFrame containing the text data.
        text_field: Column name containing text to embed.
        batch_file: Output path for the JSONL batch file.
        custom_id_field: Column to use as the custom_id in batch results.
        model: Embedding model ID.
        dimensions: Output dimensions (<=2048 for Firestore).
        cache: Optional Bogart cache to skip already-embedded texts.
        legacy_keys: Also treat texts cached under the pre-1.0.0 key
            as embedded.

    Returns:
        Tuple of (inputs_file_path, total_written, total_skipped).
    """
    _require_openai_batch(model)
    _validate_dimensions(model, dimensions)
    batch_path = Path(batch_file)
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    inputs_file = str(batch_path.parent / f'{batch_path.stem}-inputs.json')

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
                keys = _text_keys(text, model, dimensions, None, legacy_keys)
                if any(_cached_embedding(cache.get(key)) is not None for key in keys):
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
        client: Any,
        batch_file: str,
        verbose: bool = True,
    ) -> Any:
    """Submit a batch file to the OpenAI Batch API.

    Args:
        client: OpenAI client.
        batch_file: Path to the JSONL batch file.
        verbose: Log progress.

    Returns:
        The Batch job object (check .status for completion).
    """
    with open(batch_file, 'rb') as f:
        uploaded = client.files.create(file=f, purpose='batch')
    if verbose:
        logger.info('Uploaded batch file: %s', uploaded.id)

    timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')
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
        client: Any,
        job_id: str,
        poll_interval: int = 300,
        verbose: bool = True,
        timeout: float | None = 90_000,
    ) -> Any:
    """Poll a batch job until completion.

    Args:
        client: OpenAI client.
        job_id: The batch job ID.
        poll_interval: Seconds between status checks (default 5 min).
        verbose: Log status updates.
        timeout: Give up after this many seconds. The default is 25
            hours, just past the API's 24-hour completion window.
            ``None`` polls without limit.

    Returns:
        The completed Batch job object.

    Raises:
        RuntimeError: If the batch job fails or is cancelled.
        TimeoutError: If the job is still running at ``timeout``.
    """
    from time import monotonic, sleep

    started = monotonic()
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
        if timeout is not None and monotonic() - started + poll_interval > timeout:
            raise TimeoutError(
                f'Batch job {job_id} is still {job.status} after {timeout} seconds.'
            )
        sleep(poll_interval)

def process_batch_results(
        client: Any,
        job: Any,
        results_file: str,
        model: str = DEFAULT_MODEL,
        dimensions: int | None = DEFAULT_DIMENSIONS,
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
        verbose: Log progress.

    Returns:
        Number of embeddings processed.
    """
    to_firestore = upload_to_firestore and db is not None
    if to_firestore:
        _validate_firestore_dimensions(model, dimensions)

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
        with open(inputs_file, encoding='utf-8') as f:
            inputs = json.load(f)

    # Process each result.
    processed = 0
    errors = 0

    with open(results_file, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            result = json.loads(line)
            custom_id = result.get('custom_id', '')

            # Check for API errors in the result.
            response = result.get('response') or {}
            if response.get('status_code') != 200:
                errors += 1
                if verbose:
                    error_body = (response.get('body') or {}).get('error', {})
                    logger.warning('Batch error for %s: %s', custom_id, error_body)
                continue

            embedding = response['body']['data'][0]['embedding']
            text = inputs.get(custom_id, custom_id)
            cache_key = embedding_key(_normalize_text(text), model, dimensions)

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
            if to_firestore:
                ref = f'{DEFAULT_EMBEDDING_COLLECTION}/{cache_key}'
                update_document(ref, values, database=db)

            processed += 1

    if verbose:
        logger.info('Processed %s embeddings (%s errors)', f'{processed:,}', errors)
    return processed

def create_embeddings_batch(
        df: pd.DataFrame,
        text_field: str,
        output_dir: str,
        custom_id_field: str = 'id',
        model: str = DEFAULT_MODEL,
        dimensions: int | None = DEFAULT_DIMENSIONS,
        cache: Any = None,
        db: Any = None,
        client: Any = None,
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
        dimensions: Output dimensions (<=2048 for Firestore).
        cache: Bogart cache instance.
        db: Firestore client.
        client: OpenAI client.
        upload_to_firestore: Write embeddings to Firestore.
        poll_interval: Seconds between batch status checks.
        verbose: Log progress.

    Returns:
        Total embeddings processed (from API + already cached).
    """
    _require_openai_batch(model)
    if client is None:
        client = create_embedding_client('openai')

    timestamp = datetime.now(UTC).strftime('%Y%m%d-%H%M%S')
    field_slug = text_field.replace('_', '-')
    batch_file = str(Path(output_dir) / f'{field_slug}-embeddings-{timestamp}.jsonl')
    results_file = str(Path(output_dir) / f'{field_slug}-embeddings-{timestamp}-results.jsonl')

    # Step 1: Create batch file.
    if verbose:
        logger.info('Creating batch file for field: %s', text_field)
    _, written, skipped = create_batch_file(
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
