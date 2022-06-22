"""
Multiply Filter | Cannlytics Website
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/21/2021
Updated: 6/21/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from django.template.defaultfilters import register

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply a value by a given argument.
    Example:
        {{ quantity | multiply:price }}
    """
    return float(value) * float(arg)
    