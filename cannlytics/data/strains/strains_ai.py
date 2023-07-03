"""
StrainsAI
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/29/2023
Updated: 7/2/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import csv
import json
from time import sleep
from typing import List, Optional

# External imports:
from cannlytics.ai import INSTRUCTIONAL_PROMPT, initialize_openai
import pandas as pd
import openai


def generate_strain_art():
    """Generate a description for a strain."""
    # TODO: Implement!
    raise NotImplementedError


def generate_strain_description():
    """Generate a description for a strain."""
    

    # TODO: Supplement with lab result data!


    raise NotImplementedError


def identify_strains(
        text,
        model='gpt-4',
        max_tokens: Optional[int] = 1_000,
        temperature: Optional[float] = 0.0,
        user: Optional[str] = 'cannlytics',
        verbose: Optional[bool] = False,
        retry_pause: Optional[float] = 3.33,
        instructional_prompt: Optional[str] = None,
        identification_prompt: Optional[str] = None,
        json_key: Optional[str] = 'strains',
    ) -> List[dict]:
    """Identify the closest strain(s) from a strain name."""

    # Format the prompt.
    if instructional_prompt is None:
        instructional_prompt = INSTRUCTIONAL_PROMPT
    if identification_prompt is None:
        identification_prompt = 'Given the following cannabis product name or text, what is the strain(s) of cannabis? Return your answer as JSON, e.g. {"strains": ["X"]} or {"strains": ["Strain 1", "Strain 2"]} where strains is a list of the strains, where sometimes multiple strains are indicated by a cross, e.g. "Strain 1 x Strain 2".'

    # Format the message.
    messages = [
        {'role': 'system', 'content': INSTRUCTIONAL_PROMPT},
        {'role': 'system', 'content': identification_prompt},
        {'role': 'user', 'content': f'Text: {text}\n\nStrains:'}
    ]

    # Make the request to OpenAI. 
    try:
        initialize_openai(openai_api_key)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            user=user,
        )
    except:
        if retry_pause:
            sleep(retry_pause)
            initialize_openai(openai_api_key)
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                user=user,
            )
    
    # Get the content of the response.
    if verbose:
        print('RESPONSE:', response)
    content = response['choices'][0]['message']['content']
    start_index = content.find('{')
    end_index = content.rfind('}') + 1

    extracted_data = []
    try:
        obj = json.loads(content[start_index:end_index])
        extracted_data.extend(obj[json_key])
    except:
        if verbose:
            print('Failed to extract data.')

    # Return the extracted data.
    # TODO: Return the prompts and cost.
    return extracted_data


def train_strain_name_identification_model():
    """Train a model to identify strain names."""

    # TODO: Get strain name vocabulary.
    strain_vocab_file = 'strain-vocab.txt'
    strain_data = pd.read_excel('ccrs-strain-statistics-2023-03-07.xlsx')
    strain_data['strain_name'] = strain_data['strain_name'].apply(
        lambda x: x.title()
    )
    strain_data.drop_duplicates(subset=['strain_name'], inplace=True)
    strain_data.sort_values(by=['strain_name'], inplace=True)
    strain_data.to_csv(
        strain_vocab_file,
        header=None,
        index=None,
        sep='\t',
        mode='w',
        columns=['strain_name'],
        quoting=csv.QUOTE_NONE,
        # escapechar=None
    )

    # TODO: Fine-tine a model to identify strain names.

    raise NotImplementedError


# === Tests ===
# Performed 2023-07-01 by Keegan Skeate <admin@cannlytics.com>.
if __name__ == '__main__':

    from dotenv import dotenv_values
    print('Testing strains AI...')

    # Initialize OpenAI.
    config = dotenv_values('../../../.env')
    openai_api_key = config['OPENAI_API_KEY']

    # [✓] TEST: Identify strain names.
    text = 'GARCIA HAND PICKED DARK KARMA'
    strain_names = identify_strains(text)
    print(strain_names)
