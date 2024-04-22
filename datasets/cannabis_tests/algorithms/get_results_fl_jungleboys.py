"""
Get Florida cannabis lab results | JungleBoys
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 4/21/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis lab result data for JungleBoys Florida.

Data Sources:

    - [Jungle Boys Florida](https://jungleboysflorida.com)

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep

# External imports:
from cannlytics.data.coas.coas import CoADoc
from cannlytics.data.web import initialize_selenium
from cannlytics.utils.constants import DEFAULT_HEADERS
import pandas as pd

# Selenium imports.
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class JungleBoys:
    """Download lab results from Jungle Boys' website."""

    def __init__(self, data_dir, headless=False, download_dir=None):
        """Initialize the driver and directories."""
        self.data_dir = data_dir
        self.driver = initialize_selenium(
            headless=headless,
            download_dir=download_dir,
        )
        # self.datasets_dir = os.path.join(data_dir, '.datasets')
        # self.pdf_dir = os.path.join(self.datasets_dir, 'pdfs')
        # self.license_pdf_dir = os.path.join(self.pdf_dir, 'terplife')
        # if not os.path.exists(self.datasets_dir): os.makedirs(self.datasets_dir)
        # if not os.path.exists(self.pdf_dir): os.makedirs(self.pdf_dir)
        # if not os.path.exists(self.license_pdf_dir): os.makedirs(self.license_pdf_dir)

    def get_results_jungle_boys(
            self,
            products_url='https://jungleboysflorida.com/products/',
            pause=3.33,
            initial_pause=3.33,
        ):
        """Get lab results published by Jungle Boys on the public web."""

        # Get products from each store.
        all_products = []
        self.driver.get(products_url)
        sleep(3.33)
        self.verify_age_jungle_boys(self.driver)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dovetail-ecommerce-age-gate-retailer'))
        )
        select_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.dovetail-ecommerce-age-gate-retailer .chakra-button')
        for button in select_buttons:
            try:
                # Scroll into view and click the button
                self.driver.execute_script('arguments[0].scrollIntoView(true);', button)
                sleep(1) # Small delay to ensure visibility
                button.click()
                sleep(5)

                # Get all of the products for the store.
                products = self.get_product_details_jungle_boys(self.driver)
                all_products.extend(products)

                # FIXME: May need to query COAs at this stage.
                pdf_dir = r'D:\data\florida\lab_results\jungleboys\pdfs'
                # product_names = [x['name'] + ' ' + str(x['category']) for x in products]
                product_names = list(set([x['name'] for x in products]))
                self.search_and_download_jungle_boys_coas(
                    self.driver,
                    product_names,
                    pdf_dir,
                    pause=pause,
                    initial_pause=initial_pause,
                )

                # Assuming clicking navigates away or requires you to go back
                # driver.back()
                self.driver.get(products_url)
                # Re-find the buttons to avoid StaleElementReferenceException
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.dovetail-ecommerce-age-gate-retailer .chakra-button'))
                )
                select_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.dovetail-ecommerce-age-gate-retailer .chakra-button')
            except:
                pass
                # select_buttons = driver.find_elements(By.CSS_SELECTOR, '.dovetail-ecommerce-age-gate-retailer .chakra-button')

        # Download each COA (if it doesn't already exist).
        # pdf_dir = r'D:\data\florida\lab_results\jungleboys\pdfs'
        # product_names = [x['name'] + ' ' + str(x['category']) for x in all_products]
        # self.search_and_download_jungle_boys_coas(self.driver, product_names, pdf_dir)

        # Close the driver.
        self.driver.quit()

        # Return the products.
        return all_products

    def verify_age_jungle_boys(self, driver, pause=1):
        """Verify age for Jungle Boys' website."""
        checkbox_js = "document.querySelector('input[type=checkbox].chakra-checkbox__input').click();"
        driver.execute_script(checkbox_js)
        sleep(pause)
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.chakra-button:not([disabled])'))
        )
        continue_button.click()

    def get_product_details_jungle_boys(self, driver):
        products = []
        product_elements = driver.find_elements(By.CSS_SELECTOR, '.wp-block-dovetail-ecommerce-product-list-list-view')
        accessories = ['Accessories', 'Grinders', 'Lighters']
        for el in product_elements:
            driver.execute_script('arguments[0].scrollIntoView(true);', el)
            sleep(0.1)

            # Skip accessories.
            name = el.find_element(By.CSS_SELECTOR, 'div.dovetail-ecommerce-advanced-text').text
            text = el.text
            if any(x in text for x in accessories) and text not in name:
                print('Skipping:', name)
                continue

            # Get the image URL.
            image_url = el.find_element(By.TAG_NAME, 'img').get_attribute('src')

            # Get the category.
            try:
                category = el.find_element(By.CSS_SELECTOR, 'div.dovetail-ecommerce-product-category').text
            except:
                try:
                    category = el.find_element(By.CSS_SELECTOR, 'div.dovetail-ecommerce-product-sub-category').text
                except:
                    category = None

            # Get the quantity.
            quantity = None
            buttons = el.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                button_text = button.text
                if button_text and button_text != 'Add to Bag':
                    quantity = button_text
                    break

            # Get the strain type.
            strain_type = None
            try:
                strain_type = el.find_element(By.CSS_SELECTOR, 'div.dovetail-ecommerce-product-strain').text
            except:
                pass

            # Get the price and total THC.
            price, total_thc = None, None
            lines = el.text.split('\n')
            for line in lines:
                if 'THC' in line:
                    total_thc = line.replace('THC ', '').replace('%', '')
                    try:
                        total_thc = float(total_thc)
                    except:
                        pass
                elif '$' in line:
                    price = line.replace('$ ', '')
                    try:
                        price = float(price)
                    except:
                        pass

            # Record the product details.
            products.append({
                'name': name,
                'image_url': image_url,
                'price': price,
                'category': category,
                'strain_type': strain_type,
                'quantity': quantity,
            })

        # Return the products.
        return products

    def search_and_download_jungle_boys_coas(
            self,
            driver,
            product_names,
            pdf_dir,
            pause=3.33,
            initial_pause=3.33,
            coas_url='https://jungleboysflorida.com/coa/',
        ):
        """Search for and download COAs from Jungle"""
        driver.get(coas_url)
        sleep(initial_pause)
        for product_name in product_names:
            print('Searching for:', product_name)

            # JavaScript to set the value of the search input.
            js_query_selector = "document.querySelector('div.wp-block-create-block-coa__search input[placeholder=\"Search\"]')"
            search_query = product_name.replace('-', '').replace('  ', ' ')
            js_set_value = f"{js_query_selector}.value = '{search_query}';"
            driver.execute_script(js_set_value)

            # Perform the search.
            search_div = driver.find_element(By.CSS_SELECTOR, "div.wp-block-create-block-coa__search")
            search_box = search_div.find_element(By.TAG_NAME, 'input')
            search_query = product_name.replace('-', '').replace('  ', ' ')
            search_box.clear()
            search_box.send_keys(search_query)
            # Optionally, simulate a keypress to trigger any attached event listeners
            # This step mimics pressing the Enter key to submit the search
            # search_box.send_keys(Keys.RETURN)
            sleep(pause)

            # Download the PDFs.
            self.download_pdf_links(driver, pdf_dir)

    def download_pdf_links(self, driver, pdf_dir, pause=3.33, overwrite=False):
        """Download all PDF links in search results."""
        pdf_links = driver.find_elements(By.CSS_SELECTOR, ".wp-block-create-block-coa__result a[target='_blank']")
        pdf_urls = [x.get_attribute('href') for x in pdf_links]
        print('Found %i PDFs total.' % len(pdf_urls))
        all_pdf_links = driver.find_elements(By.CSS_SELECTOR, ".wp-block-create-block-coa__result a[target='_blank']")
        pdf_urls = []
        for link in all_pdf_links:
            # Check if the parent <li> of this link does not have the class "hidden"
            parent_li = link.find_element(By.XPATH, "./ancestor::li[1]")  # Get the immediate parent <li>
            if "hidden" not in parent_li.get_attribute("class"):
                pdf_urls.append(link.get_attribute('href'))
        print('Found %i queried PDFs.' % len(pdf_urls))
        for pdf_url in pdf_urls:
            pdf_name = pdf_url.split('/')[-1]
            pdf_path = os.path.join(pdf_dir, pdf_name)
            if not os.path.exists(pdf_path) and not overwrite:
                print('Downloading:', pdf_path)
                driver.get(pdf_url)
                print('Downloaded:', pdf_path)
                sleep(pause)
            else:
                print('Cached:', pdf_path)


