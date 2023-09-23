"""
Users API Endpoint Test | Cannlytics API

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 2/14/2021
Updated: 6/23/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests

BASE = "http://127.0.0.1:4200/"
endpoint = 'users'

url = os.path.join(BASE, endpoint) 
response = requests.post(url, {'email': 'contact@cannlytics.com'})