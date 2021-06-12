"""
Analyses Views | Cannlytics API
Created: 4/21/2021

API to interface with cannabis regulation information.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST', 'DELETE'])
def analyses(request, format=None):
    """Get, create, or update information about cannabis analyses."""

    if request.method == 'GET':
        # TODO: Implement filters!
        # data = get_collection(f"labs/{org_id}/analyses")
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')


@api_view(['GET', 'POST', 'DELETE'])
def analytes(request, format=None):
    """Get, create, or update information about cannabis analysis analytes."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')
