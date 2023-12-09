"""
Get California Cannabis Lab Results | Flower Company
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 12/8/2023
Updated: 12/8/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive cannabis lab result data published by the Flower Company.

Data Source:

    * [Flower Company](https://flowercompany.com/)

Data points:

    - producer
    - product_name
    - product_url
    - total_thc
    - price
    - discount_price
    - amount
    - indica_percentage
    - sativa_percentage
    - image_url
    - product_type
    - product_subtype
    - product_description
    - predicted_effects
    - predicted_aromas
    - lineage
    - distributor
    - distributor_license_number

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep

# External imports:
from cannlytics.data import create_sample_id
from cannlytics.data.coas.coas import CoADoc
import pandas as pd
import requests

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select


# Define the base URL.
base_url = 'https://flowercompany.com/category/'

# Define the categories.
categories = [
    'fire-flower',
    'cartridges',
    'concentrates',
    'edibles',
    'prerolls',
    'top-shelf-nugs',
    'just-weed',
    'wellness',
    # 'the-freshest',
    # 'staff-picks',
    # 'latest-drops',
]

# Define the indica/sativa types.
indica_percentages = {
    'Indica': 1,
    'I-Hybrid': 0.75,
    'Hybrid': 0.5,
    'S-Hybrid': 0.25,
    'Sativa': 0,
}


def extract_weight(amount_str):
    """Extracts the numerical weight in grams from the amount string."""
    if amount_str:
        parts = amount_str.split('(')
        if len(parts) > 1:
            weight = parts[1].split('g')[0].strip()
            return float(weight)
    return None


def price_to_float(price_str):
    """Converts a price string to a float."""
    return float(price_str.replace('$', ''))


# Initialize Selenium.
try:
    service = Service()
    options = Options()
    options.add_argument('--window-size=1920,1200')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options, service=service)
except:
    options = EdgeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Edge(options=options)

# Open each category page.
products = []
for category in categories:
    page_url = base_url + category
    driver.get(page_url)

    # Click "Yes" button.
    try:
        yes_button = driver.find_element(By.CLASS_NAME, 'age-gate-yes-button')
        yes_button.click()
        sleep(2)
    except Exception as e:
        pass

    # Click "Show More" until the button is not found.
    while True:
        try:
            # Find the "Show More" button and click it
            more_button = driver.find_element(By.CLASS_NAME, 'show-more-button')
            more_button.click()
            sleep(2)
        except:
            break

    # Get all of the cards.
    cards = driver.find_elements(by=By.CLASS_NAME, value='product-card-wrapper')
    for card in cards:

        # Find the product details.
        producer = card.find_element(By.CSS_SELECTOR, '.favorite-company a').text.strip()
        product_name = card.find_element(By.CSS_SELECTOR, '.favorite-product-name a').text.strip()
        product_url = card.find_element(By.CSS_SELECTOR, '.favorite-product-name a').get_attribute('href')
        total_thc = card.find_element(By.CSS_SELECTOR, '.product-card-thc').text.strip()

        # Find the price and discount.
        discount = 0
        discount_price = card.find_element(By.CSS_SELECTOR, '.price.product-card-price-actual').text.strip()
        price = card.find_element(By.CSS_SELECTOR, '.price.retail.product-card-price-retail').text.strip()

        # Find the amount.
        try:
            amount = card.find_element(By.CSS_SELECTOR, '.solo-variant-toggle').text.strip()
        except:
            select_element = card.find_element(By.CSS_SELECTOR, 'select.new-product-card-variant-select')
            select_object = Select(select_element)
            amount_options = [option.text.strip() for option in select_object.options]
            amount = amount_options[0] if amount_options else None

        # Find the strain type.
        strain_type = card.text.split('\n')[0]
        indica_percentage = indica_percentages.get(strain_type, 0)
        sativa_percentage = 1 - indica_percentage
        
        # Clean the data.
        try:
            total_thc = float(total_thc.replace('% THC', '').strip())
            price = price_to_float(price)
            discount_price = price_to_float(discount_price)
            discount = price - discount_price
        except:
            pass

        # Add the product to the list.
        products.append({
            'product_name': product_name,
            'category': category,
            'producer': producer,
            'total_thc': total_thc,
            'price': price,
            'discount_price': discount_price,
            'discount': discount,
            'amount': extract_weight(amount),
            'indica_percentage': indica_percentage,
            'sativa_percentage': sativa_percentage,
            'product_url': product_url,
        })

# Get each product URL page to get each product's data and results.
data = []
for product in products:
    driver.get(product['product_url'])
    sleep(2)

    # Click "Yes" button.
    try:
        yes_button = driver.find_element(By.CLASS_NAME, 'age-gate-yes-button')
        yes_button.click()
        sleep(1)
    except Exception as e:
        pass

    # Get data for each product:
    try:
        types = driver.find_elements(By.CSS_SELECTOR, '.detail-product-type')
        if types:
            product_type = types[0].text.strip()
        if len(types) >= 2:
            product_subtype = types[1].text.strip()
        product_description = driver.find_element(By.CSS_SELECTOR, '.product-view-description').text.strip()
        effects = driver.find_elements(By.CSS_SELECTOR, '.row.product-view-row')[1].find_element(By.CSS_SELECTOR, '.badge-flower.detail-category-text').text.strip()
        aromas = driver.find_elements(By.CSS_SELECTOR, '.row.product-view-row')[2].find_element(By.CSS_SELECTOR, '.badge-flower.detail-category-text').text.strip()
        lineage = driver.find_elements(By.CSS_SELECTOR, '.row.product-view-row')[3].find_element(By.CSS_SELECTOR, '.badge-flower.detail-category-text').text.strip()
        distributor_elements = driver.find_elements(By.CSS_SELECTOR, '.row.d-block .detail-sub-text')
        distributor = distributor_elements[0].text.strip() if len(distributor_elements) > 0 else None
        distributor_license_number = distributor_elements[1].text.strip() if len(distributor_elements) > 1 else None
        image_url = driver.find_element(By.CSS_SELECTOR, '.product-image-lg').get_attribute('src')
        lab_results_element = driver.find_element(By.CSS_SELECTOR, '.row.product-view-row .text-brand')
        lab_results_url = lab_results_element.get_attribute('href')
        product_id = create_sample_id(
            private_key=str(product['total_thc']),
            public_key=product['product_name'],
            salt=product['producer'],
        )
        item = {
            'product_id': product_id,
            'lab_results_url': lab_results_url,
            'image_url': image_url,
            'product_type': product_type,
            'product_subtype': product_subtype,
            'product_description': product_description,
            'predicted_effects': effects,
            'predicted_aromas': aromas.split(', '),
            'lineage': lineage,
            'distributor': distributor,
            'distributor_license_number': distributor_license_number,
        }
        data.append({**product, **item})
    except Exception as e:
        print("Error in data extraction: ", e)

# Save the product data.
DATA_DIR = 'D:/data/california/lab_results'
category_dir = os.path.join(DATA_DIR, f'./datasets/flower-company')
if not os.path.exists(category_dir): os.makedirs(category_dir)
timestamp = datetime.now().strftime('%Y-%m-%d')
product_datafile = os.path.join(category_dir, f'ca-products-flower-company-{category}-{timestamp}.csv')
product_data = pd.DataFrame(data)
product_data.to_csv(product_datafile, index=False)
print(f'Saved {len(product_data)} products to: {product_datafile}')

# Download all of the COAs.
PDF_DIR = 'D:/data/california/lab_results/pdfs/flower-company'
for obs in data:
    pdf_response = requests.get(obs['lab_results_url'])
    pdf_file_path = os.path.join(PDF_DIR, obs['product_id'] + '.pdf')
    if os.path.exists(pdf_file_path):
        continue
    with open(pdf_file_path, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
        print(f'Downloaded PDF: {pdf_file_path}')
    sleep(0.33)


# === Parse COAs ===

# Read the download product items.
product_data = pd.read_csv(product_datafile)

# Parse the corresponding COAs.
all_results = []
parser = CoADoc()
for i, row in product_data.iterrows():
    pdf_file_path = os.path.join(PDF_DIR, row['product_id'] + '.pdf')
    if not os.path.exists(pdf_file_path):
        continue
    try:
        coa_data = parser.parse(pdf_file_path)
        all_results.append({**row.to_dict(), **coa_data[0]})
        print(f'Parsed COA: {pdf_file_path}')
    except Exception as e:
        print(f'Failed to parse COA: {pdf_file_path}')
        continue

# Save the parsed COA data to a file.
timestamp = datetime.now().strftime('%Y-%m-%d')
results_datafile = os.path.join(category_dir, f'ca-results-flower-company-{category}-{timestamp}.xlsx')
results = pd.DataFrame(all_results)
parser.save(results, results_datafile)
print(f'Saved parsed COA data to: {results_datafile}')
