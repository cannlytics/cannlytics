"""
Analytics Views | Cannlytics API
Created: 8/1/2021
Updated: 8/1/2021

API to interface with cannabis analytics.
"""
# pylint:disable=line-too-long

# Standard imports
from json import loads

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authenticate_request


@api_view(['GET', 'POST'])
def analytics(request):
    """Get cannabis analytics."""

    # Authenticate the user.
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
    except KeyError:
        message = 'Your request was not authenticated. Ensure that you have a valid session or API key.'
        return Response({'error': True, 'message': message}, status=401)

    # GET pre-defined analytics.
    if request.method == 'GET':
        return Response({'success': True, 'data': {'pre_existing_analytics': True}}, status=200)

    # POST request to get analytics given inputs.
    elif request.method == 'POST':
        posted_data = loads(request.body.decode('utf-8'))
        print('Posted data:', posted_data)
        return Response({'success': True, 'data': {'analytics': posted_data}}, status=200)
