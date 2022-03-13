"""
Context Processors | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/26/2021
Updated: 1/10/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
from website.settings import APP_VERSION_NUMBER, DEBUG


def selected_settings(request): #pylint: disable=unused-argument
    """Include relevant settings in a view's context."""
    return {
        'APP_VERSION_NUMBER': APP_VERSION_NUMBER,
        'DEBUG': DEBUG,
    }
