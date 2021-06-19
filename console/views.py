"""
Console Views | Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 5/10/2021
"""

# External imports
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse

# Internal imports
from api.auth import auth
from cannlytics.firebase import get_collection, get_document
from console.state import layout
from console.utils import (
    get_model_context,
    get_page_data,
    get_page_context,
    get_user_context,
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
        # context = get_user_context(self.request, context)
        # context = get_model_context(context)
        # FIXME: Hot-fix for organizations namespace clash in context!
        if context['screen'] == 'organizations':
            context['organization_context'] = context['organizations']
        context['organizations'] = self.request.session['organizations']
        context['user'] = self.request.session['user']
        return context

    def get(self, request, *args, **kwargs):
        """Get data before rendering context. The session is verified
        if there is not a user ID (`uid`) in the session. Data collected
        includes: user, organizations."""
        uid = request.session.get('uid')
        if not uid:
            user_claims = auth.verify_session(request)
            uid = user_claims.get('uid')
            if not uid:
                request.session['organizations'] = []
                request.session['user'] = {}
                return super().get(request, *args, **kwargs)
        query = {'key': 'team', 'operation': 'array_contains', 'value': uid}
        organizations = get_collection('organizations', filters=[query])
        request.session['organizations'] = organizations
        request.session['user'] = get_document(f'users/{uid}')
        # TODO: If no user navigate to login.
        return super().get(request, *args, **kwargs)


#-----------------------------------------------------------------------
# Auth
#-----------------------------------------------------------------------

class LoginView(TemplateView):
    """Dynamic login view for authentication forms."""

    def get_template_names(self):
        page = self.kwargs.get('page', 'login')
        return [f'{BASE}/pages/account/{page}.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

#-----------------------------------------------------------------------
# Error views
#-----------------------------------------------------------------------

def handler404(request, *args, **argv): #pylint: disable=unused-argument
    """Handle missing pages."""
    status_code = 404
    template = f'{BASE}/pages/general/errors/{status_code}.html'
    return render(request, template, {}, status=status_code)


def handler500(request, *args, **argv): #pylint: disable=unused-argument
    """Handle internal errors."""
    status_code = 500
    template = f'{BASE}/pages/general/errors/{status_code}.html'
    return render(request, template, {}, status=status_code)


def no_content(request, *args, **argv): #pylint: disable=unused-argument
    """Return an empty response when needed, such as for a ping."""
    return HttpResponse(status=204)
