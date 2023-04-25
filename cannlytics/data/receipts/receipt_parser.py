"""
Receipt Parser
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/24/2023
Updated: 4/24/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import re
from typing import List, Optional

# External imports:
import cv2
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


class ReceiptParser(object):
    """A cannabis receipt parser."""

    def __init__(self) -> None:
        """Initialize an Open Data API client.
        """
        self.default_config = '--oem 3 --psm 6'
    
    def process_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        text = pytesseract.image_to_string(img, config=self.default_config)
        return text
    
    def parse_receipt(self, text):
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
