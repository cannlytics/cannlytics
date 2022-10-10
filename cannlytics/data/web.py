"""
Web Data Tools | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/10/2021
Updated: 10/8/2022
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
import re
from typing import Any, Optional, Tuple
import requests
from bs4 import BeautifulSoup


# === General Web Scraping Tools ===

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


def find_company_url():
    """
    TODO: Find a company's website URL. (Google search for name?)
    """
    raise NotImplementedError


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
