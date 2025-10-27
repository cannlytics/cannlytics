"""
Web Data Tools | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/10/2021
Updated: 12/31/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Resources:
    https://stackoverflow.com/questions/54416896/how-to-scrape-email-and-phone-numbers-from-a-list-of-websites
    https://hackersandslackers.com/scraping-urls-with-beautifulsoup/

TODO:
    Improve with requests-html - https://github.com/psf/requests-html
    - Get #about
    - Get absolute URLs
    - Search for text (prices/analyses)
        r.html.search('Python is a {} language')[0]
"""
# Standard imports:
import os
import re
from time import sleep
from typing import Any, Optional, Tuple

# External imports:
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
try:
    import chromedriver_binary  # Adds chromedriver binary to path.
except ImportError:
    pass # Otherwise, ChromeDriver should be in your path.


# === Dynamic HTML Scraping Tools ===

# FIXME: This may be causing a severe memory leak.
def initialize_selenium(
        browser=None,
        headless=True,
        download_dir=None,
    ) -> Any:
    """
    Initialize a Selenium WebDriver with preference for Chrome, falling back to Edge.
    The function attempts to initialize Chrome first; if it fails, it tries Edge.
    Users can specify a browser if desired.

    Args:
        browser (str, optional): The preferred browser to use ('chrome' or 'edge'). If None, tries Chrome first, then Edge.
        headless (bool): Whether to run the browser in headless mode. Defaults to True.
        download_dir (str, optional): Path to the directory for automatic file downloads. Defaults to None.

    Returns:
        webdriver: An instance of a Selenium WebDriver.

    Raises:
        RuntimeError: If it fails to initialize both Chrome and Edge drivers.
    """
    browsers = ['chrome', 'edge']
    if browser:
        browsers = [browser]
    for browser in browsers:
        try:
            if browser.lower() == 'chrome':
                service = Service()
                options = ChromeOptions()
                options.add_argument('--window-size=1920,1200')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                if headless:
                    options.add_argument('--headless')
            else:
                service = Service()
                options = EdgeOptions()
                if headless:
                    options.add_argument('--headless')
            if download_dir:
                default_directory = os.path.normpath(os.path.join(os.getcwd(), download_dir))
                prefs = {
                    'download.default_directory': default_directory,
                    'download.prompt_for_download': False,
                    'download.directory_upgrade': True,
                    'plugins.always_open_pdf_externally': True,
                    # "safebrowsing.enabled": True
                }
                options.add_experimental_option('prefs', prefs)
            if browser.lower() == 'chrome':
                driver = webdriver.Chrome(options=options, service=service)
            else:
                driver = webdriver.Edge(options=options, service=service)
            return driver
        except Exception as e:
            # Note: This has been added to try to fix the memory leak.
            try:
                driver.quit()
            except:
                pass
            print(f"Failed to initialize the {browser} driver. Trying the next one. Error: {e}")
    raise RuntimeError("Failed to initialize both Chrome and Edge drivers.")


# === Static HTML Scraping Tools ===

def format_params(parameters, **kwargs):
    """Format given keyword arguments HTTP request parameters.
    Returns:
        (dict): Returns the parameters as a dictionary.
    """
    params = {}
    for param in kwargs:
        if kwargs[param]:
            key = parameters[param]
            params[key] = kwargs[param]
    return params


