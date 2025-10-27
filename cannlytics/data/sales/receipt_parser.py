"""
BudSpender | Cannabis Receipt Parser
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/24/2023
Updated: 10/2/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import hashlib
import json
import gc
import os
from typing import Optional

# External imports:
from cannlytics.models import Receipt
from openai import OpenAI
from cannlytics.data import create_hash
import pandas as pd

# Define the prompts.
# FIXME: Re-write the prompts for receipts.
PARSE_RECEIPT_SYSTEM_PROMPT = "Please try your hardest to extract structured data defined in the `Label` model from the image. The image may or may not be a label. If the image is not a label of a cannabis product, then simply return the text 'Invalid'. If you do find data, then please return any field found. If a field is not found, then return '' or 0.0. Use your best judgement in matching similarly named fields."
PARSE_RECEIPT_USER_PROMPT = "Please try your hardest to extract structured data defined in the `Label` model from the image."


class ReceiptsParser(object):
    """A cannabis receipt parser, powered by OpenAI."""

    def __init__(
            self,
            default_config: Optional[str] = '--oem 3 --psm 6',
            openai_api_key: Optional[str] = None,
            model: Optional[str] = 'gpt-4o-mini',
            max_tokens: Optional[int] = 128_000,
        ) -> None:
        """Initialize an Open Data API client.
        Args:
            default_config: The default configuration for OpenCV.
            openai_api_key: The OpenAI API key.
            model: The OpenAI model to use, 'gpt-4o-mini' by default.
            base_prompt: The base prompt to use for the OpenAI model.
        """
        # Parameters.
        self.default_config = default_config
        self.openai_api_key = openai_api_key
        self.model = model
        self.max_tokens = max_tokens

        # State.
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.img = None
        self.image_text = ''
        self.extracted_data = None

    def parse(
            self,
            doc: str,
            client: Optional[OpenAI] = None,
            system_prompt: Optional[str] = None,
            user_prompt: Optional[str] = None,
            model: Optional[str] = 'gpt-4o-mini',
            image_detail: Optional[str] = 'high',
            max_tokens: Optional[int] = None,
            seed: Optional[int] = None,
            temperature: Optional[float] = 0.0,
            verbose: Optional[bool] = False,
        ) -> dict:
        """Parse data from a document with OpenAI's GPT vision model."""
        if system_prompt is None:
            system_prompt = PARSE_RECEIPT_SYSTEM_PROMPT
        if user_prompt is None:
            user_prompt = PARSE_RECEIPT_USER_PROMPT
        if client is None:
            client = OpenAI()
        base64_image = self.encode_image(doc)
        url = f'data:image/jpeg;base64,{base64_image}'
        image_url = {'url': url, 'detail': image_detail}
        messages = [
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': user_prompt},
                    {'type': 'image_url', 'image_url': image_url},
                ]
            }
        ]
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=Receipt,
            max_tokens=max_tokens,
            seed=seed,
            temperature=temperature,
        )
        obs = completion.choices[0].message.parsed.dict()
        usage = completion.usage.to_dict()
        if verbose:
            print('PARSED:', obs)
            print('USAGE:', usage)

        # FIXME: Calculate metadata.

        # # Calculate total price.
        # prices = obs.get('product_prices', [])
        # obs['total_price'] = 0
        # for price in prices:
        #     try:
        #         obs['total_price'] += float(price)
        #     except:
        #         pass

        # # Calculate total tax.
        # obs['total_tax'] = 0
        # tax_keys = [key for key in obs.keys() if '_tax' in key]
        # for key in tax_keys:
        #     try:
        #         obs['total_tax'] += float(obs[key])
        #     except:
        #         pass

        # # Calculate total transactions.
        # obs['total_transactions'] = len(prices)

        # Return the parsed data.
        obs['file_hash'] = self.hash_file(doc)
        obs['file_name'] = os.path.basename(doc).split('.')[0]
        obs['parsed_at'] = datetime.now().isoformat()
        obs['id'] = create_hash(obs, private_key='')
        self.prompt_tokens += usage['prompt_tokens']
        self.completion_tokens += usage['completion_tokens']
        return obs
    
    def save(self, obs, filename):
        """Save a receipt to a file."""
        if filename.endswith('json'):
            with open(filename, 'w') as f:
                json.dump(obs, f, indent=4)
                f.close()
        elif filename.endswith('csv'):
            pd.DataFrame([obs]).to_csv(filename)
        elif filename.endswith('xlsx'):
            pd.DataFrame([obs]).to_excel(filename)
        else:
            raise ValueError(f'Unknown file type: {filename}')
        
    def hash_file(self, file_path):
        """Hash a file to use as a cache key."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        return hasher.hexdigest()
        
    def quit(self):
        """Reset the parser and perform garbage cleaning."""
        self.model = 'gpt-4o-mini'
        self.openai_api_key = None
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.img = None
        self.image_text = ''
        self.extracted_data = None
        gc.collect()


# === Tests ===
# [✓] Tested: 2024-10-02 by Keegan Skeate <admin@cannlytics.com>
if __name__ == '__main__':

    # Initialize OpenAI.
    import os
    from dotenv import dotenv_values
    config = dotenv_values('../../../.env')
    os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']

    # Initialize a receipt parser.
    parser = ReceiptsParser()

    # [ ] TEST: Parse a receipt.
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    image_file = '../../../.datasets/receipts/tests/receipt-1.jpg'
    outfile = f'../../../.datasets/receipts/tests/receipt-1-{timestamp}.xlsx'
    data = parser.parse(image_file)
    print('Parsed:', data)
    print('Prompt tokens:', parser.prompt_tokens)
    print('Completion tokens:', parser.completion_tokens)
    parser.save(data, outfile)
    print('Saved:', outfile)
