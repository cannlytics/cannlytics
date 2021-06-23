"""
Analyses Views | Cannlytics API
Created: 4/21/2021
Updated: 6/12/2021

API to interface with cannabis regulation information.
"""

# External imports
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth import auth


@api_view(['GET', 'POST', 'DELETE'])
def analytes(request, format=None, analyte_id=None):
    """Get, create, or update information about cannabis analysis analytes."""

    print('Requested analyte:', analyte_id)
    model_type = 'analyte'
    claims = auth.verify_session(request)
    uid = claims['uid']
    print('User:', uid)

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')
