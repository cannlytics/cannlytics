"""
Strain Identifier
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/13/2024
Updated: 12/15/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json
import os
from time import sleep

# External imports:
from openai import OpenAI
import pandas as pd


# Default prompts for strain identification.
INSTRUCTIONAL_PROMPT = (
    'Please try your hardest to extract any cannabis strain names in given text as JSON with field `strain_names`. '
    'The text is human-entered and may contain extraneous text or text that is not a strain name. '
    'Please return any text that looks like it could be a cannabis strain name as JSON. '
)

IDENTIFICATION_PROMPT = 'Please return any cannabis strains in the following text as JSON with field `strain_names`: %s'

RESPONSE_FORMAT = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'StrainNames',
        'description': 'A list of cannabis strain names. An empty list if none.',
        'schema': {
            'type': 'object',
            'properties': {
                'strain_names': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'description': 'A list of cannabis strain names'
                }
            },
            'required': ['strain_names'],
            # 'additionalProperties': False
        },
        'strict': True
    }
}


def handle_capitalized_names(name: str) -> str:
    """Clean up names by properly casing them if they are all uppercase."""
    if name.isupper():
        return name.title()
    return name


class StrainIdentifier:
    """A reusable class for identifying cannabis strains from text."""

    def __init__(
            self, 
            client: OpenAI,
            model: str = 'gpt-4o-mini',
            instructional_prompt: str = INSTRUCTIONAL_PROMPT,
            identification_prompt: str = IDENTIFICATION_PROMPT,
            max_tokens: int = None,
            temperature: float = 0.0,
            user: str = 'cannlytics'
        ):
        self.client = client
        self.model = model
        self.instructional_prompt = instructional_prompt
        self.identification_prompt = identification_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.user = user

    def identify_strains(self, text: str):
        """
        Identify cannabis strain names from a given text.
        
        Args:
            text: The text to analyze for strain names.
            
        Returns:
            Tuple[List[str], dict]: A tuple of the identified strain names and the usage details.
        """
        messages = [
            {'role': 'system', 'content': self.instructional_prompt},
            {'role': 'user', 'content': self.identification_prompt % text}
        ]
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            user=self.user,
            response_format={"type": "json_object"}  # Specify JSON response format
        )
        usage = completion.usage.model_dump()
        content = json.loads(completion.choices[0].message.content)
        strain_names = content.get('strain_names', [])
        strain_names = [handle_capitalized_names(name) for name in strain_names]
        return strain_names, usage

    def identify_strains_batch(
            self,
            data: pd.DataFrame,
            text_column: str,
            id_column: str,
            batch_dir: str = 'standard-strain-names',
            verbose: bool = False,
            pause: int = 300
        ):
        """
        Run a batch job to identify `strain_names` for multiple entries and return a dict of results.

        Args:
            data (pd.DataFrame): DataFrame containing the text to analyze.
            text_column (str): Name of the column containing text to analyze.
            id_column (str): Name of the column containing a unique identifier.
            batch_dir (str): Directory to store batch files.
            verbose (bool): If True, print detailed information.
            pause (int): Seconds to wait between status checks of the batch job.

        Returns:
            Dict[str, List[str]]: A dictionary mapping IDs to lists of identified strains.
        """
        os.makedirs(batch_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        batch_file = os.path.join(batch_dir, f'standard-strain-names-batch-{timestamp}.jsonl')
        results_file = os.path.join(batch_dir, f'standard-strain-names-batch-results-{timestamp}.jsonl')

        # Create batch file with prompts
        with open(batch_file, 'w') as f:
            for _, row in data.iterrows():
                text = row[text_column]
                messages = [
                    {'role': 'system', 'content': self.instructional_prompt},
                    {'role': 'user', 'content': self.identification_prompt % text}
                ]
                prompt = {
                    'custom_id': str(row[id_column]),
                    'method': 'POST',
                    'url': '/v1/chat/completions',
                    'body': {
                        'model': self.model,
                        'messages': messages,
                        'max_tokens': self.max_tokens,
                        'temperature': self.temperature,
                        'user': self.user,
                        'response_format': RESPONSE_FORMAT,
                    }
                }
                f.write(json.dumps(prompt) + '\n')
        if verbose:
            print(f'Created batch file: {batch_file}')

        # Upload batch file and create job.
        batch_input_file = self.client.files.create(file=open(batch_file, 'rb'), purpose='batch')
        job = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint='/v1/chat/completions',
            completion_window='24h',
            metadata={'description': f'Identifying strains for batch {timestamp}'}
        )
        if verbose:
            print(f'Batch job started: {job.id}')

        # Wait for job completion.
        while job.status != 'completed':
            job = self.client.batches.retrieve(job.id)
            if verbose:
                print(f'Job status: {job.status}')
            if job.status == 'failed':
                raise Exception('Batch job failed')
            if job.status != 'completed':
                sleep(pause)

        # Save batch results.
        batch_results = self.client.files.content(job.output_file_id)
        batch_results.write_to_file(results_file)
        if verbose:
            print(f'Saved batch results: {results_file}')

        # Parse the results.
        strain_dict = {}
        with open(results_file, 'r') as f:
            for line in f:
                result = json.loads(line)
                custom_id = result['custom_id']
                content = json.loads(result['response']['body']['choices'][0]['message']['content'])
                names = content.get('strain_names', [])
                names = [handle_capitalized_names(name) for name in names]
                strain_dict[custom_id] = names
        return strain_dict


# === Tests ===
if __name__ == '__main__':

    from dotenv import dotenv_values

    # Read environment variables.
    config = dotenv_values('./.env')

    # Initialize OpenAI.
    openai_api_key = config['OPENAI_API_KEY']
    os.environ['OPENAI_API_KEY'] = openai_api_key
    client = OpenAI()

    # Initialize the identifier.
    identifier = StrainIdentifier(
        client=client,
        model='gpt-4o-mini'
    )

    # Extract strain names from text.
    text = 'Old-time Moonshine'
    strains, usage = identifier.identify_strains(text)
    print('Strains:', strains)
