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

    # [✓] Get information about Cannlytics AI.
    response = session.get(f'{BASE}/ai')
    assert response.status_code == 200
    print('AP live.')

    # [✓] Create a recipe.
    print('Creating a recipe...')
    data = {
      'image_type': '',
      'ingredients': ['coffee', 'milk', 'butter'],
      'product_name': 'Infused cannabis coffee',
      'doses': None,
      'special_instructions': None,
      'creativity': 0.420,
      'total_thc': 800,
      'total_cbd': 0,
      'public': True,
    }
    response = session.post(f'{BASE}/ai/recipes', json=data)
    assert response.status_code == 200
    print('Created a recipe.')

    # [✓] Generate a color from text.
    data = {'text': 'Moonshine Haze'}
    response = session.post(f'{BASE}/ai/color', json=data)
    assert response.status_code == 200
    print('Generated color from text.')

    # [✓] Generate an emoji from text.
    data = {'text': 'Moonshine Haze'}
    response = session.post(f'{BASE}/ai/emoji', json=data)
    assert response.status_code == 200
    print('Generated emoji from text.')

    # [✓] Get a user's recipes.
    response = session.get(f'{BASE}/ai/recipes')
    assert response.status_code == 200
    print('Found user recipes.')

    # [✓] Get a recipe using its ID.
    uid = response.json()['data'][0]['id']
    response = session.get(f'{BASE}/ai/recipes/{uid}')
    assert response.status_code == 200
    print('Found user recipe by ID.')

    # [ ] Get public recipes.
    params = {'public': True}
    response = session.get(f'{BASE}/ai/recipes', params=params)
    assert response.status_code == 200
    print('Found public recipes.')

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
    data = {
      'ingredients': [],
      'title': '',
      'doses': None,
      'instructions': '',
      'special_instructions': None,
      'creativity': 0.420,
      'change_recipe': True,
      'change_image': True,
      'change_title': True,
      'public': True,
    }

    # [ ] Update a recipe's image.


    # [ ] Delete a recipe.


    # [ ] Give feedback on a recipe.
    data = {
        'feedback': 'Simply delightful.',
        'like': True,
        'uid': '<recipe_id>',
    }
    params = {'action': 'feedback'}
    url = f'{BASE}/ai/recipes'
    response = session.post(url, json=data, params=params)
    assert response.status_code == 200
    print('Created a recipe.')

    # [ ] Review a public recipe.
    data = {
        'review': "A baker's dozen!",
        'rating': 0.420,
    }
    params = {'action': 'review'}
