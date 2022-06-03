"""
Test Files Utility Functions
Copyright (c) 2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 5/2/2022
Updated: 5/2/2022
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""
from cannlytics.utils.files import (
    decode_pdf,
    encode_pdf,
    get_blocks,
    get_number_of_lines,
)


# TODO: Test `decode_pdf`.                  
def test_decode_pdf():
    """Test ..."""
    result = decode_pdf()
    assert


# TODO: Test `encode_pdf`.
def test_encode_pdf():
    """Test ..."""
    result = encode_pdf()
    assert


# TODO: Test `get_blocks`.
def test_get_blocks():
    """Test ..."""
    result = get_blocks()
    assert


# TODO: Test `get_number_of_lines`.
def test_get_number_of_lines():
    """Test ..."""
    datafile = '../assets/data/instrument_data/LC2040C.csv'
    result = get_number_of_lines(datafile)
    assert


if __name__ == '__main__':

    test_decode_pdf()
    test_decode_pdf()
    test_get_blocks()
    test_get_number_of_lines()
