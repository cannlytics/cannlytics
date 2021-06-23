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
def analyses(request, format=None, analysis_id=None):
    """Get, create, or update information about cannabis analyses."""

    print('Requested analysis:', analysis_id)
    model_type = 'analyses'
    claims = auth.verify_session(request)
    uid = claims['uid']
    print('User:', uid)

    if request.method == 'GET':
        # TODO: Implement filters!
        # data = get_collection(f"labs/{org_id}/analyses")
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'DELETE':

        return Response({'error': 'not_implemented'}, content_type='application/json')
