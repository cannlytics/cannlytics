"""
File Utilities | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/6/2021
Updated: 4/21/2022
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>
"""
# Standard imports.
from base64 import b64encode, decodebytes


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
