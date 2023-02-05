"""
Recipes API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/5/2023
Updated: 2/5/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports:
import os

# External imports:
from dotenv import dotenv_values
import requests

# Internal imports:
from cannlytics.utils import (
    get_date_range,
    encode_pdf,
    get_timestamp,
)

# Dev: Test with the development server.
BASE = 'http://127.0.0.1:8000/api'

# Production: Uncomment to test with the production server once published.
# BASE = 'https://cannlytics.com/api'

# Load your API key to pass in the authorization header as a bearer token.
config = dotenv_values('../../.env')
API_KEY = config['CANNLYTICS_API_KEY']


# === Tests ===
if __name__ == '__main__':

    # Authentication a session.
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {API_KEY}'})

    # [✓] Create a recipe.
    print('Creating a recipe...')
    url = f'{BASE}/recipes'
    data = {
      'ingredients': ['coffee', 'milk', 'butter'],
      'product_name': 'Infused cannabis coffee',
      'doses': None,
      'special_instructions': None,
      'creativity': 0.420,
      # TODO: Test more fields!
    }
    response = session.post(f'{BASE}/ai/recipes', json=data)
    assert response.status_code == 200
    print('Created a recipe.')

    # [ ] Get a user's recipes.


    # [ ] Get a recipe using its ID.


    # [ ] Get public recipes.


    # [ ] Search public / user recipes:
    # - limit
    # - order_by
    # - desc
    # - filters:
    # available_filters = [
    #     {'key': 'product_name', 'type': 'str'},
    #     {'key': 'product_subtype', 'type': 'str'},
    #     {'key': 'title', 'type': 'str'},
    #     {'key': 'total_thc', 'type': 'float'},
    #     {'key': 'total_cbd', 'type': 'float'},
    #     {'key': 'serving_cbd', 'type': 'float'},
    #     {'key': 'number_of_servings', 'type': 'number_of_servings'},
    #     {'key': 'created_at_min', 'type': 'datetime'},
    #     {'key': 'created_at_max', 'type': 'datetime'},
    #     {'key': 'updated_at_min', 'type': 'datetime'},
    #     {'key': 'updated_at_max', 'type': 'datetime'},
    # ]


    # [ ] Update a recipe.


    # [ ] Update a recipe's image.


    # [ ] Delete a recipe.


    # [ ] Give feedback on a recipe.


    # [ ] Review a public recipe.
    data = {
        'review': "A baker's dozen!",
        'rating': 0.420,
    }


    # [ ] Rate a public recipe.
