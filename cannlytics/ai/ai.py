"""
Cannlytics AI
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/15/2023
Updated: 7/4/2023
"""
# Standard imports:
import json
import math
import os
from time import sleep
from typing import List, Optional

# External imports:
import logging
import google.auth
import openai

# Internal imports:
from cannlytics.firebase import access_secret_version


#-----------------------------------------------------------------------
# OpenAI parameters
#-----------------------------------------------------------------------

# AI warning.
AI_WARNING = "This data was parsed from text using OpenAI's GPT models. Please verify the data before using it. You can submit feedback and report issues to dev@cannlytics.com, thank you."

# OpenAI API model prices (as of 2023-06-06) per 1000 tokens.
PRICE_PER_1000_TOKENS = {
    'gpt-4o': {'prompt': 0.005, 'completion': 0.015},
    'gpt-4': {'prompt': 0.03, 'completion': 0.06},
    'gpt-3.5-turbo': {'prompt': 0.002, 'completion': 0.002},
    'ada': {'prompt': 0.0004, 'completion': 0.0004, 'training': 0.0004, 'usage': 0.0016},
    'babbage': {'prompt': 0.0005, 'completion': 0.0005, 'training': 0.0006, 'usage': 0.0024},
    'curie': {'prompt': 0.002, 'completion': 0.002, 'training': 0.003, 'usage': 0.012},
    'davinci': {'prompt': 0.02, 'completion': 0.02, 'training': 0.03, 'usage': 0.12},
    'dalle_1024': {'usage': 0.02},
    'dalle_512': {'usage': 0.018},
    'dalle_256': {'usage': 0.016},
    'whisper': {'usage': 0.006},
}

# Define the maximum number of tokens per prompt.
MAX_PROMPT_LENGTH = 4096

# Instructional prompt.
INSTRUCTIONAL_PROMPT = 'Only return JSON and always return at least an empty object, {}, if no data can be found. Return a value of `null` for any field that cannot be found.'


#-----------------------------------------------------------------------
# OpenAI initialization.
#-----------------------------------------------------------------------

def initialize_openai(openai_api_key = None) -> None:
    """Initialize OpenAI."""
    if openai_api_key is None:
        try:
            _, project_id = google.auth.default()
            openai_api_key = access_secret_version(
                project_id=project_id,
                secret_id='OPENAI_API_KEY',
                version_id='latest',
            )
        except:
            openai_api_key = os.environ['OPENAI_API_KEY']
    openai.api_key = openai_api_key


#-----------------------------------------------------------------------
# Token and cost management.
#-----------------------------------------------------------------------

def estimate_tokens_of_messages(messages: list, model: Optional[str] = 'gpt-4'):
    """Returns the number of tokens used by a list of messages."""
    tokens_per_message = 4 # every message follows <|start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += math.ceil(len(value) / 4)
            if key == 'name':
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def estimate_tokens_of_string(string: str, model: Optional[str] = 'gpt-4') -> int:
    """Returns the number of tokens in a text string."""
    return estimate_tokens_of_messages([{'role': 'user', 'content': string},], model=model)


def get_prompt_price(prompt, model='gpt-4', prices=PRICE_PER_1000_TOKENS):
    """Returns the price to generate a prompt."""
    num_tokens = estimate_tokens_of_string(prompt, model)
    return num_tokens / 1_000 * prices[model]['prompt']


def get_messages_price(messages, model='gpt-4', prices=PRICE_PER_1000_TOKENS):
    """Returns the price to generate a list of messages."""
    num_tokens = estimate_tokens_of_messages(messages, model)
    return num_tokens / 1_000 * prices[model]['prompt']


def get_tokens_price(num_tokens, model='gpt-4', prices=PRICE_PER_1000_TOKENS):
    """Returns the price to generate a number of tokens."""
    return num_tokens / 1_000 * prices[model]['prompt']


def get_usage_cost(completion, model='gpt-4o', prices=PRICE_PER_1000_TOKENS):
    """Returns the cost of a prompt and completion."""
    content = completion.dict()
    usage = content['usage']
    prompt_cost = usage['prompt_tokens'] / 1_000 * prices[model]['prompt']
    completion_cost = usage['completion_tokens'] / 1_000 * prices[model]['completion']
    return prompt_cost + completion_cost


def split_string(string, max_length):
    """Split a string into chunks of a given length."""
    return [string[i:i+max_length] for i in range(0, len(string), max_length)]


