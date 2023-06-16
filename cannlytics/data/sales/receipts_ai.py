"""
BudSpender | Cannabis Receipt Parser
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/24/2023
Updated: 6/15/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json
import gc
import re
from typing import List, Optional

# External imports:
from cannlytics import __version__
from cannlytics.ai import (
    AI_WARNING,
    INSTRUCTIONAL_PROMPT,
    MAX_PROMPT_LENGTH,
    gpt_to_json,
)
from cannlytics.data import create_hash
import cv2
import pandas as pd
import pdfplumber
import pytesseract
# from pydantic import BaseModel


# Prompt to parse data from a cannabis receipt.
RECEIPTS_PROMPT = """Given text, extract JSON, where:

| `date_sold` | "2020-04-20" | The date the receipt was sold. |
| `invoice_number` | "123456789" | The receipt number. |
| `product_names` | ["Blue Rhino Pre-Roll"] | The names of the product purchased. |
| `product_types` | ["flower"] | The types of the products purchased. |
| `product_quantities` | [1] | The quantities of the products purchased. |
| `product_prices` | [5.0] | The prices of the products purchased. |
| `product_ids` | ["5f8b9c4b0f5c4b0008d1b2b0"] | The IDs of the products purchased. |
| `total_amount` | 5.0 | The total amount of all product prices. |
| `subtotal` | 5.0 | The subtotal of the receipt. |
| `total_discount` | 0.0 | The amount of discount applied to the transaction, if applicable. |
| `total_paid` | 5.0 | The total amount paid. |
| `change_due` | 0.0 | The amount of change due. |
| `rewards_earned` | 0.0 | The amount of rewards earned. |
| `rewards_spent` | 0.0 | The amount of rewards spent. |
| `total_rewards` | 0.0 | The total amount of rewards. |
| `city_tax` | 0.0 | The amount of city tax applied to the transaction, if applicable. |
| `county_tax` | 0.0 | The amount of county tax applied to the transaction, if applicable. |
| `state_tax` | 0.0 | The amount of state tax applied to the transaction, if applicable. |
| `excise_tax` | 0.0 | The amount of excise tax applied to the transaction, if applicable. |
| `retailer` | "BudHouse" | The name of the retailer. |
| `retailer_license_number` | "C11-0000001-LIC" | The license number of the retailer. |
| `retailer_address` | "1234 Main St, San Diego, CA 92101" | The address of the retailer. |
| `budtender` | "John Doe" | The name of the budtender. |
"""


# # TODO: Use OpenAI's new function calling to request JSON for a sales receipt.
# class SalesReceipt(BaseModel):
#     archived_date: Optional[str] = None
#     caregiver_license_number: Optional[str] = None
#     city_tax: Optional[float] = None
#     county_tax: Optional[float] = None
#     discount_amount: Optional[float] = None
#     excise_tax: Optional[float] = None
#     id: Optional[int] = None
#     identification_method: Optional[str] = None
#     invoice_number: Optional[str] = None
#     is_final: Optional[bool] = None
#     last_modified: Optional[str] = None
#     municipal_tax: Optional[float] = None
#     patient_license_number: Optional[str] = None
#     patient_registration_location_id: Optional[str] = None
#     package_label: Optional[str] = None
#     price: Optional[float] = None
#     quantity: Optional[float] = None
#     receipt_number: Optional[str] = None
#     recorded_by_user_name: Optional[str] = None
#     recorded_date_time: Optional[str] = None
#     sales_customer_type: Optional[str] = None
#     sales_date: Optional[str] = None
#     sales_date_time: Optional[str] = None
#     sales_tax: Optional[float] = None
#     sub_total: Optional[float] = None
#     total_amount: Optional[float] = None
#     total_packages: Optional[int] = None
#     total_price: Optional[float] = None
#     total_transactions: Optional[int] = None
#     transactions: Optional[List] = None
#     unit_of_measure: Optional[str] = None
#     unit_thc_content: Optional[float] = None
#     unit_thc_content_unit_of_measure: Optional[str] = None
#     unit_thc_percent: Optional[float] = None
#     unit_weight: Optional[float] = None
#     unit_weight_unit_of_measure: Optional[str] = None


# def json_to_receipt(json: dict) -> SalesReceipt:
#     """Convert a JSON object to a SalesReceipt."""
#     return SalesReceipt(**json)


class ReceiptsParser(object):
    """A cannabis receipt parser, powered by OpenAI."""

    def __init__(
            self,
            default_config: Optional[str] = '--oem 3 --psm 6',
            openai_api_key: Optional[str] = None,
            model: Optional[str] = 'gpt-4',
        ) -> None:
        """Initialize an Open Data API client.
        """
        # Parameters.
        self.default_config = default_config
        self.openai_api_key = openai_api_key
        self.model = model

        # State.
        self.total_cost = 0
        self.img = None
        self.image_text = ''
        self.extracted_data = None
    
    def image_to_pdf_to_text(self, image_file):
        """Extract the text from an image by converting to to a PDF,
        rotating it as necessary."""
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
    
    def image_to_text(self, image_file):
        """Extract the text from an image."""
        # img = cv2.imread(image_path)
        img = self.rotate(cv2.imread(str(image_file), cv2.IMREAD_COLOR))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # img = cv2.medianBlur(img, 5)
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
    
    def parse(
            self,
            doc: str,
            openai_api_key: Optional[str] = None,
            model: Optional[str] = 'gpt-4',
            max_tokens: Optional[int] = MAX_PROMPT_LENGTH,
            temperature: Optional[float] = 0.0,
            system_prompts: Optional[List[str]] = None,
            verbose: Optional[bool] = False,
            user: Optional[str] = 'cannlytics',
            retry_pause: Optional[float] = 3.33,
        ) -> dict:
        """Parse a receipt with OpenAI's GPT model and return the data as JSON."""  

        # Get the text of a receipt.
        text = parser.image_to_text(doc)

        # Begin the observation with the hash of the text.
        obs = {}
        obs['hash'] = create_hash(text, private_key='')

        # Format the system prompts.
        if not system_prompts:
            system_prompts = [
                INSTRUCTIONAL_PROMPT,
                RECEIPTS_PROMPT
            ]

        # Initialize OpenAI.
        if openai_api_key is None:
            openai_api_key = self.openai_api_key
        if model is None:
            model = self.model

        # Parse the receipt.
        extracted_data, cost = gpt_to_json(
            text,
            system_prompts=system_prompts,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            user=user,
            openai_api_key=openai_api_key,
            verbose=verbose,
            retry_pause=retry_pause,
        )
        obs = {**obs, **extracted_data}

        # Calculate total price.
        prices = obs.get('product_prices', [])
        obs['total_price'] = 0
        for price in prices:
            try:
                obs['total_price'] += float(price)
            except:
                pass

        # Calculate total tax.
        obs['total_tax'] = 0
        tax_keys = [key for key in obs.keys() if '_tax' in key]
        for key in tax_keys:
            try:
                obs['total_tax'] += float(obs[key])
            except:
                pass

        # Calculate total transactions.
        obs['total_transactions'] = len(prices)

        # Future work: Augment retailer data.

        # Future work: Augment product data with product ID.

        # Future work: Save a copy of the image to Firebase Storage.

        # Mint the observation with unique IDs.
        obs['algorithm'] = 'receipts_ai.py'
        obs['algorithm_entry_point'] = 'parse_receipt_with_ai'
        obs['algorithm_version'] = __version__
        obs['parsed_at'] = datetime.now().isoformat()
        obs['warning'] = AI_WARNING
        return obs, cost
    
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
if __name__ == '__main__':

    # Initialize a receipt parser.

    # Initialize OpenAI.
    from dotenv import dotenv_values
    config = dotenv_values('../../../.env')
    openai_api_key = config['OPENAI_API_KEY']

    # Initialize a receipt parser.
    parser = ReceiptsParser(
        model='gpt-4',
        openai_api_key=openai_api_key,
    )

    # [✓] TEST: Parse a receipt.
    image_file = '../../../.datasets/receipts/tests/receipt-1.jpg'
    outfile = '../../../.datasets/receipts/tests/receipt-1.xlsx'
    receipt_data, cost = parser.parse(image_file)
    parser.save(receipt_data, outfile)

    # # [ ] TEST: Parse a folder of receipts.
    # RECEIPT_DIR = '../../../.datasets/receipts/tests/'
    # all_receipt_data = []
    # file_types = ['.jpg', '.png', '.jpeg']
    # filenames = os.listdir(RECEIPT_DIR)
    # for filename in filenames:
    #     if any(filename.endswith(file_type) for file_type in file_types):
    #         image_file = os.path.join(RECEIPT_DIR, filename)
    #         receipt_data = parser.parse(image_file)
    #         all_receipt_data.append(receipt_data)
