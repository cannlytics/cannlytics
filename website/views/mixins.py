"""
Mixins | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/30/2020
Updated: 12/24/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports
from datetime import datetime
from typing import Any

# External imports
from django.views.generic.base import ContextMixin
from cannlytics.auth.auth import authenticate_request

# Internal imports
from cannlytics.firebase import (
    get_collection,
    get_document,
    initialize_firebase,
    update_document,
)
from website.settings import PROJECT_NAME as BASE
from website.state import app_context, material, page_data, page_docs
from website.utils.utils import get_markdown


def get_page_context(kwargs: Any, context: dict) -> dict:
    """Get page-specific material.
    Args:
        kwargs (dict): A dictionary of keywords and their values.
        context (dict): A dictionary of existing page context.
    Returns
        (dict): The context updated with any page-specific state.
    """
    context['app'] = app_context
    parts = [('page', 'homepage'), ('section', ''), ('unit', '')]
    for part in parts:
        part_name = part[0]
        default = part[1]
        value = kwargs.get(part_name, default)
        context[part_name] = value
        try:
            page_material = material[value]
            key = value.replace('-', '_')
            context[key] = page_material
        except KeyError:
            continue
    return context


def get_page_data(context: dict) -> dict:
    """Get all data for a page from Firestore.
    Args:
        context (dict): A dictionary of existing page context.
    Returns
        (dict): The context updated with any page-specific data.
    """
    namespaces = []
    try:
        namespace = context['page']
        namespaces.append(page_data[namespace])
    except KeyError:
        pass
    try:
        namespace = context['section']
        namespaces.append(page_data[namespace])
    except KeyError:
        pass
    for namespace in namespaces:
        try:
            documents = namespace['documents']
            for item in documents:
                context[item['name']] = get_document(item['ref'])
        except KeyError:
            pass
        try:
            collections = namespace['collections']
            for item in collections:
                context[item['name']] = get_collection(
                    item['ref'],
                    limit=item.get('limit'),
                    order_by=item.get('order_by'),
                    desc=item.get('desc'),
                    filters=item.get('filters'),
                )
        except KeyError:
            pass
    return context


def get_page_docs(request: Any, context: dict) -> dict:
    """Get any text documents for a given page."""
    docs = page_docs.get(context['page'], []) + page_docs.get(context['section'], [])
    if docs:
        for doc in docs:
            name = doc.replace('-', '_').replace('/', '_')
            context = get_markdown(
                request,
                context,
                BASE,
                page=doc,
                name=name,
            )
    return context


def get_user_data(request: Any, context: dict) -> dict:
    """Get user-specific context.
    Args:
        request (HTTPRequest): A request to check for a user session.
        context (dict): Existing page context.
    Returns
        context (dict): Page context updated with any user-specific context.
    """
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        query = {'key': 'team', 'operation': 'array_contains', 'value': uid}
        organizations = get_collection('organizations', filters=[query])
        user_data = get_document(f'users/{uid}')
        context['organizations'] = organizations
        context['user'] = {**claims, **user_data}
    except KeyError:
        context['organizations'] = []
        context['user'] = {}
    return context


def save_analytics(request: Any, context: dict) -> dict:
    """Save page analytics to Firestore."""
    now = datetime.now().isoformat()
    date = now[:10]
    values = {
        'date': date,
        'time': now,
        'page': request.path,
        'query': request.GET.get('q'),
    }
    # Optional: Merge more user information and more elegantly.
    user = context['user']
    if user:
        values['email'] = user['email']
        values['uid'] = user['uid']
    ref = f'logs/website/page_visits/{now}'
    update_document(ref, values)


class BaseMixin(ContextMixin):
    """Base view used for most pages, where the URL is segmented as:
    ```
    https://{base}/{page}/{section}/{unit}/{part}/{piece}
    ```
    A number of page template paths are tried, trying to match a unit
    first, then section, then a page-section, finally a page.
    Page-sections and sections are also search for in a general folder.
    """

    def get_template_names(self):
        """Get templates for a view based on the URL."""
        page = self.kwargs.get('page', 'homepage')
        section = self.kwargs.get('section', '')
        unit = self.kwargs.get('unit', '')
        templates = [
            f'{BASE}/pages/{page}/{unit}.html',
            f'{BASE}/pages/{page}/{section}/{unit}.html',
            f'{BASE}/pages/{page}/{section}.html',
            f'{BASE}/pages/{page}/{page}-{section}.html',
            f'{BASE}/pages/{page}/{section}/{section}.html',
            f'{BASE}/pages/{page}/{page}.html',
            f'{BASE}/pages/misc/{page}/{page}-{section}.html',
            f'{BASE}/pages/misc/{page}/{section}.html',
            f'{BASE}/pages/general/{page}.html',
        ]
        return templates

    def get_context_data(self, **kwargs):
        """Get context that is used on all pages. The context is retrieved
        dynamically from the app's state. The user's permissions are verified
        on every request. User-specific context and data is returned depending
        on the page. Information about data models is provided to all pages."""
        context = super(BaseMixin, self).get_context_data(**kwargs)
        context = get_page_context(self.kwargs, context)
        initialize_firebase()
        context = get_user_data(self.request, context)
        context = get_page_data(context)
        save_analytics(self.request, context)
        return context