def get_page_metadata(url: str) -> Tuple:
    """Get the metadata of a web page.
    Args:
        url (str): The URL to scrape.
    Returns:
        (HTTPResponse): The HTTP response.
        (str): The HTML text.
        (dict): A dictionary of metadata, including: `description`, `image_url`,
            `favicon`, and `brand_color`.
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    }
    # Handle URLs without http beginning
    if not url.startswith('http'):
        url = 'http://' + url
    response = requests.get(url, headers=headers)
    html = BeautifulSoup(response.content, 'html.parser')
    metadata = {
        'description': get_page_description(html),
        'image_url': get_page_image(html),  # FIXME: Append URL if relative path.
        'favicon': get_page_favicon(html, url),
        'brand_color': get_page_theme_color(html),
    }
    return response, html, metadata


def get_page_description(html: str) -> str:
    """Get the description of a web page.
    Args:
        html (str): A body of HTML text.
    Returns:
        (str): A description excerpt from the page.
    """
    description = None
    if html.find('meta', property='description'):
        description = html.find('meta', property='description').get('content')
    elif html.find('meta', property='og:description'):
        description = html.find('meta', property='og:description').get('content')
    elif html.find('meta', property='twitter:description'):
        description = html.find('meta', property='twitter:description').get('content')
    elif html.find('p'):
        description = html.find('p').contents
    if isinstance(description, list):
        try:
            description = description[0]
        except IndexError:
            pass
    return description


def get_page_image(html: str, index: Optional[int] = 0) -> str:
    """Get an image on a web page, the first image by default.
    Args:
        html (str): A body of HTML text.
    Returns:
        (str): Returns the first image URL if found.
    """
    image = None
    if html.find('meta', property='image'):
        image = html.find('meta', property='image').get('content')
    elif html.find('meta', property='og:image'):
        image = html.find('meta', property='og:image').get('content')
    elif html.find('meta', property='twitter:image'):
        image = html.find('meta', property='twitter:image').get('content')
    elif html.find('img', src=True):
        image = html.find_all('img')[index].get('src')
    return image


def get_page_favicon(html: str, url: Optional[str] = '') -> str:
    """Get the favicon from a web page.
    Args:
        html (str): A body of HTML text.
        url (str): The URL of the page.
    Returns:
        (str): The URL of any potential favicon.
    """
    if html.find('link', attrs={'rel': 'icon'}):
        favicon = html.find('link', attrs={'rel': 'icon'}).get('href')
    elif html.find('link', attrs={'rel': 'shortcut icon'}):
        favicon = html.find('link', attrs={'rel': 'shortcut icon'}).get('href')
    else:
        favicon = f"{url.rstrip('/')}/favicon.ico"
    return favicon


def get_page_theme_color(html: str) -> str:
    """Get the theme color of a web page.
    Args:
        html (str): A body of HTML text.
    Returns:
        (str): An hex color code if found.
    """
    if html.find('meta', property='theme-color'):
        color = html.find('meta', property='theme-color').get('content')
        return color
    else:
        return None


def get_page_phone_number(html: str, response: Any, index=0) -> str:
    """Get a phone number on a web page, the first found by default.
    Args:
        html (str): A body of HTML text.
        response (HTTPResponse): An HTTP response.
    Returns:
        (str): Returns the first phone number found.
    """
    try:
        phone = html.select('a[href*=callto]')[index].text
        return phone
    except:
        pass
    try:
        phone = re.findall(
            r'\(?\b[2-9][0-9]{2}\)?[-][2-9][0-9]{2}[-][0-9]{4}\b', response.text
        )[0]
        return phone
    except:
        pass
    try:
        phone = re.findall(
            r'\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b', response.text
        )[-1]
        return phone
    except:
        print('Phone number not found')
        phone = ''
        return phone


def get_page_email(
        html: str,
        response: Any,
        index: Optional[int] = -1,
    ) -> str:
    """Get an email on a web page, the last email by default.
    Args:
        html (str): A body of HTML text.
        response (HTTPResponse): An HTTP response.
    Returns:
        (str): Returns the first email found on the page.
    """
    try:
        email = re.findall(
            r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', response.text
        )[-1]
        return email
    except:
        pass
    try:
        email = html.select('a[href*=mailto]')[index].text
    except:
        print('Email not found')
        email = ''
        return email


def find_company_address():
    """
    TODO: Try to find a company's address from their website, then Google Maps.
    """
    raise NotImplementedError
    # street, city, state, zipcode = None, None, None, None
    # return street, city, state, zipcode


def find_company_linkedin():
    """
    TODO: Tru to find a company's LinkedIn URL. (Try to find LinkedIn on homepage?)
    """
    raise NotImplementedError


def find_company_url(company_name: str):
    """
    TODO: Find a company's website URL. (Google search for name?)
    """
    raise NotImplementedError


# === Download Tools ===

def download_file_from_url(url, destination='', ext='', file_name = None):
    """Download a file from a URL to a given directory.
    Author: H S Umer farooq <https://stackoverflow.com/a/53153505>
    License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
    """
    get_response = requests.get(url, stream=True)
    if file_name is None:
        file_name = url.split('/')[-1]
    if not file_name.endswith(ext):
        file_name = file_name + ext
    file_path = os.path.join(destination, file_name)
    with open(file_path, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return file_path


def download_file_with_selenium(
        url,
        driver=None,
        persist=False,
        pause=3.33,
        wait=10,
        el_id='download',
        method='iframe',
        tag_name='iframe',
        filename=None,
        download_dir=None,
        headless=True,
    ):
    if driver is None:
        driver = initialize_selenium(
            headless=headless,
            download_dir=download_dir,
        )
    driver.get(url)
    if method == 'iframe':
        presence = EC.presence_of_element_located((By.TAG_NAME, tag_name))
        el = WebDriverWait(driver, 10).until(presence)
        driver.switch_to.frame(el)
        presence = EC.presence_of_element_located((By.ID, el_id))
        download_button = WebDriverWait(driver, wait).until(presence)
        download_button.click()
    elif method == 'button':
        presence = EC.presence_of_element_located((By.ID, el_id))
        download_button = WebDriverWait(driver, wait).until(presence)
        download_button.click()
    elif method == 'confident_cannabis':
        try:
            download_button = WebDriverWait(driver, wait).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and contains(@ng-click, 'downloadFile')]"))
            )
            download_button.click()
            sleep(pause)
        except Exception as e:
            print(f"Error downloading Confident Cannabis COA: {str(e)}")
    else:
        presence = EC.presence_of_element_located((By.TAG_NAME, tag_name))
        el = WebDriverWait(driver, 10).until(presence)
        pdf_url = el.get_attribute('href')
        response = requests.get(pdf_url)
        if response.status_code == 200:
            if filename is None:
                filename = os.path.basename(pdf_url)
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as file:
                file.write(response.content)
    sleep(pause)
    if not persist:
        driver.close()
        driver.quit()


# === Google Drive Tools ===

def download_google_drive_file(drive_file, destination):
    """Download a public Google Drive file given its ID and a destination.
    Args:
        drive_file (str): A Google Drive ID or URL for a file.
        destination (str): The local file path and name.
    Credit: turdus-merula <https://stackoverflow.com/a/39225272/5021266>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    """
    drive_id = drive_file
    if drive_id.startswith('https://drive.google'):
        drive_id = drive_id.split('/d/')[-1].split('/')[0]
    drive_base = 'https://docs.google.com/uc?export=download'
    drive_session = requests.Session()
    drive_response = drive_session.get(
        drive_base,
        params={'id': drive_id},
        stream=True,
    )
    drive_token = download_google_drive_file_confirm_token(drive_response)
    if drive_token:
        drive_response = drive_session.get(
            drive_base,
            params={'id': drive_id, 'confirm': drive_token},
            stream = True
        )
    download_google_drive_file_save_response(drive_response, destination)    


def download_google_drive_file_confirm_token(drive_response):
    """
    Credit: turdus-merula <https://stackoverflow.com/a/39225272/5021266>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    """
    for k, v in drive_response.cookies.items():
        if k.startswith('download_warning'):
            return v
    return None


def download_google_drive_file_save_response(drive_response, destination):
    """
    Credit: turdus-merula <https://stackoverflow.com/a/39225272/5021266>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    """
    CHUNK_SIZE = 32768
    with open(destination, 'wb') as f:
        for chunk in drive_response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
