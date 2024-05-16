"""
Parsing COAs with AI v2
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/16/2024
Updated: 5/16/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>

Data Sources:

    - [FLMedicalTrees](https://www.reddit.com/r/FLMedicalTrees)

"""
# Standard imports:
import ast
import base64
import json
import os
import re
from time import sleep

# External imports:
from cannlytics.ai.ai import (
    create_prompt_batch,
    save_prompt_batch_results,
    extract_data,
    read_batch_data,
)
from cannlytics.lims.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import logging
import requests
import pandas as pd
import openai
from openai import OpenAI
import pdfplumber
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import spacy


#-----------------------------------------------------------------------
# Setup.
#-----------------------------------------------------------------------

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI.
llm = OpenAI(api_key=dotenv_values('.env')['OPENAI_API_KEY'])

# Define where data is saved.
data_dir = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\159-consumption\data"

# Define where the figures are saved.
assets_dir = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\159-consumption\presentation\images\figures"

# Set figure style.
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 24,
})


#-----------------------------------------------------------------------
# Extract data from COAs with AI.
#-----------------------------------------------------------------------

from cannlytics.lims.compounds import cannabinoids, terpenes

# Metadata prompt.
EXTRACT_COA_METADATA_PROMPT = """Given text from a COA, return any found data, defined in the following table, as JSON. Not all fields may be present in the text. Only return JSON and always return at least an empty object if no data is found. Exclude any field that cannot be found.

| Field | Example | Description |
|-------|---------|-------------|
| `lab` | "MCR Labs" | The lab that tested the sample. |
| `producer` | "Grow House" | The producer of the sampled product. |
| `producer_address` | "3rd & Army, San Francisco, CA 55555" | The producer's address. |
| `date_tested` | 2022-04-20T16:20 | An ISO-formatted time when the sample was tested. |
| `date_received` | 2022-04-20T12:20 | An ISO-formatted time when the sample was received. |
| `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
| `strain_name` | "Blue Rhino" | A strain name, if specified. Otherwise, can be attempted to be parsed from the `product_name`. |
| `product_type` | "flower" | The type of product. This may be "Sample Matrix" on the COA. |
| `batch_number` | "Order-0001" | A batch number for the product. |
| `sample_id` | "Sample-0001" | A lab-specific ID for the sample. |
| `total_cannabinoids` | 14.20 | The total of all cannabinoids in percentage. |
| `total_thc` | 14.00 | The total of delta-9-THC and 0.877 times THCA in percentage. |
| `total_cbd` | 0.20 | The total of CBD and 0.877 times CBDA in percentage. |
| `total_terpenes` | 0.20 | The total terpenes in percentage. |
| `moisture_content` | 13.0 | The moisture percentage. |
| `water_activity` | 0.42 | The water activity value. |
"""

# Extract results prompt.
EXTRACT_COA_CANNABINOIDS_AND_TERPENES_PROMPT="""Given text from a COA, return the percent values for any found cannabinoid or terpene as JSON. Not all compounds may be present in the text. Only return JSON and always return at least an empty object if no values are found. Exclude any compound that cannot be found.

Please adhere to the following guidelines:

* Acceptable values include percentages, "ND", and "<LOQ".
* Use "snake_case" for fields, e.g. given "Delta-9-Tetrahydrocannabinol (Δ-9 THC)" use "delta_9_thc" as the key.
* Make sure to use the percent value, not the mg/g value.
* Do not apply the decarboxylation rate (0.877) to any of the values.
* Include all of the cannabinoids or terpenes that you see. Below is a list of possible cannabinoids/terpenes that may be encountered.

List of possible cannabinoids: {}

List of possible terpenes: {}
""".format(', '.join(cannabinoids), ', '.join(terpenes))

# Notes.
NOTES = """Note: Data was extracted from the text of COAs using OpenAI's GPT models and may include incorrect values."""


#-----------------------------------------------------------------------
# Parse COAs with AI in a batch.
# - Keep track of time and cost it takes to extract data with GPT.
#-----------------------------------------------------------------------

