# Standard imports:
import ast
import base64
import json
import os
import re
from time import sleep

# External imports:
from cannlytics.lims.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import requests
import pandas as pd
from openai import OpenAI



# === Parse COAs ===

# Base prompt.
INSTRUCTIONAL_PROMPT = 'You are a certificate of analysis (COA) parser designed to extract data from COA text. Only return JSON and always return at least an empty object, {}, if no data can be found. Return a value of `null` for any field that cannot be found.'
NOTES = """Note: Data was extracted from images of COAs using OpenAI's GPT models and may include incorrect values."""


def download_coa_image(url, image_dir):
    """Download a COA image."""
    filename = url.split('/')[-1].replace('?c=1', '')
    coa_image = os.path.join(image_dir, filename)
    if not os.path.exists(coa_image):
        response = requests.get(url)
        with open(coa_image, 'wb') as doc:
            doc.write(response.content)
    return coa_image


def encode_image(image_path):
        """Encode an image as a base64 string."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        

def extract_completion_json(completion):
    """Extract JSON from a OpenAI completion."""
    content = completion.choices[0].message.content
    extracted_json = content.lstrip('```json\n').split('\n```')[0]
    try:
        extracted_data = json.loads(extracted_json)
    except:
        try:
            if not content.endswith('"'):
                content += '"'
            extracted_data = json.loads(extracted_json + '}')
        except:
            extracted_data = json.loads(','.join(extracted_json.split(',')[:-1]) + '}')
    return extracted_data


def extract_coa_metadata(
        client,
        coa,
        model = 'gpt-4-vision-preview', # Alt: gpt-4-0125-preview
        detail = 'high',
        max_tokens = 4_096,
        temperature = 0.0,
        user = 'cannlytics',  
        method = 'image',
        verbose = True,
    ) -> dict:
    if method == 'image':
        extraction_prompt = 'Given the attached image of a COA'
    else:
        extraction_prompt = 'Given text from a COA'
    extraction_prompt += """, extract JSON, where:\n
    | Field | Example | Description |
    |-------|---------|-------------|
    | `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
    | `product_type` | "flower" | The type of product. |
    | `sample_id` | "Sample-0001" | A lab-specific ID for the sample. |
    | `sample_received` | 2022-04-20T16:20 | An ISO-formatted time when the sample was received. |
    | `report_created` | 2022-04-20T16:20 | An ISO-formatted time when the report was created. |
    | `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
    | `total_thc` | 14.00 | The analytical total of THC and THCA. |
    | `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
    """
    if method == 'image':
        base64_image = encode_image(coa)
    else:
        material_prompt = 'COA text:\n\n' + coa
    messages = [
        {'role': 'system', 'content': INSTRUCTIONAL_PROMPT},
        {'role': 'system', 'content': extraction_prompt},
    ]
    if method == 'image':
        messages.append(
        {
            'role': 'user',
            'content': [
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{base64_image}',
                        'detail': detail,
                    },
                },
            ],
        })
    else:
        messages.append({'role': 'user', 'content': material_prompt})
    if verbose:
        print('\n\n'.join([x.get('content') for x in messages if isinstance(x.get('content'), str)]))
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        user=user,
    )
    if verbose:
        print('RESPONSE:', json.dumps(completion.dict()))
    return extract_completion_json(completion)


def extract_coa_cannabinoids(
        client,
        coa,
        model = 'gpt-4-vision-preview',
        detail = 'high',
        user = 'cannlytics',
        max_tokens = 4_096,
        temperature = 0.0,
        method = 'image',
        verbose = True,
        analytes = [],
        normalize = None,
    ) -> dict:
    if method == 'image':
        extraction_prompt = 'Given the attached image of a COA'
    else:
        extraction_prompt = 'Given text from a COA'
    extraction_prompt += """, extract JSON, where:\n
    | Field | Example | Description |
    |-------|---------|-------------|
    | `{cannabinoid}` | 0.20 | The percent (%) value for the cannabinoid. Acceptable values include "ND" and "<LOQ". |

    \nPlease use "snake_case" for fields, e.g. "Delta-9-Tetrahydrocannabinol (Δ-9 THC)" as "delta_9_thc".

    \nPlease make sure to use the percent value.

    \nPlease include all of the cannabinoids that you see. Below is a list of possible cannabinoids that may be encountered.

    \nDo not apply the decarboxylation rate (0.877) to any of the values.
    """
    extraction_prompt += '\n' + '\n'.join(analytes)
    if method == 'image':
        base64_image = encode_image(coa)
    else:
        material_prompt = 'COA text:\n' + coa
    messages = [
        {'role': 'system', 'content': INSTRUCTIONAL_PROMPT},
        {'role': 'system', 'content': extraction_prompt},
    ]
    if method == 'image':
        messages.append(
        {
            'role': 'user',
            'content': [
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{base64_image}',
                        'detail': detail,
                    },
                },
            ],
        })
    else:
        messages.append({'role': 'user', 'content': material_prompt})
    if verbose:
        print('\n\n'.join([x.get('content') for x in messages if isinstance(x.get('content'), str)]))
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        user=user,
    )
    if verbose:
        print('RESPONSE:', json.dumps(completion.dict()))
    
    # Format the completion.
    extracted_data = extract_completion_json(completion)

    # Calculate `sum_of_cannabinoids` as a double check.
    sum_of_cannabinoids = 0
    for key, value in extracted_data.items():
        if 'total' in key:
            continue
        try:
            sum_of_cannabinoids += float(value)
        except:
            pass
    extracted_data['sum_of_cannabinoids'] = sum_of_cannabinoids

    # Return the extracted data.
    return extracted_data


def extract_coa_terpenes(
        client,
        coa,
        model = 'gpt-4-vision-preview',
        detail = 'high',
        user = 'cannlytics',
        max_tokens = 4_096,
        temperature = 0.0,
        method = 'image',
        units = 'mg/g',
        normalize = 10,
        analysis = 'terpenes',
        example_name = 'Caryophyllene Oxide',
        example_key = 'caryophyllene_oxide',
        analytes = [],
        verbose = True,
    ) -> dict:
    if method == 'image':
        extraction_prompt = 'Given the attached image of a COA'
    else:
        extraction_prompt = 'Given text from a COA'
    extraction_prompt += """, extract JSON, where:

    | Field | Example | Description |
    |-------|---------|-------------|
    | `total_{analysis}` | 0.42 | The sum of all {analysis} measured. |
    | `{{terpene}}` | 0.20 | The {units} value for the {analysis}. Acceptable values include "ND" and "<LOQ". |
    | `primary_aromas` | ["earthy", "sweet", "gas"] | The primary aromas of the sample. |

    \nPlease use "snake_case" for fields, e.g. "{example_name}" as "{example_key}".

    \nPlease make sure to use the {units} value.

    \nPlease include all of the {analysis} that you see. Below is a list of possible cannabinoids that may be encountered.
    """.format(
        units=units,
        analysis=analysis,
        example_name=example_name,
        example_key=example_key,
    )
    extraction_prompt += '\n' + '\n'.join(analytes)
    if method == 'image':
        base64_image = encode_image(coa)
    else:
        material_prompt = 'COA text:\n' + coa
    messages = [
        {'role': 'system', 'content': INSTRUCTIONAL_PROMPT},
        {'role': 'system', 'content': extraction_prompt},
    ]
    if method == 'image':
        messages.append(
        {
            'role': 'user',
            'content': [
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{base64_image}',
                        'detail': detail,
                    },
                },
            ],
        })
    else:
        messages.append({'role': 'user', 'content': material_prompt})
    if verbose:
        print('\n\n'.join([x.get('content') for x in messages if isinstance(x.get('content'), str)]))
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        user=user,
    )
    if verbose:
        print('RESPONSE:', json.dumps(completion.dict()))

    # Format the completion.
    extracted_data = extract_completion_json(completion)

    # Convert mg/g to percent.
    if normalize:
        for key, value in extracted_data.items():
            try:
                extracted_data[key] = float(value) / normalize
            except:
                pass

    # Calculate `total_terpenes` as a double check.
    total_terpenes = 0
    for key, value in extracted_data.items():
        if 'total' in key:
            continue
        try:
            total_terpenes += float(value)
        except:
            pass
    extracted_data['sum_of_terpenes'] = total_terpenes

    # Return the extracted data.
    return extracted_data


# FIXME: Refactor:


# Initialize OpenAI.
config = dotenv_values('../../.env')
openai_api_key = config['OPENAI_API_KEY']
client = OpenAI()

# Image properties.
image_dir = 'D:/data/work/flowgardens/images'
image_size = '7200x7200'

# Download the images of the cannabinoids and terpenes COAs.
all_extracted_data = []
for index, obs in coa_data.iterrows():
    print('Extracting data for:', obs['strain_name'])

    # Download the cannabinoid COA image.
    try:
        cannabinoid_image_url = [x for x in obs['image_urls'] if 'COA' in x][0]
        cannabinoid_image_url = cannabinoid_image_url.replace('50x50', image_size)
        cannabinoid_coa = download_coa_image(cannabinoid_image_url, image_dir)
    except:
        print('No cannabinoid COA found.')
        cannabinoid_coa = None

    # Download the terpene COA image.
    sleep(3.33)
    try:
        terpene_image_url = [x for x in obs['image_urls'] if 'Terp' in x][0]
        terpene_image_url = terpene_image_url.replace('50x50', image_size)
        terpene_coa = download_coa_image(terpene_image_url, image_dir)
    except:
        print('No terpene COA found.')
        terpene_coa = None

    # Continue if no COAs are attached.
    if not cannabinoid_coa or not terpene_coa:
        continue

    # Optional: Extract the text from the COA images.
    # obs['cannabinoid_text'] = pytesseract.image_to_string(cannabinoid_coa, config='--oem 3 --psm 6')
    # obs['terpene_text'] = pytesseract.image_to_string(terpene_coa, config='--oem 3 --psm 6')
    # obs['metadata_text'] = obs['cannabinoid_text']

    # Extract COA metadata.
    if cannabinoid_coa:
        metadata = extract_coa_metadata(client, cannabinoid_coa)
    else:
        metadata = extract_coa_metadata(client, terpene_coa)
    obs = pd.Series({**obs, **metadata})

    # Extract cannabinoid data.
    if cannabinoid_coa:
        sleep(3.33)
        cannabinoid_data = extract_coa_cannabinoids(
            client,
            cannabinoid_coa,
            analytes=specific_cannabinoids,
        )
        obs = pd.Series({**obs, **cannabinoid_data})

    # Extract terpene data.
    if terpene_coa:
        sleep(3.33)
        terpene_data = extract_coa_terpenes(
            client,
            terpene_coa,
            analytes=specific_terpenes,
        )
        obs = pd.Series({**obs, **terpene_data})

    # Optional: Get total_terpenes and primary_aromas in a separate call.

    # Record the extracted data.
    all_extracted_data.append(obs.to_dict())

# Rename fields of the extracted data.
extraction = pd.DataFrame(all_extracted_data)
extraction.rename(columns={
    'report_created': 'date_tested',
    'sample_received': 'date_received',
    'sample_id': 'lab_id',
    'primary_aromas': 'predicted_aromas',
}, inplace=True)

# Save all of the extracted data.
timestamp = pd.to_datetime('now').strftime('%Y-%m-%d-%H-%M-%S')
outfile = f'{data_dir}/flowgardens-coa-data-{timestamp}.xlsx'
extraction.to_excel(outfile, index=False)



#-----------------------------------------------------------------------
# Parse COAs with vision in one-shot.
#-----------------------------------------------------------------------

# TODO: Benchmark the speed and cost of the different models.
model = 'gpt-4o'







#-----------------------------------------------------------------------
# Parse COAs with text in one-shot.
#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
# Parse COAs with text step-by-step.
#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
# Estimate the accuracy of the various methods..
#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
# Validate the extracted data.
#-----------------------------------------------------------------------

# First, simply check if the extracted data is present in the text.



# TODO: If not present in the text, ask GPT-3 if the value is valid.



#-----------------------------------------------------------------------
# Validate the extracted data.
#-----------------------------------------------------------------------
