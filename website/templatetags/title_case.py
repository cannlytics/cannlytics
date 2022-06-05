"""
Title Case Filter | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/16/2021
Updated: 12/16/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from django.template.defaultfilters import register

@register.filter(name='title_case')
def title_case(key):
    """Capitalize a string, removing underscores and hyphens."""
    # FIXME: Handle greek letters!
    return key.replace('_', ' ').replace('-', ' ').title()
