"""
Middleware | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/1/2021
Updated: 6/14/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from urllib.parse import quote
from django import http
from django import urls
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class AppendOrRemoveSlashMiddleware(MiddlewareMixin):
    """Like django's built in APPEND_SLASH functionality, but also works in
    reverse. Eg. will remove the slash if a slash-appended url won't resolve,
    but its non-slashed counterpart will.

    Additionally, if a 404 error is raised within a view for a non-slashed url,
    and APPEND_SLASH is True, and the slash-appended url resolves, the
    middleware will redirect. (The default APPEND_SLASH behavior only catches
    Resolver404, so wouldn't work in this case.)

    See gregbrown.co.nz/code/append-or-remove-slash/ for more information."""

    def process_request(self, request):
        """Returns a redirect if adding/removing a slash is appropriate. This
        works in the same way as the default APPEND_SLASH behavior but in
        either direction. First, check if the url is valid. If not, check if
        adding/removing the trailing slash helps. If the new url is valid, redirect to it.
        """
        urlconf = getattr(request, 'urlconf', None)
        if not _is_valid_path(request.path_info, urlconf):
            if request.path_info.endswith('/'):
                new_path = request.path_info[:-1]
            else:
                new_path = request.path_info + '/'
            if _is_valid_path(new_path, urlconf):
                return http.HttpResponsePermanentRedirect(
                    generate_url(request, new_path))

    def process_response(self, request, response):
        """If a 404 is raised within a view, try appending/removing the slash
        (based on the  setting) and redirecting if the new url is
        valid."""
        if response.status_code == 404:
            if not request.path_info.endswith('/') and settings.APPEND_SLASH:
                new_path = request.path_info + '/'
            elif request.path_info.endswith('/') and not settings.APPEND_SLASH:
                new_path = request.path_info[:-1]
            else:
                new_path = None
            if new_path:
                urlconf = getattr(request, 'urlconf', None)
                if _is_valid_path(new_path, urlconf):
                    return http.HttpResponsePermanentRedirect(
                        generate_url(request, new_path))
        return response


def generate_url(request, path):
    if request.get_host():
        new_url = "%s://%s%s" % (request.is_secure() and 'https' or 'http',
                                 request.get_host(),
                                 quote(path))
    else:
        new_url = quote(path)
    if request.GET:
        new_url += '?' + request.META['QUERY_STRING']
    return new_url


def _is_valid_path(path, urlconf=None):
    """
    Returns True if the given path resolves against the default URL resolver,
    False otherwise.
    """
    try:
        urls.resolve(path, urlconf)
        return True
    except urls.Resolver404:
        return False


def open_access_middleware(get_response):
    """Allow all requests to access the API."""
    def middleware(request):
        response = get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = '*'
        return response
    return middleware
