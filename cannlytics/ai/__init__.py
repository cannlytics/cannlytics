"""
Cannlytics AI Initialization | Cannlytics
Copyright (c) 2025 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/20/2025
Updated: 6/12/2026
"""
# Dependency guard: `embeddings.py` needs the OpenAI SDK from [ai] and
# Firestore from [firebase]. Name the extras rather than surfacing a
# bare ModuleNotFoundError from two levels down.
try:
    from .embeddings import (
        create_embedding,
        get_embedding,
        get_results_embedding,
        create_batch_file,
        submit_batch_job,
        poll_batch_job,
        process_batch_results,
        create_embeddings_batch,
    )
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        'cannlytics.ai requires the `ai` and `firebase` extras. '
        'Install them with:'
        '\n\n    pip install "cannlytics[ai,firebase]"\n'
    ) from _err

__all__ = [
    'create_embedding',
    'get_embedding',
    'get_results_embedding',
    'create_batch_file',
    'submit_batch_job',
    'poll_batch_job',
    'process_batch_results',
    'create_embeddings_batch',
]