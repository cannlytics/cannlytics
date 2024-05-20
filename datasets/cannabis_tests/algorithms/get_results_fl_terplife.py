"""
Get Florida cannabis lab results | TerpLife Labs
Copyright (c) 2023-2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/18/2023
Updated: 4/21/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis lab result data for TerpLife Labs.

Data Sources:

    - [TerpLife Labs](https://www.terplifelabs.com)

"""
# Standard imports:
from datetime import datetime
import itertools
import os
import random
import string
from time import time, sleep

# External imports:
from cannlytics.data.coas.coas import CoADoc
from cannlytics.data.coas.algorithms.terplife import parse_terplife_coa
from cannlytics.data.web import initialize_selenium
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TerpLifeLabs:
    """Download lab results from TerpLife Labs."""

    def __init__(self, data_dir, namespace='terplife'):
        """Initialize the driver and directories."""
        self.data_dir = data_dir
        self.datasets_dir = os.path.join(data_dir, 'datasets', namespace)
        self.pdf_dir = os.path.join(data_dir, 'pdfs', namespace)
        if not os.path.exists(self.datasets_dir): os.makedirs(self.datasets_dir)
        if not os.path.exists(self.pdf_dir): os.makedirs(self.pdf_dir)
        # self.driver = initialize_selenium(download_dir=self.pdf_dir)

    def get_results_terplife(
            self,
            queries: list,
            url='https://www.terplifelabs.com/coa/',
            wait=30,
        ):
        """Get lab results published by TerpLife Labs on the public web."""
        start = datetime.now()
        # self.driver.get(url)
        # sleep(1)
        with initialize_selenium(download_dir=self.pdf_dir, browser='edge') as driver:
            self.driver = driver
            self.driver.get(url)
            for query in queries:
                print('Querying: %s' % query)
                sleep(1)
                self.query_search_box(query)
                self.download_search_results(wait=wait)
            self.driver.close()
            self.driver.quit()
        end = datetime.now()
        print('Finished downloading TerpLife Labs COAs.')
        print('Time elapsed: %s' % str(end - start))

    def download_search_results(self, wait=30):
        """Download the results of a search."""
        # FIXME: Wait for the table to load instead of simply waiting.
        sleep(wait)
        load = EC.presence_of_element_located((By.CLASS_NAME, 'file-list'))
        table = WebDriverWait(self.driver, wait).until(load)
        rows = table.find_elements(By.CLASS_NAME, 'file-item')
        print('Found %i rows.' % len(rows))
        for row in rows:

            # Skip if the file has already be downloaded.
            try:
                file_name = row.find_element(By.CLASS_NAME, 'file-item-name').text
                if file_name == 'COAS':
                    continue
                outfile = os.path.join(self.pdf_dir, file_name)
                if os.path.exists(outfile):
                    print('Cached: %s' % outfile)
                    continue
            except:
                print('ERROR FINDING: %s' % file_name)
                sleep(60)
                break

            # Click on the icons for each row.
            try:
                self.driver.execute_script('arguments[0].scrollIntoView();', row)
                sleep(3.33)
                row.click()
            except:
                print('ERROR CLICKING: %s' % file_name)
                continue

            # Click the download button.
            try:
                sleep(random.uniform(30, 31))
                download_button = self.driver.find_element(By.CLASS_NAME, 'lg-download')
                download_button.click()
                print('Downloaded: %s' % outfile)
                # FIXME: Properly wait for the download to finish.
                sleep(random.uniform(30, 31))
            except:
                print('ERROR DOWNLOADING: %s' % file_name)
                continue

            # Click the close button.
            try:
                close_button = self.driver.find_element(By.CLASS_NAME, 'lg-close')
                close_button.click()
            except:
                print('ERROR CLOSING: %s' % file_name)

    def query_search_box(self, character):
        """Find the search box and enter text."""
        search_box = self.get_search_box()
        self.driver.execute_script('arguments[0].scrollIntoView();', search_box)
        sleep(0.3)
        search_box.clear()
        search_box.send_keys(character)
        sleep(0.3)
        search_button = search_box.find_element(By.XPATH, 'following-sibling::*[1]')
        search_button.click()

    def get_search_box(self):
        """Find the search box and enter text."""
        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
        for input in inputs:
            if input.get_attribute('placeholder') == 'Enter a keyword to search':
                return input
        return None

    def quit(self):
        """Close the driver."""
        self.driver.close()
        self.driver.quit()


