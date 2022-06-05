"""
Greek Letter Filter | Cannlytics Website
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/4/2021
Updated: 6/4/2021
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from django.template.defaultfilters import register

@register.filter(name='greek_letters')
def greek_letters(key):
    """Render common greek letters that may appear in English."""
    render = key
    letters = [
        {'name': 'alpha', 'symbol': 'α'},
        {'name': 'beta', 'symbol': 'β'},
        {'name': 'gamma', 'symbol': 'γ'},
        {'name': 'Delta', 'symbol': 'Δ'},
    ]
    for letter in letters:
        render = render.replace(letter['name'], letter['symbol'])
    return render