# Read all of the PDFs.
pdf_dir = r'D:\data\reddit\FLMedicalTrees\pdfs'
pdf_files = os.listdir(pdf_dir)
pdf_files = [os.path.join(pdf_dir, x) for x in pdf_files]

# Read all unidentified PDFs.
datafile = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\155-seed-to-smoke\data\unidentified-coas-2024-05-16-01-37-07.json"
with open(datafile, 'r') as file:
    unidentified = json.load(file)
print('Number of unidentified COAs:', len(unidentified))

# Read all parsed COAs.
datafile = r'C:\\Users\\keega\\Documents\\cannlytics\\cannabis-data-science\\season-4\\155-seed-to-smoke\\data\\fl-medical-trees-coa-data-2024-05-16-01-37-07.xlsx'
coa_data = pd.read_excel(datafile)
print('Number of parsed COAs:', len(coa_data))

# Extract COA data from each COA PDF.
coas = []
for pdf_file in pdf_files:
    coa_id = os.path.basename(pdf_file).split('.pdf')[0].split('-coa')[0].split(' ')[0].replace('t3_', '')
    coa = {
        'coa_id': coa_id,
        'pdf_file': pdf_file,
        'coa_data': None,
        'extracted_with_ai': False,
        'model': 'gpt-4o',
    }
    lines = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                for line in page.extract_text().split('\n'):
                    if line not in lines:
                        lines.append(line)
        coa['text'] = '\n'.join(lines)
    except:
        print('Skipping invalid COA:', pdf_file)
        continue
    if pdf_file in unidentified:
        coa['extracted_with_ai'] = True
    else:
        match = coa_data.loc[coa_data['coa_id'].str.contains(coa_id)]
        if len(match) > 0:
            coa['coa_data'] = json.dumps(match.iloc[0].to_dict())
    coas.append(coa)

# DEV:
coas = pd.DataFrame(coas)
coas['coa_id'] = coas['coa_id'].apply(lambda x: x.split(' ')[0])
coas.sort_values('extracted_with_ai', inplace=True)
coas.drop_duplicates(subset='coa_id', keep='first', inplace=True)
print('Number of COAs prepared for extraction:', len(coas))

# Extract metadata from COAs in a batch.
metadata_batch_file = os.path.join(data_dir, 'coa-metadata-batch-duplicate-2024-05-16.jsonl')
metadata_job_id = create_prompt_batch(
    llm,
    coas,
    batch_file=metadata_batch_file,
    system_prompt=EXTRACT_COA_METADATA_PROMPT,
    user_prompt='Extract JSON from the following text:\n\n{}',
    description='Identifying metadata from COA text.',
    id_field='coa_id',
)
print('Metadata job ID: %s' % metadata_job_id)

# Extract cannabinoids and terpenes from COAs in a batch.
results_batch_file = os.path.join(data_dir, 'coa-results-batch-duplicate-2024-05-16.jsonl')
results_job_id = create_prompt_batch(
    llm,
    coas,
    batch_file=results_batch_file,
    system_prompt=EXTRACT_COA_CANNABINOIDS_AND_TERPENES_PROMPT,
    user_prompt='Extract JSON from the following text:\n\n{}',
    description='Identifying results from COA text.',
    id_field='coa_id',
)
print('Results job ID: %s' % metadata_job_id)


#-----------------------------------------------------------------------
# Augment data with the extracted data.
#-----------------------------------------------------------------------

# Check the status of the metadata job.
metadata_status = llm.batches.retrieve(metadata_job_id)
print('Metadata status:', metadata_status.status)

# Check the status of the results job.
results_status = llm.batches.retrieve(results_job_id)
print('Results status:', results_status.status)

# Save the results of the metadata prompt batches.
metadata_outfile = os.path.join(data_dir, 'coa-metadata-results-2024-05-16.jsonl')
save_prompt_batch_results(llm, metadata_status, metadata_outfile)

