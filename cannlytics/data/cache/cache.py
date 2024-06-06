"""
Bogart | Caching Client
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/14/2024
Updated: 5/19/2024
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
from typing import Optional

import pandas as pd


class Bogart(object):
    """A cache for storing cannabis data."""

    def __init__(self, cache_path: Optional[str] = None):
        """Initialize the cache."""
        if cache_path is None:
            cache_path = os.path.join(os.getcwd(), '.cache', 'cache.jsonl')
        self.cache = self.load_cache(cache_path)

    def set(self, key, value):
        """Set a value in the cache."""
        if key not in self.cache:
            self.cache[key] = value
            self.append_cache(key, value)

    def get(self, key):
        """Get a value from the cache."""
        return self.cache.get(key)

    def expire(self, key):
        """Expire a key in the cache."""
        if key in self.cache:
            del self.cache[key]
            self.save_cache()

    def clear_cache(self):
        """Clear the cache."""
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)
        self.cache = {}

    def load_cache(self, cache_path):
        """Load the cache from a .jsonl file."""
        cache = {}
        self.cache_path = cache_path
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as file:
                for line in file:
                    entry = json.loads(line)
                    cache.update(entry)
        return cache

    def save_cache(self):
        """Save the entire cache to a .jsonl file."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w') as file:
            for key, value in self.cache.items():
                json.dump({key: value}, file)
                file.write('\n')

    def append_cache(self, key, value):
        """Append a single entry to the .jsonl file."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'a') as file:
            json.dump({key: value}, file)
            file.write('\n')

    def hash_url(self, url):
        """Hash a URL to use as a cache key."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def hash_file(self, file_path):
        """Hash a file to use as a cache key."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def merge_caches(self, cache_path):
        """Merge another .jsonl cache file into this cache, keeping unique hashes."""
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as file:
                for line in file:
                    entry = json.loads(line)
                    for key, value in entry.items():
                        if key not in self.cache:
                            self.cache[key] = value
                            self.append_cache(key, value)
    
    def to_df(self):
        """Return the cache as a DataFrame."""
        values = list(self.cache.values())
        values = [x[0] if isinstance(x, list) else x for x in values]
        return pd.DataFrame.from_records(values)

# === Tests ===
# Tested: 2024-05-21 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__' and False:

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
    cache.clear_cache()
    print('Cache cleared.')
