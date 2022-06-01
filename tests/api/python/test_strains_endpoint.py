"""
Test Strain Data API Endpoint | Cannlytics API

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/31/2021
Updated: 6/1/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports.
import json
import urllib.parse

# External imports.
import pandas as pd
import requests


# Define the API endpoint.
BASE = 'http://127.0.0.1:8000/api'
url = f'{BASE}/data/strains'

#-----------------------------------------------------------------------

# Get strains.
params = {'limit': 3}
response = requests.get(url, params=params)
assert response.status_code == 200
data = response.json()['data']
print('Found %i strains.' % len(data))
assert len(data) == 3

#-----------------------------------------------------------------------

# Get a specific strain.
url = f'{BASE}/data/strains'
strain_name = 'Super Silver Haze'
response = requests.get(url + '/' + urllib.parse.quote_plus(strain_name))
assert response.status_code == 200
data = response.json()['data']
assert data['strain_name'] == strain_name
print('Found %s.' % data['strain_name'])

#-----------------------------------------------------------------------

# Get strains by effects.
url = f'{BASE}/data/strains'
params = {
    'limit': 10,
    'effects': json.dumps(['focused']),
}
response = requests.get(url, params=params)
assert response.status_code == 200
data = pd.DataFrame(response.json()['data'])
print('Found %i strains.' % len(data))
data['pinene_limonene_ratio'] = data['beta_pinene'].div(data['d_limonene'])
print(data[['strain_name', 'potential_effects', 'pinene_limonene_ratio']])

#-----------------------------------------------------------------------

# Get strains by aromas.
url = f'{BASE}/data/strains'
params = {
    'limit': 5,
    'aromas': json.dumps(['skunk']),
}
response = requests.get(url, params=params)
assert response.status_code == 200
data = pd.DataFrame(response.json()['data'])
print('Found %i strains.' % len(data))
print(data[['strain_name', 'potential_aromas']])

#-----------------------------------------------------------------------

# Get strain by compound concentration.
compound = 'beta_pinene'
url = f'{BASE}/data/strains'
params = {'limit': 25}
params[compound] = 'g0.2'
response = requests.get(url, params=params)
assert response.status_code == 200
data = pd.DataFrame(response.json()['data'])
print('Found %i strains.' % len(data))
print(data[['strain_name', compound]])

#-----------------------------------------------------------------------

# Post lab results to get potential effects and aromas.
data = {
    'model': 'simple',
    'samples': [
        {'total_cbd': 0.04, 'total_thc': 18.0},
        {'total_cbd': 0.04, 'total_thc': 20.0},
        {'total_cbd': 0.04, 'total_thc': 28.0},
        {'total_cbd': 7.0, 'total_thc': 7.0},
    ]
}
url = f'{BASE}/stats/effects'
response = requests.post(url, json=data)
assert response.status_code == 200
data = response.json()['data']
model_stats = data['model_stats']
samples = pd.DataFrame(data['samples'])

# Collect outcomes.
outcomes = pd.DataFrame()
for index, row in samples.iterrows():
    print(f'\nSample {index}')
    print('-------------')
    for i, key in enumerate(row['potential_effects']):
        tpr = round(model_stats['true_positive_rate'][key] * 100, 2)
        fpr = round(model_stats['false_positive_rate'][key] * 100, 2)
        title = key.replace('effect_', '').replace('_', ' ').title()
        print(title, f'(TPR: {tpr}%, FPR: {fpr}%)')
        outcomes = pd.concat([outcomes, pd.DataFrame([{
            'tpr': tpr,
            'fpr': fpr,
            'name': title,
            'strain_name': index,
        }])])

# Visualize outcomes.
import seaborn as sns
import matplotlib.pyplot as plt

# Setup plotting style.
plt.style.use('fivethirtyeight')
plt.rcParams.update({
    'figure.figsize': (18, 8),
    'font.family': 'Times New Roman',
})

# Create the plot.
sns.factorplot(
    x='name',
    y='tpr',
    hue='strain_name',
    data=outcomes,
    kind='bar',
    legend=False,
    aspect=11.7/8.27
)
plt.legend(loc='upper right', title='Strain')
plt.title('Predicted Effects That May be Reported')
plt.ylabel('True Positive Rate')
plt.xlabel('Predicted Effect')
plt.xticks(rotation=90)
plt.show()
