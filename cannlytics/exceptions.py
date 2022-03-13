"""
Cannlytics Exceptions | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/8/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Exceptions used when interfacing with the Cannlytics module.
"""


class CannlyticsError(Exception):
    """A base class for Cannlytics system exceptions."""


class CannlyticsAPIError(CannlyticsError):
    """A primary error raised by the Cannlytics API."""

    def __init__(self, response):
        message = self.get_error_message(response)
        super().__init__(message)
        self.response = response

    def get_error_message(self, response):
        """Extract error message from a Cannlytics API response.
        Args:
            response (Response): A request response from the Cannlytics API.
        Returns:
            (str): Returns any error messages.
        """
        try:
            errors = response.json()
            if isinstance(errors, list):
                try:
                    message = '\n'.join(errors)
                except TypeError:
                    message = '\n'.join([x.get('message') for x in errors])
            elif isinstance(errors, dict):
                message = errors.get('message')
            else:
                message = response.text
        except (AttributeError, KeyError, ValueError):
            message = 'Unknown Cannlytics API error'
        return message
