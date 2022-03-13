"""
Stats Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/21/2021
Updated: 12/5/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory statistics.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def stats(request, format=None):
    """Get, create, or update statistics."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

        # Return an error if no author is specified.
        # error_message = 'Unknown error, please notify <support@cannlytics.com>'
        # return Response(
        #     {'error': error_message},
        #     content_type='application/json',
        #     status=status.HTTP_400_BAD_REQUEST
        # )
