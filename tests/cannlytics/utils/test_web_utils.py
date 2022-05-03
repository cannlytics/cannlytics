"""
Test Web Utility Functions
Copyright (c) 2021-2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 1/27/2021
Updated: 5/2/2022
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>
"""
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import environ
import pytest

# FIXME:
from cannlytics.utils.web import (
    find_company_address,
    find_company_linkedin,
    find_company_url,
    format_params,
    get_page_description,
    get_page_metadata,
    get_page_image,
    get_page_email,
    get_page_favicon,
    get_page_theme_color,
    get_page_phone_number,
)


# @pytest.fixture
# def labs():
#     """Target labs to find metadata."""
#     return [{
#         'name': 'Cannlytics',
#         'website': 'https://cannlytics.com',
#     }]


# @pytest.fixture
# def expected_result():
#     """Expected result to be returned."""
#     return {}


# FIXME: Remove redundant code in logistics?


# TODO: Test `find_company_address`.
def test_find_company_address():
    """Test ..."""
    result = find_company_address()
    assert



# TODO: Test `find_company_linkedin`.
def test_find_company_linkedin():
    """Test ..."""
    result = find_company_linkedin()
    assert



# TODO: Test `find_company_url`.
def test_find_company_url():
    """Test ..."""
    result = find_company_url()
    assert

# FIXME:
# def test_find_labs(labs, expected_result):
#     """Match find_labs results to known value."""
#     env = environ.Env()
#     env.read_env('../.env')
#     credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
#     os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
#     metadata = find_labs.find_labs(labs)
#     assert metadata == expected_result


# TODO: Test `format_params`.
def test_format_params():
    """Test ..."""
    result = format_params()
    assert


# TODO: Test `get_page_description`.
def test_get_page_description():
    """Test ..."""
    result = get_page_description()
    assert


# TODO: Test `get_page_metadata`.
def test_get_page_metadata():
    """Test ..."""
    result = get_page_metadata()
    assert


# TODO: Test `get_page_image`.
def test_get_page_image():
    """Test ..."""
    result = get_page_image()
    assert



# TODO: Test `get_page_favicon`.
def test_get_page_favicon():
    """Test ..."""
    result = get_page_favicon()
    assert



# TODO: Test `get_page_theme_color`.
def test_get_page_theme_color():
    """Test ..."""
    result = get_page_theme_color()
    assert



# TODO: Test `get_page_phone_number`.
def test_get_page_phone_number():
    """Test ..."""
    result = get_page_phone_number()
    assert



# TODO: Test `get_page_email`.
def test_get_page_email():
    """Test ..."""
    result = get_page_email()
    assert


if __name__ == '__main__':

    test_find_company_address()
    test_find_company_linkedin()
    test_find_company_url()
    test_format_params()
    test_get_page_description()
    test_get_page_metadata()
    test_get_page_image()
    test_get_page_favicon()
    test_get_page_theme_color()
    test_get_page_phone_number()
    test_get_page_email()
