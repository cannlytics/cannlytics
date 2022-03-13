"""
Laboratory Views | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/15/2021
Updated: 1/9/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports
import os

# External imports.
from django.views.generic import TemplateView

# Internal imports
from cannlytics.firebase import get_document, get_collection
from website.state import lab_state
from website.views.mixins import BaseMixin


FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestingView(BaseMixin, TemplateView):
    """Testing page."""

    def get_template_names(self):
        return ['website/pages/testing/testing.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credentials = get_document('admin/google')
        api_key = credentials['public_maps_api_key']
        context['api_key'] = [api_key]
        return context


class LabView(BaseMixin, TemplateView):
    """View for lab detail pages."""

    def get_template_names(self):
        return ['website/pages/testing/lab.html']

    def get_lab_data(self, context):
        """Get a lab's data from Firestore."""
        slug = self.kwargs.get('lab')
        filters = [{'key': 'slug', 'operation': '==', 'value': slug}]
        labs = get_collection('labs', filters=filters)
        if labs:
            context['lab'] = labs[0]
        else:
            context['lab'] = {}
        return context

    def get_context_data(self, **kwargs):
        """Get the context for a page."""
        context = super().get_context_data(**kwargs)
        context = self.get_lab_data(context)
        context['fields'] = lab_state['detail_fields']
        context['tabs'] = lab_state['tabs']
        return context


class NewLabView(BaseMixin, TemplateView):
    """View for adding a lab."""

    def get_template_names(self):
        return ['website/pages/testing/lab.html']

    def get_context_data(self, **kwargs):
        """Get the context for a page."""
        context = super().get_context_data(**kwargs)
        context['lab'] = {}
        context['fields'] = lab_state['detail_fields']
        context['tabs'] = lab_state['tabs'][:2]
        return context
