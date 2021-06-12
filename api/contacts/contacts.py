"""
Contacts Views | Cannlytics API
Created: 4/21/2021
Updated: 6/12/2021

API to interface with organization contacts and people associated with
the contact.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST', 'DELETE'])
def contacts(request, format=None):
    """Get, create, update, and delete organization contact information."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')
    
    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')
    
    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')


@api_view(['GET', 'POST', 'DELETE'])
def people(request, format=None):
    """Get, create, update, and delete information for people associated
    with a contact."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')
    
    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')
    
    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')