# Save the results of the results prompt batches.
results_outfile = os.path.join(data_dir, 'coa-results-results-2024-05-16.jsonl')
save_prompt_batch_results(llm, results_status, results_outfile)

# Augment the prompt results.
extracted_metadata = read_batch_data(metadata_outfile)
extracted_results = read_batch_data(results_outfile)
coas['extracted_metadata'] = coas['coa_id'].map(extracted_metadata).apply(json.dumps)
coas['extracted_results'] = coas['coa_id'].map(extracted_results).apply(json.dumps)

# Save the COAs with the extracted data.
timestamp = pd.to_datetime('now').strftime('%Y-%m-%d-%H-%M-%S')
outfile = os.path.join(data_dir, f'extracted-coa-data-{timestamp}.xlsx')
coas.to_excel(outfile, index=False)


#-----------------------------------------------------------------------
# Extract data from a COA PDFs with AI, one-by-one.
#-----------------------------------------------------------------------

# Extract COA data from each COA PDF.
total_cost = 0
extracted_metadata = {}
extracted_results = {}
for index, coa in coas.iterrows():
    coa_id = coa['coa_id']
    text = coa['text']
    if coa_id in extracted_metadata and coa_id in extracted_results:
        print('Skipping already extracted COA:', coa_id)
        continue
    try:

        # Extract metadata.
        metadata, cost = extract_data(
            llm,
            EXTRACT_COA_METADATA_PROMPT,
            user_prompt=f'Extract JSON from the following text:\n\n{text}',
            model='gpt-4o',
            max_tokens=4096,
            temperature=0.0,
            user='cannlytics',  
            verbose=True,
            seed=4200,
        )
        total_cost += cost
        extracted_metadata[coa_id] = json.dumps(metadata)

        # Extract cannabinoids and terpenes.
        results, cost = extract_data(
            llm,
            EXTRACT_COA_CANNABINOIDS_AND_TERPENES_PROMPT,
            user_prompt=f'Extract JSON from the following text:\n\n{text}',
            model='gpt-4o',
            max_tokens=4096,
            temperature=0.0,
            user='cannlytics',  
            verbose=True,
            seed=4200,
        )
        total_cost += cost
        extracted_results[coa_id] = json.dumps(results)
    
    except:
        print('Error extracting data from COA:', coa_id)
        continue

# Augment the COAs with the extracted data.
coas['extracted_metadata'] = coas['coa_id'].map(extracted_metadata)
coas['extracted_results'] = coas['coa_id'].map(extracted_results)

# Save the COAs with the extracted data.
timestamp = pd.to_datetime('now').strftime('%Y-%m-%d-%H-%M-%S')
outfile = os.path.join(data_dir, f'extracted-coa-data-{timestamp}.xlsx')
coas.to_excel(outfile, index=False)
print('Total cost:', total_cost)
print('Extracted data saved to:', outfile)


#-----------------------------------------------------------------------
# Process the extracted COA data for analysis.
#-----------------------------------------------------------------------

from cannlytics.data.coas import get_result_value

# DEV: Read the processed data.
# datafile = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\159-consumption\data\extracted-coa-data-2024-05-16-14-38-53.xlsx"
# coas = pd.read_excel(datafile)

# Create the panel.
panel = []
for index, coa in coas.iterrows():
    observation = {
        'coa_id': coa['coa_id'],
        'pdf_file': coa['pdf_file'],
        'extracted_with_ai': coa['extracted_with_ai'],
        'model': coa['model'],
    }
    coa_data, metadata, results = {}, {}, {}
    if coa['coa_data'] is not None:
        try:
            coa_data = json.loads(coa['coa_data'])
            for compound in cannabinoids + terpenes:
                observation[compound] = get_result_value(coa_data['results'], compound)
        except:
            pass
    if coa['extracted_metadata'] is not None:
        try:
            metadata = json.loads(coa['extracted_metadata'])
            for key, value in metadata.items():
                observation[f'{key}_estimate'] = value
        except:
            pass
    if coa['extracted_results'] is not None:
        try:
            results = json.loads(coa['extracted_results'])
            for key, value in results.items():
                result = pd.to_numeric(str(value).replace('%', ''), errors='coerce')
                observation[f'{key}_estimate'] = result
        except:
            pass
    panel.append(observation)
