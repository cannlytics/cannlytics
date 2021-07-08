"""
API Views | Cannlytics API
Created: 1/22/2021
Updated: 7/8/2021

API to interface with cannabis analytics.
"""

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response


BASE = 'https://console.cannlytics.com/api'
ENDPOINTS = ['labs']
VERSION = 'v1'


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
