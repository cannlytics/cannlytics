"""
Get Strains | California
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/7/2024
Updated: 5/7/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Data points:

    - strain_name
    - strain_type
    - strain_description
    - strain_images
    - reported_aromas
    - reported_effects
    - first_date_tested
    - latest_date_tested
    - first_producer
    - first_state
    - first_zipcode
    - total_tests
    - avg_total_cannabinoids
    - avg_total_thc
    - avg_total_cbd
    - avg_total_terpenes
    - avg_{cannabinoid}
    - avg_{terpene}
    - cannabinoid_type
    - dominant_terpene
    - cannabinoid_diversity
    - terpene_diversity

"""
# Standard imports:
from datetime import datetime
import json
import math
import os
from dotenv import dotenv_values
import numpy as np

# External imports:
from cannlytics.firebase import initialize_firebase, update_documents
from cannlytics.lims.compounds import cannabinoids, terpenes
from cannlytics.utils import find_latest_file, kebab_case
from cannlytics.lims.results import PRODUCT_TYPES
import pandas as pd
import re
from PIL import Image
from rembg import remove


#-----------------------------------------------------------------------
# Read lab results and cached strain data.
#-----------------------------------------------------------------------

# Read all of the SC Labs results.
datafile ="D://data/california/lab_results/datasets/sclabs/ca-lab-results-sclabs-2024-01-02-00-39-36.xlsx"
all_results = pd.read_excel(datafile)

# Restrict to results from California.
all_results = all_results.loc[all_results['lab_state'] == 'CA']

# Restrict to flower types.
flower_types = PRODUCT_TYPES['flower']['names']
flower = all_results[all_results['product_type'].isin(flower_types)]
print('Number of flower results:', len(flower))

# Read cached strain data.
cache_dir = 'D://data/strains'
cache_file = os.path.join(cache_dir, 'strains-ca.json')
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        cache = json.load(f)
else:
    cache = {}
    os.makedirs(cache_dir, exist_ok=True)


#-----------------------------------------------------------------------
# Process strain names.
#-----------------------------------------------------------------------

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

    # Update the strain name.
    flower.at[index, 'strain_name'] = name
    flower.at[index, 'strain_type'] = strain_type


# TODO: What to do about crosses?
# - strain_names
# - lineage
# E.g. "Chem 91 x GSC"


#-----------------------------------------------------------------------
# Identify unique strains with AI.
#-----------------------------------------------------------------------

# Get all existing strain names (curated manually).


# Prompt GPT to identify potential misspelled strain names.

# TODO: Iterate over strains alphabetically.



# TODO: Find all of the unique strains.


#-----------------------------------------------------------------------
# Get images for strains.
# Note: FL COAs only have images of the containers.
#-----------------------------------------------------------------------

def remove_bg(input_path: str, output_path: str) -> None:
    """Convert a video file to another video with a transparent background.
    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path to save the output image with a transparent background.
    """
    input = Image.open(input_path)
    output = remove(input)
    output.save(output_path)


# # DEV:
# strain_name = 'Rosetta Stone'
# strain_results = flower[flower['strain_name'] == strain_name]
# print('Number of results for', strain_name, ':', len(strain_results))

# # Match COA PDFs with the results.
# pdf_dir = 'D://data/florida/results/pdfs'
# coa_pdfs = {}
# for index, result in strain_results.iterrows():
#     identifier = result['coa_pdf']
#     if identifier == 'download.pdf':
#         lab_results_url = result['lab_results_url']
#         identifier = lab_results_url.split('=')[-1].split('?')[0]
#     for root, _, files in os.walk(pdf_dir):
#         for filename in files:
#             if identifier in filename:
#                 pdf_path = os.path.join(root, filename)
#                 coa_pdfs[result['sample_hash']] = pdf_path
#                 print(pdf_path)
#                 break

# Download the images to an image dir.
# image_files = []
# image_dir = 'D://data/colorado/lab_results/images/sclabs'
# if not os.path.exists(image_dir):
#     os.makedirs(image_dir)
# for index, row in results.iterrows():
#     images = ast.literal_eval(row['images'])
#     if images:
#         coa_id = row['coa_id'].split('-')[0].strip()
#         filename = f'{image_dir}/{coa_id}.jpg'
#         if os.path.exists(filename):
#             image_files.append(filename)
#             continue
#         image_url = images[0]['url']
#         response = requests.get(image_url)
#         if response.status_code == 200:
#             print(f"Downloaded: {image_url}")
#             with open(filename, 'wb') as f:
#                 f.write(response.content)
#         else:
#             print(f"Failed to download: {image_url}")
#         image_files.append(filename)
#         sleep(2)

