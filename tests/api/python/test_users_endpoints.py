# -*- coding: utf-8 -*-
"""
Title | Project

Author: keega
Created: Sun Feb 14 19:10:21 2021

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Description:
    

Resources:

"""
import os
import requests

BASE = "http://127.0.0.1:4200/"
endpoint = 'users'

url = os.path.join(BASE, endpoint) 
response = requests.post(url, {'email': 'contact@cannlytics.com'})