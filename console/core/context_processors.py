"""
Context Processors | Cannlytics Console
Copyright (c) 2021 Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 4/26/2021
Updated: 11/26/2021
"""
# External imports.
from django.conf import settings

def selected_settings(request): #pylint: disable=unused-argument
    """Include relevant settings in a view's context."""
    return {
        'APP_VERSION_NUMBER': settings.APP_VERSION_NUMBER,
    }