def get_results_fl_jungle_boys(
        data_dir: str,
        download_dir: str,
        dataset_dir: str,
    ):
    """Get lab results for the Jungle Boys in Florida."""

    # Initialize a client to query Jungle Boys COAs.
    downloader = JungleBoys(
        data_dir=data_dir,
        download_dir=download_dir,
        headless=False,
    )

    # Download the COAs.
    downloader.get_results_jungle_boys()

    # Parse the Jungle Boys COAs.
    parser = CoADoc()
    all_pdfs = [x for x in os.listdir(download_dir) if x.endswith('.pdf')]
    coa_data = []
    print('Parsing %i COAs...' % len(all_pdfs))
    for pdf in all_pdfs:
        try:
            doc = os.path.join(download_dir, pdf)
            data = parser.parse(doc)
            if isinstance(data, dict):
                coa_data.append(data)
            elif isinstance(data, list):
                coa_data.extend(data)
            print('Parsed:', doc)
        except:
            print('Error parsing:', doc)

    # Save the Jungle Boys COA data.
    namespace = 'fl-results-jungle-boys'
    all_data = pd.DataFrame(coa_data)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    outfile = os.path.join(dataset_dir,  f'{namespace}-{timestamp}.xlsx')
    parser.save(coa_data, outfile)
    return all_data


# === Test ===
# [✓] Tested: 2024-04-14 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Get Jungle Boys Florida results.
    get_results_fl_jungle_boys(
        data_dir='D://data/florida/results',
        download_dir='D://data/florida/results/pdfs/jungleboys',
        dataset_dir='D://data/florida/results/datasets/jungleboys',
    )