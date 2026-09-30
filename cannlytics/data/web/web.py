"""
Web Data Tools | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/10/2021
Updated: 9/28/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Tools for reading web pages and downloading files: page metadata
    (description, image, favicon, theme color, phone, e-mail), file
    downloads, public Google Drive files, and a Selenium browser for
    pages that need one. Requires ``pip install "cannlytics[web]"``;
    Selenium is imported only when a browser is started.
"""
# Standard imports:
import logging
import os
import re
import tempfile
from time import sleep
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# External imports:
import requests
from bs4 import BeautifulSoup

# Internal imports:
from cannlytics.constants import DEFAULT_HEADERS

# Module logger. A library must not print to stdout.
logger = logging.getLogger(__name__)

# Seconds to wait for a server before giving up: (connect, read).
TIMEOUT = (10, 60)

# === Browser (Selenium) ===

def _selenium():
    """Import Selenium, or say which extra provides it."""
    try:
        from selenium import webdriver
    except ImportError as error:
        raise ImportError(
            'A browser needs Selenium: pip install "cannlytics[web]"'
        ) from error
    return webdriver

def initialize_selenium(
        browser: Optional[str] = None,
        headless: bool = True,
        download_dir: Optional[str] = None,
        arguments: Iterable[str] = (),
    ) -> Any:
    """Start a Selenium WebDriver: Chrome, falling back to Edge.

    Selenium (4.6 and later) finds or downloads a matching driver by
    itself; nothing needs to be on your ``PATH``.

    Args:
        browser: ``'chrome'`` or ``'edge'``; by default Chrome is tried
            first, then Edge.
        headless: Run without a window (default ``True``).
        download_dir: Save downloads here, without prompting.
        arguments: Extra command-line arguments for the browser.

    Returns:
        A WebDriver. Call ``driver.quit()`` when done.

    Raises:
        ImportError: If Selenium is not installed.
        RuntimeError: If no browser could be started; the message
            includes each browser's error.
    """
    webdriver = _selenium()
    errors = []
    for name in [browser] if browser else ['chrome', 'edge']:
        name = name.lower()
        if name not in ('chrome', 'edge'):
            raise ValueError(f"browser must be 'chrome' or 'edge', not {name!r}")
        driver = None
        try:
            if name == 'chrome':
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
            else:
                from selenium.webdriver.edge.options import Options
                from selenium.webdriver.edge.service import Service
            options = Options()
            for argument in ('--window-size=1920,1200', '--disable-gpu', '--no-sandbox', *arguments):
                options.add_argument(argument)
            if headless:
                options.add_argument('--headless=new')
            if download_dir:
                options.add_experimental_option('prefs', {
                    'download.default_directory': os.path.abspath(download_dir),
                    'download.prompt_for_download': False,
                    'download.directory_upgrade': True,
                    'plugins.always_open_pdf_externally': True,
                })
            browser_class = webdriver.Chrome if name == 'chrome' else webdriver.Edge
            driver = browser_class(options=options, service=Service())
            return driver
        except Exception as error:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
            errors.append(f'{name}: {error}')
            logger.warning('Could not start %s: %s', name, error)
    raise RuntimeError('Could not start a browser. ' + ' | '.join(errors))

