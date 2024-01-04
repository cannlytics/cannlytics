"""
Cannabis Labels Parser
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 11/23/2023
Updated: 11/24/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import base64
from datetime import datetime
import json
import gc
import re
from typing import Optional

# External imports:
from cannlytics.ai import (
    AI_WARNING,
    INSTRUCTIONAL_PROMPT,
    MAX_PROMPT_LENGTH,
)
from cannlytics.data import create_hash
import cv2
from openai import OpenAI
import pandas as pd
import pdfplumber
import pytesseract


# Prompt to parse data from a cannabis receipt.
EXTRACT_LABEL_DATA_PROMPT = """Given text from a product label, extract any of the following fields you see as JSON. Fields:

| Field | Example | Description |
|-------|---------|-------------|
| `package_label` | "Product-0001" | A product label number. |
| `batch_number` | "Batch-0001" | A batch number for the product. |
| `product_name` | "Blue Rhino Pre-Roll" | The name of the product. |
| `strain_name` | "Blue Rhino" | The strain name of the product. |
| `product_type` | "flower" | The type of the product. |
| `total_cannabinoids` | 14.20 | The analytical total of all cannabinoids measured. |
| `total_thc` | 14.00 | The analytical total of THC and THCA. |
| `total_cbd` | 0.20 | The analytical total of CBD and CBDA. |
| `total_terpenes` | 0.42 | The sum of all terpenes measured. |
| `product_size` | 2000 | The size of the product in milligrams. |
| `serving_size` | 1000 | An estimated serving size in milligrams. |
| `servings_per_package` | 2 | The number of servings per package. |
| `price` | $30 | The price of the product. |
| `retailer` | "BudHouse" | The name of the retailer. |
| `retailer_license_number` | "C11-0000001-LIC" | The license number of the retailer. |
| `producer` | "Grow House" | The producer of the product. |
| `producer_license_number` | "L2Calc" | The producer's license number. |
| `date_produced` | 2022-04-20T12:20 | An ISO-formatted time when the product was produced. |
| `{analyte}` | {"thcv": 0.20} | The percent of any listed cannabinoid or terpene in `snake_case`. |
"""


class DataParser(object):
    """A cannabis data parser, powered by OpenAI."""

    def __init__(
            self,
            default_config: Optional[str] = '--oem 3 --psm 6',
            openai_api_key: Optional[str] = None,
            model: Optional[str] = 'gpt-4',
            instructions: Optional[str] = INSTRUCTIONAL_PROMPT,
            max_tokens: Optional[int] = MAX_PROMPT_LENGTH,
        ) -> None:
        """Initialize a data parser client.
        Args:
            default_config: The default configuration for OpenCV.
            openai_api_key: The OpenAI API key.
            model: The OpenAI model to use, 'gpt-4-0314' by default.
            base_prompt: The base prompt to use for the OpenAI model.
        """
        # Parameters.
        self.default_config = default_config
        self.openai_api_key = openai_api_key
        self.model = model
        self.instructions = instructions
        self.max_tokens = max_tokens

        # State.
        self.total_cost = 0
        self.img = None
        self.image_text = ''
        self.extracted_data = None

    def parse(
            self,
            doc: str,
            extraction_prompt: str,
            instructional_prompt: Optional[str] = None,
            model: Optional[str] = 'gpt-4',
            max_tokens: Optional[int] = None,
            temperature: Optional[float] = 0.0,
            verbose: Optional[bool] = False,
            user: Optional[str] = 'cannlytics',
        ) -> dict:
        """Parse data from a document with OpenAI's GPT model and
        return the data as JSON."""
        # Initialize parameters.
        if max_tokens is None:
            max_tokens = self.max_tokens

        # Get the text of a receipt.
        text = self.image_to_text(doc)

        # Begin the observation with the hash of the text.
        obs = {}
        obs['hash'] = create_hash(text, private_key='')

        # Initialize OpenAI.
        client = OpenAI()
        if model is None:
            model = self.model

        # Format the prompt.
        metadata_prompt = 'Text: ' + text + '\n\nJSON:'
        if instructional_prompt is None:
            instructional_prompt = 'Return JSON.'
        messages = [
            {'role': 'system', 'content': extraction_prompt},
            {'role': 'system', 'content': instructional_prompt},
            {'role': 'user', 'content': metadata_prompt},
        ]
        temperature = 0.0
        user = 'cannlytics'
        max_tokens = 4_096
        if verbose:
            print('MESSAGES:', messages)

        # Prompt AI to extract data as JSON.
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            user=user,
        )
        if verbose:
            print(completion.choices[0].message)
        usage = completion.model_dump()['usage']
        cost = 0.01 / 1_000 * usage['prompt_tokens'] + 0.03 / 1_000 * usage['completion_tokens']
        content = completion.choices[0].message.content
        extracted_json = content.lstrip('```json\n').rstrip('\n```')
        extracted_data = json.loads(extracted_json)
        obs = {**obs, **extracted_data}

        # Mint the observation with unique IDs.
        obs['parsed_at'] = datetime.now().isoformat()
        obs['warning'] = AI_WARNING
        obs['id'] = create_hash(obs, private_key='')
        self.total_cost += cost
        return obs
    
    def parse_with_vision(
            self,
            doc: str,
            extraction_prompt: str,
            instructional_prompt: Optional[str] = None,
            model: Optional[str] = 'gpt-4-vision-preview',
            detail: Optional[str] = 'high',
            max_tokens: Optional[int] = 4_000,
            verbose: Optional[bool] = False,
        ) -> dict:
        """Parse data from a document with OpenAI's GPT vision model."""

        # Format the prompt.
        extraction_prompt = EXTRACT_LABEL_DATA_PROMPT
        instructional_prompt = 'Return any fields from the product label image as JSON.'
        base64_image = self.encode_image(doc)

        # Proactively rotate the image to be readable.
        img = self.rotate(cv2.imread(str(doc), cv2.IMREAD_COLOR))

        # TODO: Upload image to Firebase Storage and get a download URL.
        

        # Make request to GPT-4 Vision.
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': extraction_prompt},
                    {'type': 'text', 'text': instructional_prompt},
                    {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{base64_image}',
                        'detail': detail,
                    },
                    },
                ],
                }
            ],
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        if verbose:
            print(content)
        extracted_json = content.lstrip('```json\n').split('\n```')[0]
        clean_json = '\n'.join([line.split('//')[0].rstrip() for line in extracted_json.split('\n')])
        obs = json.loads(clean_json)
        usage = response.usage
        cost = 0.01 / 1_000 * usage.prompt_tokens + 0.03 / 1_000 * usage.completion_tokens
        if verbose:
            print('Cost:', cost)
        obs['parsed_at'] = datetime.now().isoformat()
        obs['warning'] = AI_WARNING
        obs['id'] = create_hash(obs, private_key='')
        self.total_cost += cost
        return obs

    def image_to_pdf_to_text(self, image_file: str) -> str:
        """Extract the text from an image by converting it to a PDF.
        Args:
            image_file: The path to the image file.
        """
        img = self.rotate(cv2.imread(str(image_file), cv2.IMREAD_COLOR))
        pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
        pdf_file = image_file.replace('.jpg', '.pdf')
        with open(pdf_file, 'w+b') as f:
            f.write(pdf)
            f.close()
        report = pdfplumber.open(pdf_file)
        text = ''
        for page in report.pages:
            text += page.extract_text()
        return text

    def image_to_text(
            self,
            image_file: str,
            median_blur: Optional[int] = 0
        ) -> str:
        """Extract the text from an image.
        Args:
            image_file: The path to the image file.
            median_blur: Removes noise. Must be a positive odd integer.
        """
        img = self.rotate(cv2.imread(str(image_file), cv2.IMREAD_COLOR))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if median_blur: img = cv2.medianBlur(img, median_blur)
        text = pytesseract.image_to_string(img, config=self.default_config)
        return text

    def rotate(self, image, center=None, scale=1.0):
        """Rotate an image with text into a readable position, as well as possible.
        Credit: Mousam Singh <https://stackoverflow.com/a/55122911/5021266>
        License: CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>
        """
        (h, w) = image.shape[:2]
        if center is None:
            center = (w / 2, h / 2)
        degrees = int(re.search(
            '(?<=Rotate: )\d+',
            pytesseract.image_to_osd(image),
        ).group(0))
        angle = 360 - degrees
        M = cv2.getRotationMatrix2D(center, angle, scale)
        rotated = cv2.warpAffine(image, M, (w, h))
        return rotated
    
    def encode_image(self, image_path):
        """Encode an image as a base64 string."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def save(self, obs, filename):
        """Save extracted data to a file."""
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
        
    def quit(self):
        """Reset the parser and perform garbage cleaning."""
        self.model = 'gpt-4'
        self.openai_api_key = None
        self.total_cost = 0
        self.img = None
        self.image_text = ''
        self.extracted_data = None
        gc.collect()


# === Tests ===
if __name__ == "__main__":

    # Initialize OpenAI.
    from dotenv import dotenv_values
    import os
    config = dotenv_values('../../../.env')
    os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']

    # Initialize a data parser.
    parser = DataParser(
        model='gpt-4-1106-preview',
    )

    # [✓] TEST: Parse a label with OCR + AI.
    doc = '../../../.datasets/products/product-photos-2022/PXL_20220221_164104503.jpg'
    data = parser.parse(
        doc=doc,
        extraction_prompt=EXTRACT_LABEL_DATA_PROMPT,
        verbose=True,
    )
    print('Extracted:', data)
    print('Cost:', parser.total_cost)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    outfile = f'../../../.datasets/products/tests/label-1-{timestamp}.xlsx'
    parser.save(data, outfile)
    print('Saved:', outfile)

    # [✓] TEST: Parse a label image directly with GPT-4 vision.
    doc = '../../../.datasets/products/product-photos-2022/PXL_20211011_171904976.jpg'
    data = parser.parse_with_vision(
        doc=doc,
        extraction_prompt=EXTRACT_LABEL_DATA_PROMPT,
        verbose=True,
    )
    print('Extracted:', data)
    print('Cost:', parser.total_cost)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    outfile = f'../../../.datasets/products/tests/label-2-{timestamp}.xlsx'
    parser.save(data, outfile)
    print('Saved:', outfile)

    # Parse a directory of product labels.
    from cannlytics.data.tools import scan_qr_code
    from cannlytics.data.coas import CoADoc

    all_data = []
    product_label_dir = '../../../.datasets/products/product-photos-2022'
    product_label_files = os.listdir(product_label_dir)
    coa_parser = CoADoc()
    for file in product_label_files:
        obs = {}
        doc = os.path.join(product_label_dir, file)

        # Scan any QR codes.
        obs['qr_code'] = scan_qr_code(doc)
        print('QR code:', obs['qr_code'])

        # Parse with OCR + AI.
        obs['text'] = parser.image_to_text(doc)
        obs['ocr_data'] = parser.parse(
            doc=doc,
            extraction_prompt=EXTRACT_LABEL_DATA_PROMPT,
            verbose=True,
        )

        # Parse with AI vision.
        obs['data'] = parser.parse_with_vision(
            doc=doc,
            extraction_prompt=EXTRACT_LABEL_DATA_PROMPT,
            verbose=True,
        )
        all_data.append(obs)

        # Compare the label THC to the THC on the COA.
        if obs['qr_code']:
            coa_data = coa_parser.parse(obs['qr_code'])
            print('Label THC:', obs['total_thc'])
            print('COA THC:', coa_data['total_thc'])
