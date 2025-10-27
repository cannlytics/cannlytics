"""
Bogart | Caching Client
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/14/2024
Updated: 1/3/2025
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Bogart implements caching to give algorithms memory of data and files
    that have already been collected. This greatly quickens data collection.

References:

    - [Don't Bogart Me](https://www.youtube.com/watch?v=emD48UF-vqE)

"""
# Standard imports:
import hashlib
import json
import os
from pathlib import Path
from typing import Generator, Optional

# External imports:
import pandas as pd


class Bogart(object):
    """A cache for storing cannabis data."""

    def __init__(self, cache_path: Optional[str] = None):
        """Initialize the cache."""
        if cache_path is None:
            cache_path = os.path.join(os.getcwd(), '.cache', 'cache.jsonl')
        self.cache = self.load(cache_path)

    def append(self, key, value):
        """Append a single entry to the .jsonl file."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'a') as file:
            json.dump({key: value}, file)
            file.write('\n')
    
    def load(self, cache_path):
        """Load the cache from a .jsonl file."""
        cache = {}
        self.cache_path = cache_path
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as file:
                for line in file:
                    try:
                        entry = json.loads(line)
                        cache.update(entry)
                    except json.JSONDecodeError:
                        print(f"Skipping invalid line in cache: {line}")
        return cache

    def save(self):
        """Save the entire cache to a .jsonl file."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w') as file:
            for key, value in self.cache.items():
                json.dump({key: value}, file)
                file.write('\n')

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
        """Hash a URL to use as a cache key."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def hash_file(self, file_path, block_size=65536):
        """Hash a file to use as a cache key by reading it in chunks."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            while True:
                buf = file.read(block_size)
                if not buf:
                    break
                hasher.update(buf)
        return hasher.hexdigest()

    def merge(self, cache_path):
        """Merge another .jsonl cache file into this cache, keeping unique hashes."""
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as file:
                for line in file:
                    entry = json.loads(line)
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
    with open(cache_path, 'r', encoding='utf-8') as file:
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
                print(f"Error parsing line {i}: {e}")
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
        print(f"Processed {total_rows} rows...")
        dfs.append(chunk_df)
    return pd.concat(dfs, ignore_index=True)


def organize_cache(
        input_path: str,
        output_path: Optional[str] = None,
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
    with input_path.open('r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            if isinstance(entry, dict) and entry:
                key = list(entry.keys())[0]
                unique_entries[key] = entry

    # Save sorted and deduplicated entries.
    with output_path.open('w', encoding='utf-8') as f:
        for entry in sorted(unique_entries.values(), key=lambda x: list(x.keys())[0].lower()):
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# === Tests ===
# Tested: 2024-05-21 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    from datetime import datetime

    # Initialize the cache.
    cache_path = 'D://data/.cache/test-cache.jsonl'
    cache = Bogart(cache_path)

    # Set a value in the cache.
    url = 'https://cannlytics.com'
    url_hash = cache.hash_url(url)
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cache.set(url_hash, {'status': 'collected', 'url': url, 'date': date})
    print('Cache set:', cache.get(url_hash))

    # Set a value in the cache.
    url = 'https://cannlytics.com/contact'
    url_hash = cache.hash_url(url)
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cache.set(url_hash, {'status': 'collected', 'url': url, 'date': date})
    print('Cache set:', cache.get(url_hash))

    # Check if a value is in the cache.
    print('Cache get:', cache.get(url_hash))

    # Expire a key in the cache.
    cache.expire(url_hash)
    print('Cache expired:', cache.get(url_hash))

    # Clear the cache.
    cache.clear()
    print('Cache cleared.')
