"""
Main Views | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 12/29/2020
Updated: 11/15/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# External imports
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

# Internal imports
from website.views.mixins import BaseMixin, get_page_docs


class GeneralView(BaseMixin, TemplateView):
    """Generic view for most pages."""

    def get_context_data(self, **kwargs):
        """Get the context for a page."""
        context = super().get_context_data(**kwargs)
        context = get_page_docs(self.request, context)
        return context


def handler404(request, *args, **argv): #pylint: disable=unused-argument
    """Handle missing pages."""
    template = 'website/pages/general/errors/404.html'
    return render(request, template, {}, status=404)


def handler500(request, *args, **argv): #pylint: disable=unused-argument
    """Handle internal errors."""
    template = 'website/pages/general/errors/500.html'
    return render(request, template, {}, status=500)

def meetup(request): #pylint: disable=unused-argument
    """Redirect the user to the Cannabis Data Science meetup."""
    return HttpResponseRedirect('https://meet.google.com/ifq-jtmc-nuh')
