
# Standard imports:
import ast
from datetime import datetime
import glob
import os
from time import sleep

# External imports:
from cannlytics.utils import find_latest_file, snake_case
from cannlytics.lims.results import PRODUCT_TYPES
import pandas as pd
import re
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
from PIL import Image
from rembg import remove


# Read latest aggregated FL lab results.
data_dir = "D://data/florida/results/datasets"
latest_file = find_latest_file(data_dir)
all_results = pd.read_excel(latest_file)
print('Number of results:', len(all_results))

# Restrict to flower types.
flower_types = PRODUCT_TYPES['flower']['names']
flower = all_results[all_results['product_type'].isin(flower_types)]
print('Number of flower results:', len(flower))

# Exclude invalid strain names.
invalid_strain_names = [
    'Hybrid',
    'Hybrid Blend',
    '(H) Hybrid Blend',
    'Sativa',
    'Sativa Blend',
    '(S) Sativa Blend',
    'Indica',
    'Indica Blend',
    '(I) Indica Blend',
    ',N/A',
    'N/A',
    'Matrix: Flower',
    'Matrix: Derivative',
    'Matrix: Edible',
]
flower = flower[~flower['strain_name'].isin(invalid_strain_names)]

# Remove nuisance characters.
for index, row in flower.iterrows():

    # Remove strain type.
    name = row['strain_name']
    if '(H)' in name or ' Hybrid' in name:
        name = name.replace('(H)', '').replace(' Hybrid', '').strip()
        strain_type = 'Hybrid'
    elif '(I)' in name or ' Indica' in name:
        name = name.replace('(I)', '').replace(' Indica', '').strip()
        strain_type = 'Indica'
    elif '(S)' in name or ' Sativa' in name:
        name = name.replace('(S)', '').replace(' Sativa', '').strip()
        strain_type = 'Sativa'

    # Replace genetic indicators.
    name = re.sub(r'\sF\d+', '', name)
    name = re.sub(r'\sRV\d+', '', name)
    name = re.sub(r'\sTLMB\d+', '', name)
    name = re.sub(r'\s#\d+', '', name)

    # Remove unnecessary words.
    name = name.replace('Auto ', '')
    name = name.replace(' XX', '')
    name = name.replace(' Flower', '')
    name = name.replace(' 3.5 g', '')
    name = name.replace(' 3.5g', '')

    # Replace extra spaces.
    name = re.sub(r'\s+', ' ', name).strip()

    flower.at[index, 'strain_name'] = name
    flower.at[index, 'strain_type'] = strain_type

# TODO: Find all of the unique stains.
# Note: NLP will be required.


# TODO: What to do about crosses?
# E.g. "Chem 91 x GSC"


#-----------------------------------------------------------------------
# Identify unique strains with AI.
#-----------------------------------------------------------------------

# Get all existing strain names (curated manually).

# Prompt GPT to identify potential misspelled strain names.


#-----------------------------------------------------------------------
# Strain statistics
#-----------------------------------------------------------------------

# TODO: Calculate statistics for each strain.
strain_names = list(flower['strain_name'].unique())
strain_names.sort()
print('Total number of strains:', len(flower['strain_name'].unique()))
# - totals by month
# - average_total_cannabinoids
# - average_total_thc
# - average_total_cbd
# - average_{cannabinoid}
# - average_total_terpenes
# - average_{terpene}
# - first_date_tested
# - first_producer


# Add keywords to strains.
# refs, updates = [], []
# for strain in strains:
#     name = strain['strain_name'].lower()
#     keywords = name.split() + [name[0]]
#     keywords = list(set(keywords))


# TODO: Archive the strain statistics.
# - created_at
# - updated_at


# TODO: Save images for each strain.
# - Crop the image
# - Upload to Firebase Storage
# - Get a dynamic URL
# - Save the URL and reference to Firestore
