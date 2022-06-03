"""
File Utilities | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 5/15/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports.
import os
from base64 import b64encode, decodebytes
import zipfile

# External imports.
import requests
from cannlytics.utils.utils import kebab_case, snake_case


def decode_pdf(data: str, destination: str):
    """Save an base-64 encoded string as a PDF.
    Args:
        data (str): Base-64 encoded string representing a PDF.
        destination (str): The destination for the PDF file.
    """
    bits = decodebytes(data)
    with open(destination, 'wb') as pdf:
        pdf.write(bits)


def encode_pdf(filename: str) -> str:
    """Open a PDF file in binary mode.
    Args:
        filename (str): The full file path of a PDF to encode.
    Returns:
        (str): A string encoded in base-64.
    """
    with open(filename, 'rb') as pdf:
        return b64encode(pdf.read())


def get_blocks(files, size=65536):
    """Get a block of a file by the given size."""
    while True:
        block = files.read(size)
        if not block: break
        yield block


def get_number_of_lines(file_name, encoding='utf-16', errors='ignore'):
    """
    Read the number of lines in a large file.
    Credit: glglgl, SU3 <https://stackoverflow.com/a/9631635/5021266>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    """
    with open(file_name, 'r', encoding=encoding, errors=errors) as f:
        count = sum(bl.count('\n') for bl in get_blocks(f))
        print('Number of rows:', count)
        return count
    


def download_file_from_url(url, destination='', ext=''):
    """Download a file from a URL to a given directory.
    Author: H S Umer farooq <https://stackoverflow.com/a/53153505>
    License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
    """
    get_response = requests.get(url,stream=True)
    file_name = snake_case(url.split('/')[-1])
    file_path = os.path.join(destination, file_name + ext)
    with open(file_path, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return file_path


def unzip_files(_dir, extension='.zip'):
    """Unzip all files in a specified folder.
    Author: nlavr https://stackoverflow.com/a/69101930
    License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
    """
    for item in os.listdir(_dir):
        abs_path = os.path.join(_dir, item)
        if item.endswith(extension):
            file_name = os.path.abspath(abs_path)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(_dir)
            zip_ref.close()
            os.remove(file_name)
        elif os.path.isdir(abs_path):
            unzip_files(abs_path)
