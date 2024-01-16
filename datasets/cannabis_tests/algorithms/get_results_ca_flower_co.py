"""
Get California Cannabis Lab Results | Flower Company
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 12/8/2023
Updated: 12/9/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive cannabis lab result data published by the Flower Company.

Data Source:

    * [Flower Company](https://flowercompany.com/)

Data points:

    ✓ product_id (generated)
    ✓ producer
    ✓ product_name
    ✓ product_url
    ✓ total_thc
    ✓ total_thc_units
    ✓ total_cbd
    ✓ total_cbd_units
    ✓ price
    ✓ discount_price
    ✓ amount
    ✓ classification
    ✓ indica_percentage
    ✓ sativa_percentage
    ✓ image_url
    ✓ product_type
    ✓ product_subtype
    ✓ product_description
    ✓ predicted_effects
    ✓ predicted_aromas
    ✓ lineage
    ✓ distributor
    ✓ distributor_license_number
    ✓ lab_results_url
    ✓ results (augmented)

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
try:
    import chromedriver_binary  # Adds chromedriver binary to path.
except ImportError:
    pass # Otherwise, ChromeDriver should be in your path.


# Define the base URL.
base_url = 'https://flowercompany.com/'

# Define the categories.
brand_pages = []
category_pages = [
    'category/fire-flower',
    'category/cartridges',
    'category/concentrates',
    'category/edibles',
    'category/prerolls',
    'category/top-shelf-nugs',
    'category/just-weed',
    'category/wellness',
    'category/the-freshest',
    'category/staff-picks',
    'category/latest-drops',
]

# Define the indica/sativa types.
indica_percentages = {
    'Indica': 1,
    'I-Hybrid': 0.75,
    'Hybrid': 0.5,
    'S-Hybrid': 0.25,
    'Sativa': 0,
}

# Parameters.
verbose = True
headless = False


def initialize_driver(headless=False):
    """Initialize Selenium, using Chrome first and Edge if Chrome fails."""
    try:
        service = Service()
        options = Options()
        if headless:
            options.add_argument('--window-size=1920,1200')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
        return webdriver.Chrome(options=options, service=service)
    except:
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        return webdriver.Edge(options=options)


def click_yes_button(driver):
    """Click the "Yes" button."""
    try:
        yes_button = driver.find_element(By.CLASS_NAME, 'age-gate-yes-button')
        yes_button.click()
        sleep(2)
    except:
        pass


def click_show_more_button(driver):
    """Click "Show More" until the button is not found."""
    while True:
        try:
            # Find the "Show More" button and click it
            more_button = driver.find_element(By.CLASS_NAME, 'show-more-button')
            more_button.click()
            sleep(3)
        except:
            break


def save_product_data(items, data_dir, namespace='lab-results'):
    """Save the product data to a CSV file."""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    timestamp = datetime.now().strftime('%Y-%m-%d')
    datafile = os.path.join(data_dir, f'{namespace}-{timestamp}.csv')
    df = pd.DataFrame(items)
    df.to_csv(datafile, index=False)
    return datafile


def download_coa_pdfs(
        items,
        pdf_dir,
        url_key='lab_results_url',
        id_key='product_id',
        verbose=True,
        pause=0.33,
    ):
    """Download all of the COA PDFs."""
    for obs in items:
        url = obs[url_key]
        if not url:
            continue
        response = requests.get(url)
        filename = os.path.join(pdf_dir, obs[id_key] + '.pdf')
        if os.path.exists(filename):
            continue
        with open(filename, 'wb') as pdf_file:
            pdf_file.write(response.content)
            if verbose:
                print(f'Downloaded PDF: {filename}')
        sleep(pause)


def parse_coa_pdfs(parser, data, pdf_dir, id_key='product_id', verbose=True):
    """Parse corresponding COAs from a DataFrame in a PDF directory.
    The `id_key` is used to match the PDF filename to the DataFrame.
    """
    all_results = []
    for _, row in data.iterrows():
        pdf_file_path = os.path.join(pdf_dir, row[id_key] + '.pdf')
        if not os.path.exists(pdf_file_path):
            continue
        try:
            coa_data = parser.parse(pdf_file_path)
            all_results.append({**row.to_dict(), **coa_data[0]})
            if verbose:
                print(f'Parsed COA: {pdf_file_path}')
        except Exception as e:
            if verbose:
                print(f'Failed to parse COA: {pdf_file_path}')
            continue
    return pd.DataFrame(all_results)


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


# === Test ===
if __name__ == '__main__':

    # Define where the data lives.
    PDF_DIR = 'D:/data/california/lab_results/pdfs/flower-company'
    DATA_DIR = 'D:/data/california/lab_results/datasets/flower-company'

    # TODO: Turn the following into a re-usable function.
    # TODO: Implement logging.

    # Initialize the driver.
    driver = initialize_driver(headless=False)

    # Get all of the brand pages.
    driver.get(base_url + 'menu')
    try:
        yes_button = driver.find_element(By.CLASS_NAME, 'age-gate-yes-button')
        yes_button.click()
        sleep(2)
    except Exception as e:
        pass
    div = driver.find_element(By.CLASS_NAME, 'special-content-brand-row')
    links = div.find_elements(by=By.TAG_NAME, value='a')
    for link in links:
        brand_pages.append(link.get_attribute('href').replace(base_url, ''))

    # Open each brand/category page.
    products, recorded = [], []
    for page in brand_pages + category_pages:

        # Get the brand/category page.
        driver.get(base_url + page)

        # Click "Yes" button.
        click_yes_button(driver)

        # Click "Show More" until the button is not found.
        click_show_more_button(driver)

        # Get all of the cards.
        sleep(3)
        cards = driver.find_elements(by=By.CLASS_NAME, value='product-card-wrapper')
        if verbose:
            print(f'Found {len(cards)} products for page: {page}')

        # Get the data from each card.
        for card in cards:

            # Find the product details.
            producer = card.find_element(By.CSS_SELECTOR, '.favorite-company a').text.strip()
            product_name = card.find_element(By.CSS_SELECTOR, '.favorite-product-name a').text.strip()
            product_url = card.find_element(By.CSS_SELECTOR, '.favorite-product-name a').get_attribute('href')
            
            # Skip the product if it's already recorded.
            if product_url in recorded:
                continue
            recorded.append(product_url)

            # Get the total THC.
            # TODO: Get other totals.
            try:
                total_thc = card.find_element(By.CSS_SELECTOR, '.product-card-thc').text.strip()
            except:
                total_thc = ''

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
            classification = card.text.split('\n')[0]
            indica_percentage = indica_percentages.get(classification, 0.5)
            sativa_percentage = 1 - indica_percentage

            # Clean the data.
            try:
                total_thc_units = 'percent' if '%' in total_thc else 'mg'
                total_thc = float(total_thc.lower().replace('% thc', '').replace('mg thc', '').strip())
                price = price_to_float(price)
                discount_price = price_to_float(discount_price)
                discount = price - discount_price
            except:
                pass

            # Add the product to the list.
            products.append({
                'product_name': product_name,
                'category': page.split('/')[-1],
                'producer': producer,
                'total_thc': total_thc,
                'total_thc_units': total_thc_units,
                'price': price,
                'discount_price': discount_price,
                'discount': discount,
                'amount': extract_weight(amount),
                'classification': classification,
                'indica_percentage': indica_percentage,
                'sativa_percentage': sativa_percentage,
                'product_url': product_url,
            })

    # Get each product URL page to get each product's data and results.
    data = []
    for product in products:
        if verbose:
            print(f'Getting data for: {product["product_url"]}')
        driver.get(product['product_url'])
        sleep(3)

        # Click "Yes" button.
        click_yes_button(driver)

        # Get data for each product:
        types = driver.find_elements(By.CSS_SELECTOR, '.detail-product-type')
        if types:
            product_type = types[0].text.strip()
        if len(types) >= 2:
            product_subtype = types[1].text.strip()
        else:
            product_subtype = None
        product_description = driver.find_element(By.CSS_SELECTOR, '.product-view-description').text.strip()

        # Skip accessories.
        if product_type == 'Accessory':
            continue

        # Get the effects, aromas, lineage, and lab results URL.
        info_rows = driver.find_elements(By.CSS_SELECTOR, '.row.product-view-row')
        effects, aromas, lineage, lab_results_url = '', '', '', ''
        for row in info_rows:
            parts = row.text.split('\n')
            field = parts[0].lower()
            if 'effects' in field:
                effects = parts[-1]
            elif 'aromas' in field:
                aromas = parts[-1]
            elif 'lineage' in field:
                lineage = parts[-1]
            elif 'tested' in field:
                try:
                    el = row.find_element(By.TAG_NAME, 'a')
                    lab_results_url = el.get_attribute('href')
                except:
                    pass

        # Get the distributor.
        els = driver.find_elements(By.CSS_SELECTOR, '.row.d-block .detail-sub-text')
        distributor = els[-2].text.strip() if len(els) > 1 else None
        distributor_license_number = els[-1].text.strip() if len(els) > 1 else None
        
        # Get the image URL.
        image_url = driver.find_element(By.CSS_SELECTOR, '.product-image-lg').get_attribute('src')

        # Get product name and producer, if missing.
        if not product['product_name']:
            product['product_name'] = driver.find_element(By.CSS_SELECTOR, '.product-view-name').text
            product['producer'] = driver.find_element(By.CSS_SELECTOR, '.product-view-brand').text
        
        # Get prices and amounts, if missing.
        if not product['price']:
            price_element = driver.find_element(By.ID, 'variant-price-retail')
            driver.execute_script("arguments[0].scrollIntoView(true);", price_element)
            sleep(0.2)
            price = price_element.text
            discount_price = driver.find_element(By.ID, 'variant-price').text
            amount = driver.find_element(By.CSS_SELECTOR, '.variant-toggle').text
            product['amount'] = extract_weight(amount)
            product['price'] = price_to_float(price)
            product['discount_price'] = price_to_float(discount_price)
            product['discount'] = product['price'] - product['discount_price']

        # Get compounds, if missing.
        if not product.get('total_thc'):
            try:
                total_thc = driver.find_element(By.CSS_SELECTOR, '.product-card-thc').text
                product['total_thc'] = float(total_thc.lower().replace('% thc', '').replace('mg thc', '').strip())
                product['total_thc_units'] = 'percent' if '%' in total_thc else 'mg'
            except:
                pass
        if not product.get('total_cbd'):
            try:
                total_cbd = driver.find_element(By.CSS_SELECTOR, '.product-card-cbd').text
                product['total_cbd'] = float(total_cbd.lower().replace('% cbd', '').replace('mg cbd', '').strip())
                product['total_cbd_units'] = 'percent' if '%' in total_cbd else 'mg'
            except:
                product['total_cbd'] = None

        # Get classification, if missing.
        if not product['classification']:
            el = driver.find_element(By.CSS_SELECTOR, '.product-detail-type-container')
            product['classification'] = el.text.split('\n')[0]
            product['indica_percentage'] = indica_percentages.get(product['classification'], 0.5)
            product['sativa_percentage'] = 1 - indica_percentage
        
        # Create a product ID.
        product_id = create_sample_id(
            private_key=str(product['total_thc']),
            public_key=product['product_name'],
            salt=product['producer'],
        )

        # Record the product item details.
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

    # Close the browser.
    driver.close()

    # Save the product data.
    datafile = save_product_data(data, DATA_DIR, namespace='ca-products-flower-company')
    if verbose:
        print(f'Saved {len(data)} products to: {datafile}')

    # Download all of the COAs.
    download_coa_pdfs(data, pdf_dir=PDF_DIR, verbose=verbose)


    # === Parse COAs ===

    # Read the download product items.
    product_data = pd.read_csv(datafile)

    # Parse the corresponding COAs.
    parser = CoADoc()
    results = parse_coa_pdfs(
        parser=parser,
        data=product_data,
        pdf_dir=PDF_DIR,
        verbose=verbose,
    )

    # Save the parsed COA data to a file.
    timestamp = datetime.now().strftime('%Y-%m-%d')
    results_datafile = os.path.join(DATA_DIR, f'ca-results-flower-company-{timestamp}.xlsx')
    parser.save(results, results_datafile)
    print(f'Saved {len(results)} parsed COAs to: {results_datafile}')
