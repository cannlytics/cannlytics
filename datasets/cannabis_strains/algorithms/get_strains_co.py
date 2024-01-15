# Standard imports:
import ast
import os
from time import sleep

# External imports:
from cannlytics.utils import snake_case
import pandas as pd
import re
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

from PIL import Image
from rembg import remove


# Read all of the SC Labs results.
datafile ="D://data/california/lab_results/datasets/sclabs/ca-lab-results-sclabs-2024-01-02-00-39-36.xlsx"
data = pd.read_excel(datafile)

# Find all of the results from Colorado.
results = data.loc[data['lab_state'] == 'CO']

# Save the Colorado results.
outfile = 'C://Users/keega/Documents/cannlytics/cannlytics/datasets/cannabis_tests/data/co/co-lab-results-sclabs-2024-01-02.xlsx'
results.to_excel(outfile, index=False)

# TODO: Find all of the unique stains in Colorado.
# Note: NLP will be required.


# TODO: Calculate statistics for each strain.
# - totals by month
# - average_total_cannabinoids
# - average_total_thc
# - average_total_cbd
# - average_{cannabinoid}
# - average_total_terpenes
# - average_{terpene}
# - first_date_tested
# - first_producer


# TODO: Archive the strain statistics.
# - created_at
# - updated_at


# TODO: Save images for each strain.
# - Crop the image
# - Upload to Firebase Storage
# - Get a dynamic URL
# - Save the URL and reference to Firestore


# === Image management ===

def remove_bg(input_path: str, output_path: str) -> None:
    """Convert a video file to another video with a transparent background.
    
    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path to save the output image with a transparent background.
    """
    input = Image.open(input_path)
    output = remove(input)
    output.save(output_path)


# Download the images to an image dir.
image_files = []
image_dir = 'D://data/colorado/lab_results/images/sclabs'
if not os.path.exists(image_dir):
    os.makedirs(image_dir)
for index, row in results.iterrows():
    images = ast.literal_eval(row['images'])
    if images:
        coa_id = row['coa_id'].split('-')[0].strip()
        filename = f'{image_dir}/{coa_id}.jpg'
        if os.path.exists(filename):
            image_files.append(filename)
            continue
        image_url = images[0]['url']
        response = requests.get(image_url)
        if response.status_code == 200:
            print(f"Downloaded: {image_url}")
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download: {image_url}")
        image_files.append(filename)
        sleep(2)

# Crop the images.
cropped_images = []
for image_file in image_files:
    cropped_file = image_file.replace('.jpg', '-cropped.png')
    if os.path.exists(cropped_file):
        cropped_images.append(cropped_file)
        continue
    remove_bg(image_file, cropped_file)
    cropped_images.append(cropped_file)
    print(f'Cropped: {cropped_file}')
