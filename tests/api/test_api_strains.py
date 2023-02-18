"""
Test Strain Data API Endpoint | Cannlytics API
SkunkFx
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/31/2021
Updated: 6/3/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports.
import json
import urllib.parse

# External imports.
import pandas as pd
import requests


# Define the API endpoint.
# BASE = 'http://127.0.0.1:8000/api'
BASE = 'https://cannlytics.com/api' # Uncomment for production.
url = f'{BASE}/data/strains'

#-----------------------------------------------------------------------

# Get strains.
params = {'limit': 3}
response = requests.get(url, params=params)
print(response.url)
assert response.status_code == 200
data = response.json()['data']
print('Found %i strains.' % len(data))
assert len(data) == 3

#-----------------------------------------------------------------------

# Get a specific strain.
url = f'{BASE}/data/strains'
strain_name = 'Super Silver Haze'
response = requests.get(url + '/' + urllib.parse.quote_plus(strain_name))
print(response.url)
assert response.status_code == 200
data = response.json()['data']
assert data['strain_name'] == strain_name
print('Found %s.' % data['strain_name'])

#-----------------------------------------------------------------------

# Get strains by effects.
url = f'{BASE}/data/strains'
effects = json.dumps(['focused', 'creative'])
params = {'limit': 10, 'effects': effects}
response = requests.get(url, params=params)
print(response.url)
assert response.status_code == 200
data = pd.DataFrame(response.json()['data'])
print('Found %i strains.' % len(data))
data['pinene_limonene_ratio'] = data['beta_pinene'].div(data['d_limonene'])
print(data[['strain_name', 'potential_effects', 'pinene_limonene_ratio']])

#-----------------------------------------------------------------------

# Get strains by aromas.
url = f'{BASE}/data/strains'
aromas = json.dumps(['skunk'])
params = {'limit': 5,'aromas': aromas}
response = requests.get(url, params=params)
print(response.url)
assert response.status_code == 200
data = pd.DataFrame(response.json()['data'])
print('Found %i strains.' % len(data))
print(data[['strain_name', 'potential_aromas']])

#-----------------------------------------------------------------------

# Get strain by compound concentration.
compound = 'terpinolene'
url = f'{BASE}/data/strains'
params = {'limit': 25, compound: 'ge0.6'}
response = requests.get(url, params=params)
print(response.url)
assert response.status_code == 200
data = pd.DataFrame(response.json()['data'])
print('Found %i strains.' % len(data))
print(data[['strain_name', compound]])
