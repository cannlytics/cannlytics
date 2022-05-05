"""
Metrc Exceptions | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/5/2021
Updated: 11/8/2021
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Exceptions used when interfacing with the Metrc API.
"""


class MetrcAPIError(Exception):
    """A primary error raised by the Metrc API.
    Insufficient permissions for a request typically
    result in a 401 unauthorized error.
    """

    def __init__(self, response):
        message = self.get_response_messages(response)
        super().__init__(message)
        self.response = response

    def get_response_messages(self, response):
        """Extract error messages from a Metrc API response.
        Args:
            response (Response): A request response from the Metrc API.
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
                message = errors.get('Message', errors.get('message'))
            else:
                message = response.text
        except (AttributeError, KeyError, ValueError):
            message = 'Unknown Metrc API error'
        return message