def download_file_with_selenium(
        url: str,
        driver: Any = None,
        persist: bool = False,
        pause: float = 3.33,
        wait: float = 10,
        el_id: str = 'download',
        method: str = 'iframe',
        tag_name: str = 'iframe',
        filename: Optional[str] = None,
        download_dir: Optional[str] = None,
        headless: bool = True,
    ) -> Optional[str]:
    """Download a file from a page that needs a browser.

    Args:
        url: The page.
        driver: A WebDriver to use; by default one is started (and quit
            afterwards, even if the download fails).
        persist: Keep the driver open.
        pause: Seconds to wait for the browser to finish a download.
        wait: Seconds to wait for the download element.
        el_id: The id of the download button (``'iframe'`` and
            ``'button'`` methods).
        method: ``'iframe'`` (a button inside an iframe), ``'button'``,
            ``'confident_cannabis'``, or ``'link'`` (an element whose
            ``href`` is the file, fetched directly).
        tag_name: The iframe or link tag.
        filename: For ``'link'``: the file name (default: from the URL).
        download_dir: Where files are saved (default: the working
            directory).
        headless: Run a started browser without a window.

    Returns:
        For ``'link'``, the path of the saved file; otherwise ``None``
        (the browser saves the file to ``download_dir``).
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    owned = driver is None
    if owned:
        driver = initialize_selenium(headless=headless, download_dir=download_dir)
    saved = None
    try:
        driver.get(url)
        if method == 'iframe':
            frame = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
            driver.switch_to.frame(frame)
            WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.ID, el_id))).click()
        elif method == 'button':
            WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.ID, el_id))).click()
        elif method == 'confident_cannabis':
            button = (By.XPATH, "//button[contains(@class, 'btn-primary') and contains(@ng-click, 'downloadFile')]")
            WebDriverWait(driver, wait).until(EC.element_to_be_clickable(button)).click()
        else:
            element = WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
            file_url = element.get_attribute('href')
            name = filename or os.path.basename(urlparse(file_url).path)
            saved = download_file_from_url(file_url, destination=download_dir or '', file_name=name)
        sleep(pause)
    finally:
        if owned and not persist:
            driver.quit()
    return saved

# === Page metadata ===

def format_params(parameters: Dict[str, str], **kwargs) -> Dict[str, Any]:
    """Map keyword arguments to an API's parameter names, dropping empty ones.

    Example::

        format_params({'limit': '$limit'}, limit=10, order=None)   # {'$limit': 10}
    """
    return {parameters[key]: value for key, value in kwargs.items() if value}

def get_page_metadata(url: str, timeout: Any = TIMEOUT) -> Tuple[requests.Response, BeautifulSoup, Dict[str, Any]]:
    """Fetch a page and read its metadata.

    Args:
        url: The page (``http://`` is assumed if no scheme is given).
        timeout: Seconds to wait for the server.

    Returns:
        The response, the parsed HTML, and a dictionary with
        ``description``, ``image_url``, ``favicon``, and ``brand_color``
        (image and favicon as absolute URLs).
    """
    if not urlparse(url).scheme:
        url = 'http://' + url
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    html = BeautifulSoup(response.content, 'html.parser')
    metadata = {
        'description': get_page_description(html),
        'image_url': get_page_image(html, url=response.url),
        'favicon': get_page_favicon(html, response.url),
        'brand_color': get_page_theme_color(html),
    }
    return response, html, metadata

def _meta(html: BeautifulSoup, *names: str) -> Optional[str]:
    """The content of the first ``<meta>`` found by name or property."""
    for name in names:
        for attribute in ('name', 'property', 'itemprop'):
            tag = html.find('meta', attrs={attribute: name})
            if tag and tag.get('content'):
                return tag['content'].strip()
    return None

def get_page_description(html: BeautifulSoup) -> Optional[str]:
    """A page's description: its description meta tags, else its first paragraph."""
    description = _meta(html, 'description', 'og:description', 'twitter:description')
    if description:
        return description
    paragraph = html.find('p')
    text = paragraph.get_text(' ', strip=True) if paragraph else ''
    return text or None

def get_page_image(html: BeautifulSoup, index: int = 0, url: str = '') -> Optional[str]:
    """A page's image: its sharing image, else its ``index``-th ``<img>``.

    Relative addresses are resolved against ``url`` when it is given.
    """
    image = _meta(html, 'og:image', 'twitter:image', 'image')
    if not image:
        images = [tag['src'] for tag in html.find_all('img', src=True)]
        image = images[index] if -len(images) <= index < len(images) else None
    return urljoin(url, image) if image and url else image

def get_page_favicon(html: BeautifulSoup, url: str = '') -> Optional[str]:
    """A page's favicon, absolute when ``url`` is given; else the site's ``/favicon.ico``."""
    link = html.find('link', rel=lambda rel: rel and 'icon' in [r.lower() for r in (rel if isinstance(rel, list) else rel.split())])
    if link and link.get('href'):
        return urljoin(url, link['href']) if url else link['href']
    if not url:
        return None
    parts = urlparse(url)
    return f'{parts.scheme}://{parts.netloc}/favicon.ico'

def get_page_theme_color(html: BeautifulSoup) -> Optional[str]:
    """A page's theme color (``<meta name="theme-color">``)."""
    return _meta(html, 'theme-color')

_PHONE = re.compile(r'\(?\b[2-9]\d{2}\)?[-. ]?[2-9]\d{2}[-. ]?\d{4}\b')
_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
_NOT_EMAIL = re.compile(r'\.(png|jpe?g|gif|svg|webp|ico|css|js)$', re.IGNORECASE)

def get_page_phone_number(html: BeautifulSoup, response: Any = None, index: int = 0) -> str:
    """A phone number on a page: from ``tel:`` or ``callto:`` links, else the page text.

    Returns:
        The ``index``-th number found by link, else the first in the
        text, else ``''``.
    """
    links = html.select('a[href^="tel:"], a[href^="callto:"]')
    numbers = [link.get_text(strip=True) or link['href'].split(':', 1)[1] for link in links]
    if -len(numbers) <= index < len(numbers):
        return numbers[index]
    text = response.text if response is not None else html.get_text(' ')
    match = _PHONE.search(text)
    return match.group(0) if match else ''

def get_page_email(html: BeautifulSoup, response: Any = None, index: int = -1) -> str:
    """An e-mail address on a page: from ``mailto:`` links, else the page text.

    File names such as ``logo@2x.png`` are not addresses.

    Returns:
        The ``index``-th address found (the last by default), else ``''``.
    """
    addresses = [link['href'][7:].split('?')[0] for link in html.select('a[href^="mailto:"]')]
    if not addresses:
        text = response.text if response is not None else html.get_text(' ')
        addresses = [a for a in _EMAIL.findall(text) if not _NOT_EMAIL.search(a)]
    addresses = [a for a in addresses if a]
    return addresses[index] if -len(addresses) <= index < len(addresses) else ''

# === Downloads ===

def _save(response: requests.Response, path: str, chunk_size: int = 1 << 16) -> str:
    """Stream a response to ``path`` atomically: a failure leaves no partial file."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=folder, suffix='.part')
    try:
        with os.fdopen(handle, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise
    return path

def download_file_from_url(
        url: str,
        destination: str = '',
        ext: str = '',
        file_name: Optional[str] = None,
        timeout: Any = TIMEOUT,
    ) -> str:
    """Download a file to a folder.

    Args:
        url: The file.
        destination: The folder (created if missing).
        ext: An extension to add to the file name if it lacks it.
        file_name: The file name (default: the URL's last segment).
        timeout: Seconds to wait for the server.

    Returns:
        The path of the saved file.

    Raises:
        requests.HTTPError: If the server answers with an error; nothing
            is written.
    """
    response = requests.get(url, stream=True, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    name = file_name or os.path.basename(urlparse(url).path) or 'download'
    if ext and not name.endswith(ext):
        name += ext
    return _save(response, os.path.join(destination, name))

# === Google Drive ===

_DRIVE_ID = re.compile(r'(?:/d/|[?&]id=)([A-Za-z0-9_-]{10,})')

def download_google_drive_file(drive_file: str, destination: str, timeout: Any = TIMEOUT) -> str:
    """Download a public Google Drive file.

    Large files are served behind a "can't scan for viruses" page; its
    confirmation form is submitted (the older cookie token is also
    honored). If Drive still answers with a page rather than the file,
    nothing is saved.

    Args:
        drive_file: A Drive file ID or sharing URL.
        destination: The local file path.
        timeout: Seconds to wait for the server.

    Returns:
        ``destination``.

    Raises:
        ValueError: If Drive returns a web page instead of the file
            (a private file, or an unrecognized confirmation page).
    """
    match = _DRIVE_ID.search(drive_file)
    drive_id = match.group(1) if match else drive_file
    session = requests.Session()
    response = session.get('https://drive.google.com/uc', params={'id': drive_id, 'export': 'download'},
                           stream=True, timeout=timeout)
    response.raise_for_status()
    token = next((value for key, value in response.cookies.items() if key.startswith('download_warning')), None)
    if token:
        response = session.get('https://drive.google.com/uc', params={'id': drive_id, 'export': 'download', 'confirm': token},
                               stream=True, timeout=timeout)
    elif 'text/html' in response.headers.get('Content-Type', ''):
        form = BeautifulSoup(response.text, 'html.parser').find('form')
        if form is not None and form.get('action'):
            fields = {tag['name']: tag.get('value', '') for tag in form.find_all('input') if tag.get('name')}
            response = session.get(urljoin(response.url, form['action']), params=fields, stream=True, timeout=timeout)
    response.raise_for_status()
    if 'text/html' in response.headers.get('Content-Type', ''):
        raise ValueError(f'Google Drive returned a page, not the file {drive_id!r}: is it shared publicly?')
    return _save(response, destination)

__all__: List[str] = [
    'TIMEOUT', 'download_file_from_url', 'download_file_with_selenium', 'download_google_drive_file',
    'format_params', 'get_page_description', 'get_page_email', 'get_page_favicon', 'get_page_image',
    'get_page_metadata', 'get_page_phone_number', 'get_page_theme_color', 'initialize_selenium',
]
