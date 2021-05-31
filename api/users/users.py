"""
Views | Cannlytics API
Created: 1/22/2021
Updated: 4/26/2021

API interface for Cannlytics users to manage their personal information.
"""

# External imports
from json import loads
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Internal imports
from cannlytics.firebase import (
    create_log,
    get_document,
    update_document,
)
from cannlytics.utils import utils
from cannlytics_api.auth import auth


#-----------------------------------------------------------------------
# Users Endpoints
#-----------------------------------------------------------------------

@api_view(['GET', 'POST'])
def users(request):
    """Get, update, or create user's data."""
    print('Request to users endpoint!')
    # try:
    claims = auth.verify_session(request)
    if request.method =='POST':
        post_data = loads(request.body.decode('utf-8'))
        uid = claims['uid']
        try:
            update_document(f'users/{uid}', post_data)
            create_log(
                ref=f'users/{uid}/logs',
                claims=claims,
                action='Updated user data.',
                log_type='users',
                key='user_data',
                changes=[post_data]
            )
            return Response(post_data, content_type='application/json')
        except:
            user_email = post_data['email']
            user = {
                'email': user_email,
                'created_at': utils.get_timestamp(),
                'uid': post_data['uid'],
                'photo_url': f'https://robohash.org/${user_email}?set=set5',
            }
            update_document(f'users/{uid}', post_data)
            create_log(
                f'users/{uid}/logs',
                claims,
                'Created new user.',
                'users',
                'user_data',
                [post_data]
            )
            return Response(user, content_type='application/json')
    else:
        user_data = get_document(f'users/{claims["uid"]}')
        return Response(user_data, content_type='application/json')
    # except:
    #     return Response(
    #         {'success': False},
    #         content_type='application/json',
    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #     )
