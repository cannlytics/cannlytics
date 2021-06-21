"""
Console Views | Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 6/21/2021
"""

# External imports
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse

# Internal imports
from api.auth import auth
from cannlytics.firebase import (
    create_log,
    create_session_cookie,
    get_collection,
    get_document,
    initialize_firebase,
    update_document,
    revoke_refresh_tokens,
    verify_session_cookie,
    verify_token,
)
from console.state import layout
from console.utils import (
    # get_model_context,
    get_page_data,
    get_page_context,
)

BASE = 'console'

#-----------------------------------------------------------------------
# Main view
#-----------------------------------------------------------------------

class ConsoleView(TemplateView):
    """Main view used for most console pages."""

    login_url = '/account/sign-in'
    redirect_field_name = 'redirect_to'

    def get_template_names(self):
        """Get the screen's template based on the URL path, where the
        URL is segmented as 'https://{base}/{screen}/{section}/{unit}.
        A number of page template paths are tried, trying to match a unit
        first, then section, then a screen-section, finally a screen.
        Screen-sections and sections are also search for in a general folder.
        """
        screen = self.kwargs.get('screen', 'dashboard')
        section = self.kwargs.get('section', screen)
        unit = self.kwargs.get('unit', section)
        return [
            f'{BASE}/pages/{screen}/{unit}.html',
            f'{BASE}/pages/{screen}/{section}/{unit}.html',
            f'{BASE}/pages/{screen}/{screen}-{section}-{unit}.html',
            f'{BASE}/pages/{screen}/{section}.html',
            f'{BASE}/pages/{screen}/{screen}-{section}.html',
            f'{BASE}/pages/{screen}/{section}/{section}.html',
            f'{BASE}/pages/{screen}/{screen}.html',
            f'{BASE}/pages/misc/{screen}/{screen}-{section}.html',
            f'{BASE}/pages/misc/{screen}/{section}.html',
        ]

    def get_context_data(self, **kwargs):
        """Get context that is used on all pages. The context is retrieved
        dynamically from the app's state. The user's permissions
        are verified on every request. User-specific context and data
        can be returned depending on the page."""
        context = super().get_context_data(**kwargs)
        context['sidebar'] = layout['sidebar']
        context['screen'] = kwargs.get('screen', '')
        context['section'] = kwargs.get('section', '')
        context['unit'] = kwargs.get('unit', '')
        if not context['screen']:
            context['screen'] = 'dashboard'
            context['dashboard'] = layout['dashboard']
        context = get_page_context(self.kwargs, context)
        context = get_page_data(self.kwargs, context)

        # Optional: Get model fields?
        # context = get_model_context(context)

        # Get user and organization data.
        # Optional: Test if get is faster
        user = auth.verify_session(self.request)
        if user:
            uid = user['uid']
            query = {'key': 'team', 'operation': 'array_contains', 'value': uid}
            organizations = get_collection('organizations', filters=[query])
            user_data = get_document(f'users/{uid}')
            if context['screen'] == 'organizations':
                context['organization_context'] = context['organizations']
            context['organizations'] = organizations
            context['user'] = user_data
        # else:
        #     context['organizations'] = []
        #     context['user'] = {}
        return context

    # Optional: Test if get is faster.
    # def get(self, request, *args, **kwargs):
    #     """Get data before rendering context. Any existing user data is
    #     retrieved. If there is no user data in the session, the the
    #     request is verified. If the request is unauthenticated, then
    #     the user is redirected to the sign in page. If the user is
    #     authenticated, then the user's data and organization data is
    #     added to the session."""
    #     user = request.session.get('user', {})
    #     print('User in get session:', user)
    #     return super().get(request, *args, **kwargs)
        # try:
        #     user = auth.verify_session(request)
        # except:
        #     pass

        # print('User in session:', user)
        # try:
        #     if not user:
        #         # FIXME:
        #         # user = auth.verify_session(request)
        #         # user = auth.authenticate_request(request)
        #         print('User verified from request:', user)
        #         if user:
        #             request.session['user'] = user
        #         else:
        #             print('User not detected from request!')
        #             request.session['organizations'] = []
        #             request.session['user'] = {}
                    # return HttpResponseRedirect('/account/sign-in')
        # try:
        #     if user:
        #         uid = user['uid']
        #         query = {'key': 'team', 'operation': 'array_contains', 'value': uid}
        #         organizations = get_collection('organizations', filters=[query])
        #         request.session['organizations'] = organizations
        #     else:
        #         request.session['organizations'] = []
        #         request.session['user'] = {}
        # except:
        #     print('Error adding user + organization data to the session.')
        #     pass
            # Optional: Redirect if no user.
            # return HttpResponseRedirect('/account/sign-in')
        # except:
        #     pass
        # request.session['user'] = get_document(f'users/{uid}')
        # return super().get(request, *args, **kwargs)


#-----------------------------------------------------------------------
# Authentication views
#-----------------------------------------------------------------------

class LoginView(TemplateView):
    """Dynamic login view for authentication forms."""

    def get_template_names(self):
        page = self.kwargs.get('page', 'login')
        return [f'{BASE}/pages/account/{page}.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def login(request, *args, **argv): #pylint: disable=unused-argument
    """Functional view to create a user session."""
    try:
        authorization = request.headers.get('Authorization', '')
        token = authorization.split(' ').pop()
        if not token:
            return HttpResponse(status=401)
        initialize_firebase()
        session_cookie = create_session_cookie(token)
        # FIXME: Return proper json
        # response = HttpResponse(status=204)
        response = JsonResponse('{"success": true}', status=204)
        response.set_cookie(
            key='__session',
            value=session_cookie,
            # expires=expires, # TODO: Set expiration time.
            # httponly=True, # TODO: Explore httponly option
            # secure=True, # TODO: Explore secure option
        )
        # Optional: Test impact of logging on speed.
        claims = verify_token(token)
        uid = claims['uid']
        create_log(
            ref=f'users/{uid}/logs',
            claims=claims,
            action='Signed in.',
            log_type='auth',
            key='login'
        )
        update_document(f'users/{uid}', {'signed_in': True})
        return response
    except:
        return HttpResponse(status=401)


def logout(request, *args, **argv): #pylint: disable=unused-argument
    """Functional view to remove a user session."""
    try:
        session_cookie = request.COOKIES.get('__session')
        # Optional: Test impact of logging on speed.
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
        revoke_refresh_tokens(claims['sub'])
        response = HttpResponse(status=205)
        response.set_cookie('__session', expires=0)
        return response
    except:
        return HttpResponse(status=401)


#-----------------------------------------------------------------------
# Error views
#-----------------------------------------------------------------------

def handler404(request, *args, **argv): #pylint: disable=unused-argument
    """Handle missing pages."""
    status_code = 404
    template = f'{BASE}/pages/misc/errors/{status_code}.html'
    return render(request, template, {}, status=status_code)


def handler500(request, *args, **argv): #pylint: disable=unused-argument
    """Handle internal errors."""
    status_code = 500
    template = f'{BASE}/pages/misc/errors/{status_code}.html'
    return render(request, template, {}, status=status_code)


def no_content(request, *args, **argv): #pylint: disable=unused-argument
    """Return an empty response when needed, such as for a ping."""
    return HttpResponse(status=204)
