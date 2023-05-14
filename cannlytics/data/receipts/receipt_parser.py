"""
BudSpender | Receipt Parser
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/24/2023
Updated: 5/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import re
from typing import List, Optional

# External imports:
import cv2
import pdfplumber
import pytesseract
import numpy as np
from pydantic import BaseModel


class SalesReceipt(BaseModel):
    archived_date: Optional[str] = None
    caregiver_license_number: Optional[str] = None
    city_tax: Optional[float] = None
    county_tax: Optional[float] = None
    discount_amount: Optional[float] = None
    excise_tax: Optional[float] = None
    id: Optional[int] = None
    identification_method: Optional[str] = None
    invoice_number: Optional[str] = None
    is_final: Optional[bool] = None
    last_modified: Optional[str] = None
    municipal_tax: Optional[float] = None
    patient_license_number: Optional[str] = None
    patient_registration_location_id: Optional[str] = None
    package_label: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    receipt_number: Optional[str] = None
    recorded_by_user_name: Optional[str] = None
    recorded_date_time: Optional[str] = None
    sales_customer_type: Optional[str] = None
    sales_date: Optional[str] = None
    sales_date_time: Optional[str] = None
    sales_tax: Optional[float] = None
    sub_total: Optional[float] = None
    total_amount: Optional[float] = None
    total_packages: Optional[int] = None
    total_price: Optional[float] = None
    total_transactions: Optional[int] = None
    transactions: Optional[List] = None
    unit_of_measure: Optional[str] = None
    unit_thc_content: Optional[float] = None
    unit_thc_content_unit_of_measure: Optional[str] = None
    unit_thc_percent: Optional[float] = None
    unit_weight: Optional[float] = None
    unit_weight_unit_of_measure: Optional[str] = None


class BudSpender(object):
    """A cannabis receipt parser."""

    def __init__(self) -> None:
        """Initialize an Open Data API client.
        """
        self.default_config = '--oem 3 --psm 6'
    
    def image_to_text(self, image_file):
        """Extract the text from an image by converting to to a PDF,
        rotating it as necessary."""
        image_data = self.rotate(cv2.imread(str(image_file), cv2.IMREAD_COLOR))
        pdf = pytesseract.image_to_pdf_or_hocr(image_data, extension='pdf')
        pdf_file = image_file.replace('.jpg', '.pdf')
        with open(pdf_file, 'w+b') as f:
            f.write(pdf)
            f.close()
        receipt = pdfplumber.open(pdf_file)
        text = ''
        for page in receipt.pages:
            text += page.extract_text()
        return text
    
    def process_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        text = pytesseract.image_to_string(img, config=self.default_config)
        return text

    def rotate(image, center=None, scale=1.0):
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
    
    # TODO:
    def parse(self, text):
        """Extract data from a cannabis receipt."""
        # extract product name, quantity, price, taxes, and discounts using regular expressions
        pattern = r'(\d+)\s+(\w+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)'
        matches = re.findall(pattern, text)
        products = []
        for match in matches:
            product = {
                'name': match[1],
                'quantity': int(match[0]),
                'price': float(match[2]),
                'taxes': float(match[3]),
                'discounts': float(match[4])
            }
            products.append(product)
        return products

# === Test ===
if __name__ == '__main__':

    import os

    # Initialize a receipt parser.
    parser = BudSpender()

    # Specify where your receipts live.
    RECEIPT_DIR = '../../.datasets/receipts'
    receipt_filenames = []
    filenames = os.listdir(RECEIPT_DIR)
    for filename in filenames:
        if filename.endswith('.jpg'):
            receipt_filenames.append(f'{RECEIPT_DIR}/{filename}')

    # Example: Extract the text from a receipt.
    image_file = '../../.datasets/receipts/receipt-1.jpg'
    image_text = parser.image_to_text(image_file)

    # Example: Extract the text from all receipts.
    receipt_texts = []
    for filename in receipt_filenames:
        image_text = parser.image_to_text(filename)
        receipt_texts.append(image_text)

    # Save the receipt text.
    with open('receipt_texts.txt', 'w+') as f:
        for s in receipt_texts:
            f.write(str(s) + '\n')

    # Use a pre-trained model to tokenize the receipts.

