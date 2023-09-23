"""
Authentication Views | Cannlytics Console
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/18/2020
Updated: 12/13/2021
License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
"""
# External imports
from django.http import JsonResponse
from django.views.generic.base import TemplateView

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    create_log,
    create_session_cookie,
    revoke_refresh_tokens,
    update_document,
    verify_token,
)
from lims.settings import (
    PROJECT_NAME as BASE,
    DEFAULT_FROM_EMAIL,
    SESSION_COOKIE_AGE,
)
from lims.state import app_context


class LoginView(TemplateView):
    """Dynamic login view for authentication forms."""

    def get_template_names(self):
        page = self.kwargs.get('page', 'login')
        return [f'{BASE}/pages/account/{page}.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = app_context
        return context


def login(request, *args, **argv): #pylint: disable=unused-argument
    """Functional view to create a user session."""
    try:

        # Ensure that the user passed an authorization bearer token.
        authorization = request.headers.get('Authorization')
        token = authorization.split(' ').pop()
        if not token:
            message = 'Authorization token not provided in the request header.'
            return JsonResponse({'success': False, 'message': message}, status=401)

        # Initialize Firebase and verify the Firebase ID token.
        claims = verify_token(token)
        uid = claims['uid']

        # Create and set a session cookie in the response.
        cache = f'public, max-age={SESSION_COOKIE_AGE}, s-maxage={SESSION_COOKIE_AGE}'
        session_cookie = create_session_cookie(token)
        response = JsonResponse({'success': True}, status=200)
        response['Cache-Control'] = cache
        response['Set-Cookie'] = f'__session={session_cookie}; Path=/'

        # Also save the session cookie in the session.
        # Note: The session is preferred over cookies,
        # but cookies are currently needed for production.
        request.session['__session'] = session_cookie

        # Log the login and update the user as signed-in.
        update_document(f'users/{uid}', {'signed_in': True})
        create_log(
            ref=f'users/{uid}/logs',
            claims=claims,
            action='Signed in.',
            log_type='auth',
            key='login'
        )
        return response

    except:
        message = f'Authorization failed in entirety. Please contact {DEFAULT_FROM_EMAIL}.'
        return JsonResponse({'success': False, 'message': message}, status=401)


def logout(request, *args, **argv): #pylint: disable=unused-argument
    """Functional view to remove a user session."""
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        update_document(f'users/{uid}', {'signed_in': False})
        create_log(
            ref=f'users/{uid}/logs',
            claims=claims,
            action='Signed out.',
            log_type='auth',
            key='logout'
        )
        revoke_refresh_tokens(claims['sub'])
        response = JsonResponse({'success': True}, status=200)
        response['Set-Cookie'] = '__session=None; Path=/'
        request.session['__session'] = ''
        return response
    except KeyError:
        response = JsonResponse({'success': False}, status=205)
        response['Set-Cookie'] = '__session=None; Path=/'
        request.session['__session'] = ''
        return response
