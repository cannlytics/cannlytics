# -*- coding: utf-8 -*-
"""
Test Labs Endpoints | Cannlytics API

Copyright © 2021 Cannlytics
Author: Keegan Skeate <contact@cannlytics.com>
Created: 2/1/2021

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""
import os
import pytest
import requests


BASE = "http://127.0.0.1:4200/"
ENDPOINTS = ["", "/labs"]

# TODO: Test authenticate.

# TODO: Test updating a lab.

# TODO: Test getting and creating lab logs.

# TODO: Test getting and creating lab analyses.


@pytest.fixture
def target_endpoints():
    """Target endpoints."""
    return target_endpoints


@pytest.fixture
def expected_result():
    """Expected result to be returned."""
    return [200] * len(ENDPOINTS)


def test_endpoints(target_endpoints, expected_result):
    """Request each endpoint, expecting responses with 200 status code."""
    metadata = []
    for endpoint in ENDPOINTS:
        url = os.path.join(BASE, endpoint) 
        response = requests.get(url)
        metadata.append(response.status_code)
    assert metadata == expected_result

