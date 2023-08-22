"""
StrainsAI
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/29/2023
Updated: 8/21/2023
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


def generate_strain_art(
        name: str,
        openai_api_key: Optional[str] = None,
        art_style=' in the style of pixel art',
        n=1,
        size='1024x1024',
        user: Optional[str] = 'cannlytics',
    ) -> str:
    """Generate a strain art image URL given text."""
    initialize_openai(openai_api_key)
    response = openai.Image.create(
        prompt=name + art_style,
        n=n,
        size=size,
        user=user,
    )
    image_url = response['data'][0]['url']
    return image_url


def generate_strain_description(
        name: str,
        stats: Optional[dict] = None,
        instructions: Optional[str] = None,
        model='gpt-4',
        openai_api_key: Optional[str] = None,
        max_tokens: Optional[int] = 1_000,
        temperature: Optional[float] = 0.42,
        word_count=50,
        user: Optional[str] = 'cannlytics',
        retry_pause: Optional[float] = 3.33,
        verbose: Optional[bool] = False,
    ) -> str:
    """Generate a description for a strain or product given text."""

    # Begin the message with the instructional prompt.
    identification_prompt = f'Given the following cannabis strain, product name, or text, can you please provide a {word_count} word description? Please only answer with the description.'
    messages = [{'role': 'system', 'content': identification_prompt}]

    # Add any additional instructions.
    if instructions is not None:
        messages.append({'role': 'system', 'content': instructions})

    # Incorporate information, such as lab results or stats.
    if stats is not None:
        info = json.dumps(stats)
        messages.append({
            'role': 'system',
            'content': f'Try to incorporate this information in the description: {info}'
        })

    # Add the text and finish the prompt.
    messages.append({
        'role': 'user',
        'content': f'Text: {name}\n\nDescription:',
    })
    if verbose:
        print('MESSAGES:', messages)

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
        print('RESPONSE:', json.dumps(response))

    # Return the content.
    return response['choices'][0]['message']['content']


def identify_strains(
        text,
        model='gpt-4',
        openai_api_key: Optional[str] = None,
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
        print('RESPONSE:', json.dumps(response))
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
# Performed 2023-07-10 by Keegan Skeate <admin@cannlytics.com>.
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

    # [✓] TEST: Generate strain art.
    image_url = generate_strain_art(
        text,
        openai_api_key=openai_api_key,
    )
    print(image_url)

    # [✓] TEST: Generate strain description.
    short_description = generate_strain_description(
        text,
        model='gpt-3.5-turbo',
        temperature=0.5,
        word_count=15,
        verbose=True,
    )
    long_description = generate_strain_description(
        text,
        model='gpt-3.5-turbo',
        temperature=0.5,
        word_count=300,
        verbose=True,
    )
    creative_description = generate_strain_description(
        text,
        model='gpt-3.5-turbo',
        temperature=1.0,
        word_count=60,
        verbose=True,
    )
    scientific_description = generate_strain_description(
        text,
        model='gpt-3.5-turbo',
        temperature=0.0,
        word_count=60,
        verbose=True,
    )