panel = pd.DataFrame(panel)


#-----------------------------------------------------------------------
# Optional: Post-extraction processing
#-----------------------------------------------------------------------

# # Calculate `sum_of_cannabinoids`.
# sum_of_cannabinoids = 0
# for key, value in extracted_data.items():
#     if 'total' in key:
#         continue
#     try:
#         sum_of_cannabinoids += float(value)
#     except:
#         pass
# extracted_data['sum_of_cannabinoids'] = sum_of_cannabinoids

# Calculate `sum_of_terpenes`.
# total_terpenes = 0
# for key, value in extracted_data.items():
#     if 'total' in key:
#         continue
#     try:
#         total_terpenes += float(value)
#     except:
#         pass
# extracted_data['sum_of_terpenes'] = total_terpenes

# Parse the `producer_address`.


#-----------------------------------------------------------------------
# Estimate the accuracy of parsing COAs with AI
#-----------------------------------------------------------------------

# Calculate the error for each compound.
sample = panel.loc[panel['extracted_with_ai'] == False]
compounds = cannabinoids + terpenes
for compound in compounds:
    try:
        sample[compound] = pd.to_numeric(sample[compound], errors='coerce')
        sample[f'{compound}_estimate'] = pd.to_numeric(sample[f'{compound}_estimate'], errors='coerce')
        sample[f'{compound}_error'] = sample[f'{compound}_estimate'] - sample[compound]
        sample[f'{compound}_error_abs'] = sample[f'{compound}_error'].abs()
        sample[f'{compound}_error_pct'] = sample[f'{compound}_error_abs'] / sample[compound]

        # Visualize the error.
        plt.figure(figsize=(13, 8))
        sns.histplot(sample[f'{compound}_error_pct'], bins=20, kde=True)
        plt.title(f'Error in {compound} estimation')
        plt.xlabel('Error (%)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(assets_dir, f'{compound}-error.png'))
        plt.show()
    except:
        continue

# Calculate the accuracy for each compound.
accuracy = {}
for compound in compounds:
    sample[compound] = pd.to_numeric(sample[compound], errors='coerce')
    try:
        sample[f'{compound}_estimate'] = pd.to_numeric(sample[f'{compound}_estimate'], errors='coerce')
        positive = sample.loc[sample[compound] > 0]
        sample['diff'] = sample[f'{compound}_estimate'] - sample[compound]
        correct = sample.loc[sample['diff'].abs() < 0.05]
        accuracy[compound] = round((len(correct) / len(positive)) * 100, 2)
    except:
        continue
    # sample[f'{compound}_error_pct'] = pd.to_numeric(sample[f'{compound}_error_pct'], errors='coerce')
    

# Sort by accuracy.
accuracy = {k: v for k, v in sorted(accuracy.items(), key=lambda item: item[1], reverse=True)}

# Visualize the accuracy.
plt.figure(figsize=(13, 17))
plt.barh(list(accuracy.keys()), list(accuracy.values()))
plt.title('Accuracy of Data Extraction from COAs with GPT-4o')
plt.xlabel('Accuracy (%)')
plt.ylabel('')
plt.tight_layout()
plt.savefig(os.path.join(assets_dir, 'accuracy.png'))
plt.show()


#-----------------------------------------------------------------------
# Validate the extracted data.
#-----------------------------------------------------------------------

# First, simply check if the extracted data is present in the text.



# Optional: If not present in the text, ask GPT-3 if the value is valid.



#-----------------------------------------------------------------------
# Re-analyze the data with the newly extracted COA data.
#-----------------------------------------------------------------------

# TODO: Correlate COA data with extracted data where both are present.
