"""
Get Value Given Key Filter | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/16/2021
Updated: 12/16/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from django.template.defaultfilters import register

@register.filter(name='dict_key')
def dict_key(data, key):
    """Returns the value for a given key from a dictionary."""
    value = data.get(key, '')
    if value is None:
        value = ''
    return value
