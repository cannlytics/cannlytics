


import hashlib
import json
import os


def clear_cache(cache_path):
    if os.path.exists(cache_path):
        os.remove(cache_path)


def load_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as file:
            return json.load(file)
    else:
        return {}


def save_cache(cache, cache_path):
    with open(cache_path, 'w') as file:
        json.dump(cache, file)


def fetch_product_data(product_url, cache):
    # Hash the URL to use as a cache key
    url_hash = hashlib.sha256(product_url.encode('utf-8')).hexdigest()
    if url_hash in cache:
        return cache[url_hash]  # Return cached data if available

    # Simulate fetching data from the URL
    product_data = {"name": "Example", "price": 9.99}  # Placeholder for actual fetch logic
    cache[url_hash] = product_data  # Update cache
    return product_data


def main():
    cache_path = 'product_cache.json'
    cache = load_cache(cache_path)
    product_url = 'https://flowercompany.com/product/example'
    product_data = fetch_product_data(product_url, cache)
    print(product_data)
    save_cache(cache, cache_path)
