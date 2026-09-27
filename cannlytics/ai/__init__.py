"""
Cannlytics AI Initialization | Cannlytics
Copyright (c) 2025-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/20/2025
Updated: 9/21/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Embeddings for text, images, and documents. Importing this package
    needs only the core install; a provider SDK (the `ai` extra) is
    imported on the first call that reaches a provider, and Firestore
    (the `firebase` extra) only when ``use_db=True``.
"""
from .embeddings import (
    DEFAULT_DIMENSIONS,
    DEFAULT_MODEL,
    DEFAULT_MULTIMODAL_DIMENSIONS,
    DEFAULT_MULTIMODAL_MODEL,
    EMBEDDING_MODELS,
    EMBEDDING_TASKS,
    aggregate_embeddings,
    cosine_similarity,
    count_pdf_pages,
    create_batch_file,
    create_embedding,
    create_embedding_client,
    create_embeddings,
    create_embeddings_batch,
    create_file_embedding,
    create_pdf_embedding,
    embedding_key,
    find_similar,
    format_task_prompt,
    get_embedding,
    get_embedding_provider,
    get_results_embedding,
    legacy_embedding_key,
    normalize_embedding,
    poll_batch_job,
    process_batch_results,
    project_embeddings,
    score_outliers,
    split_pdf_pages,
    submit_batch_job,
)

__all__ = [
    'DEFAULT_DIMENSIONS',
    'DEFAULT_MODEL',
    'DEFAULT_MULTIMODAL_DIMENSIONS',
    'DEFAULT_MULTIMODAL_MODEL',
    'EMBEDDING_MODELS',
    'EMBEDDING_TASKS',
    'aggregate_embeddings',
    'cosine_similarity',
    'count_pdf_pages',
    'create_batch_file',
    'create_embedding',
    'create_embedding_client',
    'create_embeddings',
    'create_embeddings_batch',
    'create_file_embedding',
    'create_pdf_embedding',
    'embedding_key',
    'find_similar',
    'format_task_prompt',
    'get_embedding',
    'get_embedding_provider',
    'get_results_embedding',
    'legacy_embedding_key',
    'normalize_embedding',
    'poll_batch_job',
    'process_batch_results',
    'project_embeddings',
    'score_outliers',
    'split_pdf_pages',
    'submit_batch_job',
]
