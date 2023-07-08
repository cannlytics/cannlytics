"""
Context Processors | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/26/2021
Updated: 7/6/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Internal imports.
from website.settings import APP_VERSION_NUMBER, DEBUG


def selected_settings(request): #pylint: disable=unused-argument
    """Include relevant settings in a view's context."""
    return {
        'DEBUG': DEBUG,
        'version': APP_VERSION_NUMBER
    }
