"""
Authentication Views | Cannlytics console
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 8/29/2021
"""

# Standard imports
# from datetime import datetime, timedelta

# External imports
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView

# Internal imports
from cannlytics.firebase import (
    create_log,
    create_session_cookie,
    initialize_firebase,
    update_document,
    revoke_refresh_tokens,
    verify_session_cookie,
    verify_token,
)
from console.settings import PROJECT_NAME


class LoginView(TemplateView):
    """Dynamic login view for authentication forms."""

    def get_template_names(self):
        page = self.kwargs.get('page', 'login')
        return [f'{PROJECT_NAME}/pages/account/{page}.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def login(request, *args, **argv): #pylint: disable=unused-argument
    """Functional view to create a user session.
    Optional: Ensure that the request succeeds on the client!
    """
    try:
        print('Logging user in...')
        authorization = request.headers.get('Authorization', '')
        token = authorization.split(' ').pop()
        if not token:
            # return HttpResponse(status=401)
            message = 'Authorization token not provided in the request header.'
            return JsonResponse({'error': True, 'message': message}, status=401)
        initialize_firebase()
        print('Initialized Firebase.')

        # Set session cookie in a cookie in the response.
        # response = HttpResponse(status=200)
        response = JsonResponse({'success': True}, status=200)
        # Optional: Let user specify cookie duration?
        # expires_in = timedelta(days=5) 
        # expires = datetime.now() + expires_in
        session_cookie = create_session_cookie(token)
        response['Set-Cookie'] = f'__session={session_cookie}; Path=/'
        response['Cache-Control'] = 'public, max-age=300, s-maxage=900' # TODO: Set the expiration time

        # Save session cookie in the session.
        # Preferred over cookies (but cookies are still needed for production).
        request.session['__session'] = session_cookie

        # Verify the user, create a log, update the user as signed-in,
        # and return a response with the session cookie.
        claims = verify_token(token)
        uid = claims['uid']
        print('Verified user with Firebase Authentication:', claims['email'])
        create_log(
            ref=f'users/{uid}/logs',
            claims=claims,
            action='Signed in.',
            log_type='auth',
            key='login'
        )
        update_document(f'users/{uid}', {'signed_in': True})
        print('Logged user sign-in in Firestore:', uid)
        return response
    except:
        # return HttpResponse(status=401)
        message = 'Authorization failed in entirety. Please contact support.'
        return JsonResponse({'error': True, 'message': message}, status=401)


def logout(request, *args, **argv): #pylint: disable=unused-argument
    """Functional view to remove a user session.
    FIXME: Does not appear to delete the user's session!
    """
    try:
        print('Signing user out.')
        session_cookie = request.COOKIES.get('__session')
        if session_cookie is None:
            session_cookie = request.session['__session']
        claims = verify_session_cookie(session_cookie)
        uid = claims['uid']
        create_log(
            ref=f'users/{uid}/logs',
            claims=claims,
            action='Signed out.',
            log_type='auth',
            key='logout'
        )
        update_document(f'users/{uid}', {'signed_in': False})
        print('Updated user as signed-out in Firestore:', uid)
        revoke_refresh_tokens(claims['sub'])
        # request.session['__session'] = ''
        response = HttpResponse(status=205)
        # response = JsonResponse({'success': True}, status=205)
        response['Set-Cookie'] = '__session=None; Path=/'
        response['Cache-Control'] = 'public, max-age=300, s-maxage=900'
        return response
    except:
        # request.session['__session'] = ''
        response = HttpResponse(status=205)
        # response = JsonResponse({'success': True}, status=205)
        response['Set-Cookie'] = '__session=None; Path=/'
        response['Cache-Control'] = 'public, max-age=300, s-maxage=900'
        return response
