"""
Main Views | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 12/16/2021
License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
"""
# External imports.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView

# Internal imports.
from cannlytics.auth.auth import authenticate_request
from console.settings import PROJECT_NAME as BASE
from console.views.context_helpers import (
    get_data_models,
    get_organization_data_models,
    get_page_context,
    get_page_data,
    get_user_data,
    save_analytics,
)


class ConsoleView(TemplateView):
    """Main view used for most console pages."""

    login_url = '/account/sign-in'
    redirect_field_name = 'redirect_to'

    def get_template_names(self):
        """Get the screen's template based on the URL path, where the URL is
        segmented as: `https://{base}/{screen}/{section}/{unit}/{part}/{piece}`.
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
            f'{BASE}/pages/{screen}/{section}.html',
            f'{BASE}/pages/{screen}/{screen}-{section}.html',
            f'{BASE}/pages/{screen}/{section}/{section}.html',
            f'{BASE}/pages/{screen}/{screen}.html',
            f'{BASE}/pages/misc/{screen}/{screen}-{section}.html',
            f'{BASE}/pages/misc/{screen}/{section}.html',
        ]

    def get_context_data(self, **kwargs):
        """Get context that is used on all pages. The context is retrieved
        dynamically from the app's state. The user's permissions are verified
        on every request. User-specific context and data is returned depending
        on the page. Information about data models is provided to all pages."""
        context = super().get_context_data(**kwargs)        
        context = get_data_models(context)
        context = get_page_context(self.kwargs, context)
        context = get_user_data(self.request, context)
        context = get_organization_data_models(context)
        context = get_page_data(context)
        save_analytics(self.request, context)
        return context

    def get(self, request, screen=None, section=None, unit=None, part=None, piece=None): #pylint: disable=too-many-arguments,arguments-differ,unused-argument
        """Ensure that there is a user session, otherwise
        navigate to the sign-in page."""
        if screen != 'account':
            claims = authenticate_request(request)
            if not claims:
                return HttpResponseRedirect('/account/sign-in')
        return super(ConsoleView, self).get(request)


def handler404(request, *args, **argv): #pylint: disable=unused-argument
    """Handle missing pages."""
    template = f'{BASE}/pages/misc/errors/404.html'
    return render(request, template, {}, status=404)


def handler500(request, *args, **argv): #pylint: disable=unused-argument
    """Handle internal errors."""
    template = f'{BASE}/pages/misc/errors/500.html'
    return render(request, template, {}, status=500)


def no_content(request, *args, **argv): #pylint: disable=unused-argument
    """Return an empty response when needed, such as for a ping."""
    return HttpResponse(status=204)
