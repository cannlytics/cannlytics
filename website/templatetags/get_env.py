"""
Get Environment Variable Filter | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/16/2021
Updated: 12/16/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
import os

from django.template.defaultfilters import register

@register.filter(name='get_env')
def get_env(key):
    """Get a variable from the .env file."""
    return os.environ.get(key, None)