def split_into_token_chunks(
        text: str,
        max_prompt_length: int,
        model: Optional[str] = 'gpt-4',
    ) -> List[str]:
    """Split a body of text into desired portions less than a given
    desired length in tokens.
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = ''
    for line in lines:
        if estimate_tokens_of_string(current_chunk + '\n' + line, model) <= max_prompt_length:
            current_chunk += '\n' + line
        else:
            chunks.append(current_chunk)
            current_chunk = line
    chunks.append(current_chunk)
    return chunks


#-----------------------------------------------------------------------
# Engineered prompts.
#-----------------------------------------------------------------------

# DEPRECATED:
def gpt_to_json(
        text: str,
        system_prompts: List[str],
        model: Optional[str] = 'gpt-4',
        max_tokens: Optional[int] = 4_000,
        temperature: Optional[float] = 0.0,
        user: Optional[str] = 'cannlytics',
        openai_api_key: Optional[str] = None,
        verbose: Optional[bool] = False,
        retry_pause: Optional[float] = 3.33,
        text_label: Optional[str] = 'Text',
        json_label: Optional[str] = 'JSON',
    ) -> dict:
    """Prompt GPT and convert the output content to JSON."""

    # Add the system prompts.
    messages = []
    for system_prompt in system_prompts:
        messages.append({'role': 'system', 'content': system_prompt})
    
    # Add the main prompt.
    main_prompt = f'{text_label}: ' + text + f'\n\n{json_label}:'
    messages.append({'role': 'user', 'content': main_prompt})

    # Make the request to the OpenAI API.
    try:
        if verbose:
            print('MESSAGES:', messages)
        try:
            initialize_openai(openai_api_key)
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                user=user,
            )

        # Retry the request if it fails.
        except:
            if retry_pause:
                if verbose:
                    print('First OpenAI query failed, retrying.')
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
        content = response['choices'][0]['message']['content']
        if verbose:
            print('CONTENT:', content)
    except:
        if verbose:
            print('OpenAI query failed.')

    # Get the structured the data.
    try:
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        extract = json.loads(content[start_index:end_index])
    except:
        extract = {}
        if verbose:
            print('JSON parsing failed.')

    # Calculate the cost of the request.
    try:
        cost = get_tokens_price(messages, model=model)
    except:
        cost = 0

    # Return the extracted data.
    return extract, cost


def extract_completion(completion):
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


def extract_data(
        client,
        extraction_prompt: str,
        user_prompt: str,
        model = 'gpt-4o',
        max_tokens = 4_096,
        temperature = 0.0,
        user = 'cannlytics',  
        verbose = True,
        seed = None,
    ):
    """Extract strains from text using OpenAI's GPT model."""
    messages = [
        {'role': 'system', 'content': extraction_prompt},
        {'role': 'user', 'content': user_prompt}
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        user=user,
        response_format={"type": "json_object"},
        seed=seed,
    )
    if verbose: logging.info(f'RESPONSE: {json.dumps(completion.dict())}')
    cost = get_usage_cost(completion, model=model)
    extract = extract_completion(completion)
    return extract, cost


#-----------------------------------------------------------------------
# OpenAI Batches
#-----------------------------------------------------------------------


def create_prompt_batch_file(
        prompts,
        batch_file: str,
        system_prompt: str,
        user_prompt: str,
        text_key='text',
        id_field='custom_id',
        max_tokens=4096,
        model='gpt-4o',
        temperature=0.0,
        user='cannlytics',
        seed=4200,
    ):
    """Create a batch file."""
    with open(batch_file, "w") as f:
        for _, obs in prompts.iterrows():
            prompt = user_prompt.format(obs[text_key])
            custom_id = obs[id_field]
            request = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "user": user,
                    "response_format": {"type": "json_object"},
                    "seed": seed
                }
            }
            f.write(json.dumps(request) + "\n")


def create_prompt_batch(
        client,
        prompts,
        batch_file: str,
        system_prompt: str,
        user_prompt: str,
        description='',
        text_key='text',
        id_field='custom_id',
        max_tokens=4096,
        model='gpt-4o',
        temperature=0.0,
        user='cannlytics',
        seed=4200,
        verbose=True,
    ):
    """Create a batch of OpenAI prompts."""
    # Create a batch file.
    create_prompt_batch_file(
        prompts,
        batch_file,
        system_prompt,
        user_prompt,
        text_key=text_key,
        id_field=id_field,
        max_tokens=max_tokens,
        model=model,
        temperature=temperature,
        user=user,
        seed=seed,
    )

    # Upload the batch file.
    if verbose: logging.info(f"Uploading batch file: '{batch_file}'")
    batch_input_file = client.files.create(
        file=open(batch_file, "rb"),
        purpose="batch",
    )
    if verbose: logging.info(f"Uploaded batch file: {batch_input_file.id}")

    # Create the batch job.
    job = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": description}
    )
    if verbose: logging.info(f'Created prompt batch: {job.id}')
    return job.id


def read_batch_data(batch_file, field=None):
    """Merge a field from a batch."""
    extraction = {}
    with open(batch_file, 'r') as f:
        batch_results = [json.loads(line) for line in f]
    for result in batch_results:
        custom_id = result["custom_id"]
        content = result["response"]["body"]["choices"][0]["message"]["content"]
        content_json = json.loads(content)
        if field:
            extraction[custom_id] = content_json[field]
        else:
            extraction[custom_id] = content_json
    return extraction


def save_prompt_batch_results(client, status, outfile):
    """Retrieve the results of the batch job."""
    content = client.files.content(status.output_file_id)
    content.write_to_file(outfile)
