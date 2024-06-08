"""
Get Florida cannabis lab results | Flowery
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 4/28/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis lab result data for the Flowery.

Data Sources:

    - [The Flowery](https://support.theflowery.co)

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep

# External imports:
from cannlytics.data.web import initialize_selenium
from cannlytics.utils.constants import DEFAULT_HEADERS
import pandas as pd
import requests

# Selenium imports.
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def get_results_the_flowery(
        data_dir: str,
        slug = 'the-flowery',
        producer_license_number = 'MMTC-2019-0020',
        lists_url = 'https://support.theflowery.co/hc/en-us/sections/7240468576283-Drop-Information',
        overwrite = False,
    ):
    """Get lab results published by The Flowery on the public web."""

    # Initialize the web driver.
    driver = initialize_selenium()

    # Load the lists page to get each list of COAs.
    coa_lists = []
    driver.get(lists_url)
    links = driver.find_elements(by=By.TAG_NAME, value='a')
    for link in links:
        if 'COAs' in link.text:
            coa_lists.append(link.get_attribute('href'))

    # Get COA URLs.
    coa_urls = []
    for coa_list in coa_lists:
        driver = initialize_selenium()
        driver.get(coa_list)
        links = driver.find_elements(by=By.TAG_NAME, value='a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.endswith('.pdf'):
                coa_urls.append(href)
        driver.close()
        driver.quit()

    # Close the browser.
    driver.close()
    driver.quit()

    # Create an output directory.
    datasets_dir = os.path.join(data_dir, '.datasets')
    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir)

    # Save the COA URLs.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    df = pd.DataFrame(coa_urls)
    df.to_excel(f'{datasets_dir}/fl-lab-result-urls-{slug}-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for %s' % (len(df), slug))

    # Create a directory for COA PDFs.
    pdf_dir = os.path.join(datasets_dir, 'pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Create a directory for each licensees COAs.
    license_pdf_dir = os.path.join(pdf_dir, producer_license_number)
    if not os.path.exists(license_pdf_dir):
        os.makedirs(license_pdf_dir)

    # Download the COA PDFs.
    for coa_url in coa_urls:
        sample_id = coa_url.split('/')[-1].split('.')[0]
        batch_id = coa_url.split('/')[-2]
        outfile = os.path.join(license_pdf_dir, f'{batch_id}-{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            continue
        sleep(0.3)
        response = requests.get(coa_url, headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        print('Downloaded: %s' % outfile)

    # TODO: Save details about each COA, including The Flowery company data.

    # Return the COA URLs.
    return df


def get_product_results_the_flowery(
        data_dir: str,
        overwrite = False,
        **kwargs,
    ):
    """Get product results from The Flowery website."""
    # Initialize a web driver.
    driver = initialize_selenium()

    # Iterate over all of the product types.
    observations = []
    categories = ['Flower', 'Concentrates', 'Pre-Rolls', 'Vaporizers', 'Tinctures']
    for category in categories:

        # Load the category page.
        url = f'https://theflowery.co/shop?categories[]={category}'
        driver.get(url)
        sleep(3.33)

        # Get all of the product cards.
        divs = driver.find_elements(by=By.CSS_SELECTOR, value='a.s-shop-product-card')
        for div in divs:
            
            # Extract product name.
            product_name = div.find_element(by=By.CLASS_NAME, value='title').text

            # Extract product image URL.
            product_image = div.find_element(by=By.TAG_NAME, value='img').get_attribute('src')

            # Extract product price.
            product_price = float(div.find_element(by=By.CLASS_NAME, value='full-price').text.strip('$'))

            # Extract strain type.
            strain_type = div.find_element(by=By.CLASS_NAME, value='sort').text

            # Extract product URL (assuming the URL is stored in the href attribute of a link)
            product_url = div.get_attribute('href')

            # Store the extracted data in a dictionary
            obs = {
                'product_name': product_name,
                'image_url': product_image,
                'product_price': product_price,
                'strain_type': strain_type,
                'product_url': product_url
            }
            observations.append(obs)

    # Get the COA URL for each product.
    # TODO: Also get the image_url.
    for i, obs in enumerate(observations):
        coa_url = ''
        driver.get(obs['product_url'])
        sleep(3.33)
        links = driver.find_elements(by=By.TAG_NAME, value='a')
        for link in links:
            if link.get_attribute('href') and '.pdf' in link.get_attribute('href'):
                coa_url = link.get_attribute('href')
                break
        observations[i]['coa_url'] = coa_url
        print('Found COA URL: %s' % coa_url)

    # Close the driver.
    driver.close()

    # Download the COA PDFs.
    license_pdf_dir = os.path.join(data_dir, '.datasets', 'pdfs', 'MMTC-2019-0020')
    for obs in observations:
        coa_url = obs['coa_url']

        # Get the sample ID
        sample_id = coa_url.split('/')[-1].split('.')[0]

        # Format the file.
        outfile = os.path.join(license_pdf_dir, f'{sample_id}.pdf')
        if os.path.exists(outfile) and not overwrite:
            print('Cached: %s' % outfile)
            continue
        sleep(0.3)

        # Download the PDF.
        # FIXME: This is failing every time.
        # try:
        response = requests.get(coa_url, headers=DEFAULT_HEADERS)
        with open(outfile, 'wb') as pdf:
            pdf.write(response.content)
        print('Downloaded: %s' % outfile)
        sleep(3.33)
        # except:
        #     print('Failed to download: %s' % coa_url)

    # Merge The Flowery data with the COA data.
    the_flowery = {'business_dba_name': 'The Flowery'}
    observations = [{**the_flowery, **x} for x in observations]

    # Save the data.
    date = datetime.now().isoformat()[:19].replace(':', '-')
    data = pd.DataFrame(observations)
    data.to_excel(f'{data_dir}/the-flowery-lab-result-urls-{date}.xlsx', index=False)
    print('Saved %i lab result URLs for The Flowery.' % len(data))
    return data


# === Test ===
# [✓] Tested: 2024-04-14 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = 'D://data/florida/results'
    
    # [✓] TEST: Get The Flowery COAs.
    try:
        the_flowery_products = get_product_results_the_flowery(DATA_DIR)
    except Exception as e:
        print('ERROR:', e)
    try:
        the_flowery_coas = get_results_the_flowery(DATA_DIR)
    except Exception as e:
        print('ERROR:', e)
