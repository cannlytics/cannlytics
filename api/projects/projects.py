"""
Projects Views | Cannlytics API
Created: 4/21/2021
Updated: 6/12/2021

API to interface with laboratory projects.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST', 'DELETE'])
def projects(request, format=None):
    """Get, create, or update laboratory projects, a group of samples
    submitted at the same time by a given organization."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')
