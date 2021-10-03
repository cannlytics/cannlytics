# -*- coding: utf-8 -*-
"""
Metrc Exceptions | Cannlytics

Exceptions used when interfacing with the Metrc API.
"""


class TraceabilityException(Exception):
    """A base class for traceability system exceptions."""


class MetrcAPIError(TraceabilityException):
    """A primary error raised by the API.
    Insufficient permissions for a request typically
    result in a 401 unauthorized error.
    """

    def __init__(self, response):
        super(MetrcAPIError, self).__init__(self._extract_text(response))
        self.response = response

    def _extract_text(self, response):
        return self._text_from_detail(response) or response.text

    def _text_from_detail(self, response):
        try:
            errors = response.json()
            if isinstance(errors, list):
                message = '\n'.join(errors)
                return f'\n---------------\n{message}\n---------------'
            else:
                message = errors['Message']
                return f'\n---------------\n{message}\n---------------'
        except (AttributeError, KeyError, ValueError):
            message = 'Unknown API error'
            return f'\n---------------\n{message}\n---------------'
