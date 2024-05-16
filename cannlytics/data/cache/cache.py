"""
Bogart | Caching Client
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/14/2024
Updated: 5/14/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Bogart implements caching to give algorithms memory of data and files
    that have already been collected. This greatly quickens data collection.

References:

    - [Don't Bogart Me](https://www.youtube.com/watch?v=emD48UF-vqE)

"""
import hashlib
import json
import os


class Bogart(object):
    """A cache for storing cannabis data."""

    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.cache = self.load_cache(cache_path)

    # TODO: Add methods:
    # - set
    # - get
    # - expire
    # - get_size


    def clear_cache(cache_path):
        """Sometimes the Bogart is said to fly into a rage and wreck
        all his work before leaving. This is called clearing the cache."""
        if os.path.exists(cache_path):
            os.remove(cache_path)


    def load_cache(cache_path):
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as file:
                return json.load(file)
        else:
            return {}


    def save(cache, cache_path):
        with open(cache_path, 'w') as file:
            json.dump(cache, file)


    def hash_url(url, cache):
        # Hash a URL to use as a cache key.
        return hashlib.sha256(url.encode('utf-8')).hexdigest()


    # TODO: Hash file.


# === Tests ===
# Tested: 2024-05-14 by Keegan Skeate <keegan@cannlytics.com>
if __name__ == '__main__':

    # TODO: Implement tests.
    cache = Bogart()