# Crop the images.
# cropped_images = []
# for image_file in image_files:
#     cropped_file = image_file.replace('.jpg', '-cropped.png')
#     if os.path.exists(cropped_file):
#         cropped_images.append(cropped_file)
#         continue
#     remove_bg(image_file, cropped_file)
#     cropped_images.append(cropped_file)
#     print(f'Cropped: {cropped_file}')

# Keep track of images in a cache.

# Upload new files to Firebase Storage.
#     bucket_name = config['FIREBASE_STORAGE_BUCKET']
#     firebase.upload_file(file_ref, file_path, bucket_name=bucket_name)
#     download_url = firebase.get_file_url(file_ref, bucket_name=bucket_name)
#     obs['images'] = [{'ref': file_ref, 'url': download_url, 'filename': 'image_data.png'}]

# Save the file references with the strain data.


#-----------------------------------------------------------------------
# Strain statistics
#-----------------------------------------------------------------------

def calc_diversity(df, compounds):
    """Calculate Shannon Diversity Index."""
    diversities = []
    for _, row in df.iterrows():
        proportions = [pd.to_numeric(row[compound], errors='coerce') for compound in compounds if pd.to_numeric(row[compound], errors='coerce') > 0]
        proportions = np.array(proportions) / sum(proportions)
        shannon_index = -np.sum(proportions * np.log2(proportions))
        diversities.append(shannon_index)
    return diversities


# Find all unique strains.
strain_names = list(flower['strain_name'].unique())
strain_names.sort()
print('Total number of strains:', len(flower['strain_name'].unique()))

# Calculate statistics for each strain.
strain_stats = {}
for strain_name in strain_names[:1]:
    print('Getting statistics for', strain_name)
    stats = {'strain_name': strain_name}
    strain_results = flower[flower['strain_name'] == strain_name]

    # Summary stats.
    stats['total_tests'] = len(strain_results)
    stats['strain_type'] = strain_results['strain_type'].mode().values[0]

    # First and last test dates.
    first_date_tested = strain_results['date_tested'].min()
    first = strain_results.loc[strain_results['date_tested'] == first_date_tested].iloc[0]
    stats['first_date_tested'] = first_date_tested
    stats['latest_date_tested'] = strain_results['date_tested'].max()

    # Find the first producer.
    stats['first_producer'] = first.get('producer')
    stats['first_license_number'] = first.get('producer_license_number')
    stats['first_state'] = first.get('producer_state')
    stats['first_city'] = first.get('producer_city', '')
    stats['first_county'] = first.get('producer_county', '')
    stats['first_zipcode'] = first.get('producer_zipcode', '')

    # Calculate average concentrations and standard deviations.
    stats['avg_total_cannabinoids'] = round(strain_results['total_cannabinoids'].mean(), 2)
    stats['avg_total_thc'] = round(strain_results['total_thc'].mean(), 2)
    stats['avg_total_cbd'] = round(strain_results['total_cbd'].mean(), 2)
    stats['avg_total_terpenes'] = round(strain_results['total_terpenes'].mean(), 2)
    for cannabinoid in cannabinoids:
        try:
            series = strain_results.loc[strain_results[cannabinoid] > 0.0001][cannabinoid]
            stats[f'avg_{cannabinoid}'] = round(series.mean(), 2)
            stats[f'std_{cannabinoid}'] = round(series.std(), 2)
        except:
            stats[f'avg_{cannabinoid}'] = 0
            stats[f'std_{cannabinoid}'] = 0
    for terpene in terpenes:
        try:
            series = strain_results.loc[strain_results[terpene] > 0.0001][terpene]
            stats[f'avg_{terpene}'] = round(series.mean(), 2)
            stats[f'std_{terpene}'] = round(series.std(), 2)
        except:
            stats[f'avg_{terpene}'] = 0
            stats[f'std_{terpene}'] = 0

    # Add keywords.
    name = strain_name.lower()
    keywords = name.split() + [name[0]]
    stats['keywords'] = list(set(keywords))

    # TODO: Calculate common ratios.
    # Note: `pinene` is the sum of `alpha_pinene` and `beta_pinene`.
    # avg_thc_cbd_ratio
    # avg_beta_pinene_d_limonene_ratio
    # avg_alpha_humulene_beta_caryophyllene_ratio
    # avg_camphene_d_limonene_ratio
    # avg_beta_myrcene_pinene_ratio
    # avg_beta_caryophyllene_d_limonene_ratio

    stats['avg_thc_cbd_ratio'] = round(stats['avg_total_thc'] / stats['avg_total_cbd'], 2)

    # Determine the cannabinoid type.
    # See: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9119530/
    log_thc_cbd_ratio = round(math.log10(stats['avg_thc_cbd_ratio']), 2)
    if log_thc_cbd_ratio < -0.5:
        stats['cannabinoid_type'] = 'CBD Dominant'
    elif log_thc_cbd_ratio > 0.5:
        stats['cannabinoid_type'] = 'THC Dominant'
    else:
        stats['cannabinoid_type'] = 'Balanced THC:CBD'

    # Determine the dominant terpene.
    dominant_terpene = ''
    max_terpene = 0
    for terpene in terpenes:
        if stats[f'avg_{terpene}'] > max_terpene:
            dominant_terpene = terpene
            max_terpene = stats[f'avg_{terpene}']
    stats['dominant_terpene'] = dominant_terpene

    # Chemical diversity.
    df = pd.DataFrame([stats])
    avg_cannabinoids = [f'avg_{x}' for x in cannabinoids]
    avg_terpenes = [f'avg_{x}' for x in terpenes]
    stats['cannabinoid_diversity'] = round(calc_diversity(df, avg_cannabinoids)[0], 4)
    stats['terpene_diversity'] = round(calc_diversity(df, avg_terpenes)[0], 4)

    # Calculate percentiles for each compound.

    # Record strain stats.
    strain_stats[strain_name] = stats