def get_day_month_combinations():
    """Get all day-month combinations."""
    day_month_combinations = []
    for month in range(1, 13):
        if month in [4, 6, 9, 11]:
            days_in_month = 30
        elif month == 2:
            days_in_month = 29
        else:
            days_in_month = 31
        for day in range(1, days_in_month + 1):
            formatted_month = f'{month:02d}'
            formatted_day = f'{day:02d}'
            combination = formatted_month + formatted_day
            day_month_combinations.append(combination)
    return day_month_combinations


def add_digits(strings):
    """Add digits 0-9 to each string in a list."""
    return [s + str(digit) for s in strings for digit in range(10)]


def add_letters(strings):
    """Add letters a-z to each string in a list."""
    return [s + letter for s in strings for letter in string.ascii_lowercase]


# === Test ===
# [✓] Tested: 2024-04-21 by Keegan Skeate <keegan@cannlytics>
if __name__ == '__main__':

    # Query by digit combinations.
    day_month_combinations = get_day_month_combinations()
    queries = [''.join(map(str, x)) for x in itertools.product(range(10), repeat=2)]
    # queries = []

    # Query by alphabetic combinations.
    specific_letters = [x for x in string.ascii_lowercase]
    queries += [a + b for a in specific_letters for b in string.ascii_lowercase]

    # Drill down on specific queries.
    long_letters = [ 'wu', 'us', 'tp', 'qd', 'oo', 'og', 'nd', 'mh', 'it',
                    'io', 'ie', 'fm', 'bu', 'bf', 'at', 'aq', 'ao']
    long_digits = ['81', '61', '51', '41', '40', '30', '20']

    # Create new lists with the combinations
    # queries += add_letters(long_letters)
    # queries += add_digits(long_digits)
    # queries.reverse()
    print('All queries:', queries)

    # Download TerpLife Labs COAs.
    # FIXME: This has a severe memory leak. Chrome may not being closed properly.
    DATA_DIR = 'D://data/florida/results'
    downloader = TerpLifeLabs(DATA_DIR)
    downloader.get_results_terplife(queries)
    downloader.quit()

    # Optional: Search TerpLife for known strains.

    # Find the recently downloaded PDFs.
    days_ago = 365
    pdf_dir = 'D://data/florida/results/pdfs/terplife'
    current_time = time()
    recent_threshold = days_ago * 24 * 60 * 60
    recent_files = []
    for filename in os.listdir(pdf_dir):
        file_path = os.path.join(pdf_dir, filename)
        if os.path.isfile(file_path):
            modification_time = os.path.getmtime(file_path)
            time_difference = current_time - modification_time
            if time_difference <= recent_threshold:
                recent_files.append(file_path)

    # Parse the downloaded PDFs.
    print('Parsing %i recently downloaded files...' % len(recent_files))
    parser = CoADoc()
    all_data = []
    for doc in recent_files:
        try:
            coa_data = parse_terplife_coa(parser, doc, verbose=True)
            all_data.append(coa_data)
            print(f'Parsed: {doc}')
        except Exception as e:
            print('Failed to parse:', doc)
            print(e)

    # Save all of the data.
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_dir = 'D://data/florida/results/datasets/terplife'
    outfile = os.path.join(output_dir, f'fl-results-terplife-{timestamp}.xlsx')
    all_results = pd.DataFrame(all_data)
    all_results.replace(r'\\u0000', '', regex=True, inplace=True)
    parser.save(all_results, outfile)
    print('Saved %i COA data:' % len(all_results), outfile)
