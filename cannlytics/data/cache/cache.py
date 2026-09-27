"""
Bogart | Caching Client
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/14/2024
Updated: 9/21/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Bogart implements caching to give algorithms memory of data and files
    that have already been collected. This greatly quickens data collection.

    A cache is a JSONL file of ``{key: value}`` lines. Keys are SHA-256
    digests from ``cannlytics.utils.hashing``. Files are always read and
    written as UTF-8, and full rewrites are atomic (written beside the
    cache, then renamed over it), so an interrupted run leaves the old
    cache or the new one and never half of each.

References:

    - [Don't Bogart Me](https://www.youtube.com/watch?v=emD48UF-vqE)

"""
# Standard imports:
import json
import logging
import os
import tempfile
from pathlib import Path
from collections.abc import Generator, Iterable

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.utils.hashing import hash_file, hash_text

# Module logger. A library must not print to stdout.
logger = logging.getLogger(__name__)

# Every cache file is UTF-8, on every platform. Without this, Windows
# reads with the locale code page and turns a UTF-8 "Δ9" into "Î”9".
ENCODING = 'utf-8'

def _ensure_parent(path: str) -> None:
    """Create the parent directory of a path, if it names one."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

def _write_jsonl_atomic(
        path: str,
        entries: Iterable[tuple[str, object]],
        ensure_ascii: bool = True,
    ) -> None:
    """Write ``{key: value}`` lines beside ``path``, then rename over it."""
    _ensure_parent(path)
    directory = os.path.dirname(path) or '.'
    handle, temp_path = tempfile.mkstemp(dir=directory, suffix='.tmp')
    try:
        with os.fdopen(handle, 'w', encoding=ENCODING) as file:
            for key, value in entries:
                json.dump({key: value}, file, ensure_ascii=ensure_ascii)
                file.write('\n')
        os.replace(temp_path, path)
    except BaseException:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

class Bogart:
    """A cache for storing cannabis data."""

    def __init__(self, cache_path: str | None = None):
        """Initialize the cache."""
        if cache_path is None:
            cache_path = os.path.join(os.getcwd(), '.cache', 'cache.jsonl')
        self.cache_path = cache_path
        self.cache = self.load(cache_path)

    def append(self, key, value):
        """Append a single entry to the .jsonl file."""
        _ensure_parent(self.cache_path)
        with open(self.cache_path, 'a', encoding=ENCODING) as file:
            json.dump({key: value}, file)
            file.write('\n')

    def load(self, cache_path):
        """Load the cache from a .jsonl file."""
        cache = {}
        self.cache_path = cache_path
        if os.path.exists(self.cache_path):
            with open(self.cache_path, encoding=ENCODING) as file:
                for line in file:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        cache.update(entry)
                    except json.JSONDecodeError:
                        logger.warning('Skipping invalid line in cache: %s', line)
        return cache

    def save(self):
        """Save the entire cache to a .jsonl file, atomically."""
        _write_jsonl_atomic(self.cache_path, self.cache.items())

    def set(self, key, value):
        """Set a value in the cache."""
        if key not in self.cache:
            self.cache[key] = value
            self.append(key, value)

    def get(self, key, default=None):
        """Get a value from the cache."""
        return self.cache.get(key, default)

    def expire(self, key):
        """Expire a key in the cache."""
        if key in self.cache:
            del self.cache[key]
            self.save()

    def clear(self):
        """Clear the cache."""
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)
        self.cache = {}

    def hash_url(self, url):
        """Hash a URL (SHA-256) to use as a cache key."""
        return hash_text(url)

    def hash_file(self, file_path, block_size=65536):
        """Hash a whole file (SHA-256) to use as a cache key."""
        return hash_file(file_path, size=block_size)

    def merge(self, cache_path):
        """Merge another .jsonl cache file into this cache, keeping unique hashes."""
        if os.path.exists(cache_path):
            with open(cache_path, encoding=ENCODING) as file:
                for line in file:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning('Skipping invalid line in cache: %s', line)
                        continue
                    for key, value in entry.items():
                        if key not in self.cache:
                            self.cache[key] = value
                            self.append(key, value)

    def to_df(self):
        """Return the cache as a DataFrame."""
        values = list(self.cache.values())
        # Note: This may be better to handle as an option.
        try:
            values = [x[0] if isinstance(x, list) else x for x in values]
        except TypeError:
            pass
        return pd.DataFrame.from_records(values)

def read_jsonl(
        cache_path: str,
        desired_fields: list[str],
        chunk_size: int = 10_000,
        method: str = 'records',
    ) -> Generator[pd.DataFrame, None, None]:
    """
    Read a JSONL file in chunks and extract only specified fields.
    Args:
        cache_path (str): Path to the JSONL file
        desired_fields (List[str]): List of field names to extract
        chunk_size (int): Number of records to process at a time
    Returns:
        Generator[pd.DataFrame]: Chunks of data as pandas DataFrames
    """
    chunk_data = []
    with open(cache_path, encoding=ENCODING) as file:
        for i, line in enumerate(file, 1):
            try:
                record = json.loads(line)
                if method == 'records':
                    _, obs = next(iter(record.items()))
                else:
                    obs = record
                filtered_record = {
                    field: obs.get(field)
                    for field in desired_fields
                }
                chunk_data.append(filtered_record)
                if i % chunk_size == 0:
                    yield pd.DataFrame(chunk_data)
                    chunk_data = []
            except json.JSONDecodeError as e:
                logger.warning('Error parsing line %s: %s', i, e)
                continue
        if chunk_data:
            yield pd.DataFrame(chunk_data)

def read_cache(
        cache_path: str,
        desired_fields: list[str],
        chunk_size: int = 10_000,
        method: str = 'records',
    ) -> pd.DataFrame:
    """Read a JSONL cache file and return the data as a DataFrame."""
    dfs = []
    total_rows = 0
    for chunk_df in read_jsonl(cache_path, desired_fields, chunk_size=chunk_size, method=method):
        total_rows += len(chunk_df)
        logger.info('Processed %s rows...', total_rows)
        dfs.append(chunk_df)
    return pd.concat(dfs, ignore_index=True)

def organize_cache(
        input_path: str,
        output_path: str | None = None,
    ) -> None:
    """
    Reads a JSONL file, sorts by the first key of each JSON object,
    removes duplicates, and writes the result to a new JSONL file.
    """
    # Convert paths to Path objects.
    if output_path is None:
        output_path = input_path
    input_path, output_path = Path(input_path), Path(output_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read and parse JSONL, keeping only unique entries.
    unique_entries: dict[str, dict] = {}
    with input_path.open('r', encoding=ENCODING) as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line.strip())
            if isinstance(entry, dict) and entry:
                key = list(entry.keys())[0]
                unique_entries[key] = entry

    # Save sorted and deduplicated entries.
    ordered = sorted(unique_entries.values(), key=lambda x: list(x.keys())[0].lower())
    _write_jsonl_atomic(
        str(output_path),
        ((key, value) for entry in ordered for key, value in entry.items()),
        ensure_ascii=False,
    )

def rekey_cache(
        cache_path: str,
        key_map: dict[str, str],
        output_path: str | None = None,
        hash_fields: tuple[str, ...] = ('pdf_hash', 'hash'),
    ) -> dict[str, int]:
    """Rewrite a cache's keys, such as pre-1.0.0 SHA-1 keys to SHA-256.

    Build ``key_map`` with ``cannlytics.utils.hashing.build_hash_crosswalk``
    and ``crosswalk_key_map``. Nothing is re-parsed and the input is
    untouched unless ``output_path`` is omitted, in which case the cache
    is replaced atomically.

    Args:
        cache_path: The JSONL cache to read.
        key_map: Map of old key to new key. Keys absent from the map
            are kept as they are.
        output_path: Where to write. Defaults to ``cache_path``.
        hash_fields: Fields inside each value that repeat the key and
            are rewritten along with it.

    Returns:
        Counts: ``total``, ``rekeyed``, ``unchanged``, and ``collisions``
        (entries dropped because their new key was already taken; the
        first entry wins, as in ``Bogart.set``).

    Raises:
        FileNotFoundError: If ``cache_path`` does not exist.
    """
    if not os.path.exists(cache_path):
        raise FileNotFoundError(f'Cache not found: {cache_path}')
    stats = {'total': 0, 'rekeyed': 0, 'unchanged': 0, 'collisions': 0}
    entries: dict[str, object] = {}
    with open(cache_path, encoding=ENCODING) as file:
        for line in file:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                logger.warning('Skipping invalid line in cache: %s', line)
                continue
            for key, value in record.items():
                stats['total'] += 1
                new_key = key_map.get(key, key)
                if new_key in entries:
                    stats['collisions'] += 1
                    continue
                if new_key != key:
                    stats['rekeyed'] += 1
                    if isinstance(value, dict):
                        value = {
                            k: (new_key if k in hash_fields and v == key else v)
                            for k, v in value.items()
                        }
                else:
                    stats['unchanged'] += 1
                entries[new_key] = value
    _write_jsonl_atomic(output_path or cache_path, entries.items())
    return stats