# Include lab result IDs?
# - lab_result_ids


#-----------------------------------------------------------------------
# Get any mentioned aromas and effects for given strains.
#-----------------------------------------------------------------------

# TODO: Read Reddit posts.


# TODO: Find any posts that mention the strain name.


#-----------------------------------------------------------------------
# Write description with AI.
#-----------------------------------------------------------------------

# Define the strain description prompt.
strain_description_prompt = """Act as a world-class writer for one of the world's most prestigious scientific journals. Write a brief scientific description for the following cannabis strain, incorporating some of its facts in a stylistic manner, to be used as a caption for the strain in various scientific publications. Do not mention any purported effects or aromas. Only return the description. Write with wit, almost undetectably dry humor, elegant prose, with captivating, thought-provoking, unusual language with an excessive amount of alliteration, puns, cultural references, quirky word choices, and fun and humorous sentence structures."""
strain_description_prompt += """\n
- Strain Name: {strain_name}
- Strain Type: {strain_type}
- First Date Tested: {first_date_tested}
- Latest Date Tested: {latest_date_tested}
- First Producer: {first_producer}
- First City: {first_city}
- First State: {first_state}
- Total Tests: {total_tests}
- Average Total Cannabinoids: {avg_total_cannabinoids}
- Average Total THC: {avg_total_thc}
- Average Total CBD: {avg_total_cbd}
- Average Total Terpenes: {avg_total_terpenes}
""".format(**stats)
for cannabinoid in cannabinoids:
    value = stats['avg_' + cannabinoid]
    if value > 0:
        strain_description_prompt += f"- Average {cannabinoid}: {value}\n"
for terpene in terpenes:
    value = stats['avg_' + terpene]
    if value > 0:
        strain_description_prompt += f"- Average {terpene}: {value}\n"
print(strain_description_prompt)

# TODO: Create strain descriptions in batches.


#-----------------------------------------------------------------------
# Upload strain data to Firestore.
#-----------------------------------------------------------------------

# Parameters.
overwrite = False

# Initialize Firebase.
config = dotenv_values('.env')
db = initialize_firebase()
bucket_name = config['FIREBASE_STORAGE_BUCKET']
firebase_api_key = config['FIREBASE_API_KEY']

# Structure the data.
strain_data = pd.DataFrame(strain_stats.values())

# Create a strain ID for each strain.
strain_data['strain_id'] = strain_data['strain_name'].apply(kebab_case)

# Upload the data to Firestore if not locally cached.
refs, updates = [], []
collection = 'strains'
for _, obs in strain_data.iterrows():
    doc_id = obs['strain_id']
    if doc_id not in cache.get('strains', []) or overwrite:
        entry = obs.to_dict()
        entry['updated_at'] = datetime.now().isoformat()[:19]
        refs.append(f'{collection}/{doc_id}')
        updates.append(entry)
        cache.setdefault('strains', []).append(doc_id)
if refs:
    update_documents(refs, updates, database=db)
    print('Uploaded %i results to Firestore.' % len(refs))

# Save the updated cache
with open(cache_file, 'w') as f:
    json.dump(cache, f)
    print('Saved cache:', cache_file)