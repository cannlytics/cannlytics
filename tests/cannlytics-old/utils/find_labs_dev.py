# -*- coding: utf-8 -*-
"""
Test Find Labs
Created: 1/27/2021
"""
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import environ
import pytest
from cannlytics import find_labs # pylint: disable=import-error


@pytest.fixture
def labs():
    """Target labs to find metadata."""
    return [{
        'name': 'Cannlytics',
        'website': 'https://cannlytics.com',
    }]


@pytest.fixture
def expected_result():
    """Expected result to be returned."""
    return {}


def test_find_labs(labs, expected_result):
    """Match find_labs results to known value."""
    env = environ.Env()
    env.read_env('../.env')
    credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    metadata = find_labs.find_labs(labs)
    assert metadata == expected_result

