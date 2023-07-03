"""
Base API Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/6/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API endpoint base URLs to provide user's with information about
how to use the API in aims for the Cannlytics API to be self-discoverable.
"""
# External imports.
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports.
from api.api import BASE, ENDPOINTS, VERSION


@api_view(['GET'])
def index(request, format=None):
    """Informational base endpoint."""
    message = f'Welcome to the Cannlytics API. The current version is {VERSION} and is located at {BASE}/{VERSION}.'
    return Response({'message': message}, content_type='application/json')


@api_view(['GET'])
def base(request, format=None):
    """Informational version endpoint."""
    message = f'Welcome to {VERSION} of the Cannlytics API. Available endpoints:\n\n'
    for endpoint in ENDPOINTS:
        message += f'{endpoint}\n'
    return Response({'message': message}, content_type='application/json')
