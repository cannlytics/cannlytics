"""
URLs | Cannlytics API
Created: 4/21/2021
Updated: 4/25/2021
Description: API URLs to interface with cannabis analytics.
"""

# External imports
from django.urls import include, path
from rest_framework import urlpatterns
from rest_framework.urlpatterns import format_suffix_patterns

# Internal imports
from cannlytics_api import views
from cannlytics_api.auth import auth
from cannlytics_api.areas import areas
from cannlytics_api.inventory import inventory
from cannlytics_api.organizations import organizations
from cannlytics_api.users import users

app_name = 'cannlytics_api' # pylint: disable=invalid-name

urlpatterns = [
    path('', views.index, name='index'),
    path('auth', include([
        path('/authenticate', auth.authenticate),
        path('/sign-out', auth.logout),
    ])),
    # Allow for labs to choose to make their analyses public,
    # so that producers can search for analyses.
    path('analyses', include([
        path('', views.index),
        path('/<uuid:analysis_id>', views.index),
    ])),
    path('analytes', include([
        path('', views.index),
        path('/<uuid:analyte_id>', views.index),
    ])),
    # path('areas', inventory.areas),
    path('areas', include([
        path('', areas.areas),
        path('/<uuid:area_id>', areas.areas),
    ])),
    path('clients', include([
        path('', views.index),
        path('/<uuid:org_id>', views.index),
        path('/<uuid:org_id>/contacts', views.index),
    ])),
    path('inventory', include([
        path('', views.index),
        path('/<uuid:inventory_id>', views.index),
    ])),
    path('instruments', include([
        path('', views.index),
        path('/<uuid:instruments_id>', views.index),
    ])),
    path('invoices', include([
        path('', views.index),
        path('/<uuid:invoice_id>', views.index),
    ])),
    path('users', include([
        path('', users.users),
        path('/<uuid:uid>', users.users),
        path('/<uuid:uid>/settings', users.users),
    ])),
    path('organizations', include([
        path('', organizations.organizations),
        path('/<org_id>', organizations.organizations),
        path('/<uuid:org_id>/settings', organizations.organizations),
        # path('join/', organizations.join_organization),
    ])),
    path('samples', include([
        path('', views.index),
        path('/<uuid:sample_id>', views.index),
    ])),
    path('results', include([
        path('', views.index),
        path('/<uuid:sample_id>', views.index),
    ])),
    path('transfers', include([
        path('', views.index),
        path('/<uuid:sample_id>', views.index),
    ])),
    path('regulations', views.regulations),
    path('create-key', auth.create_api_key),
    path('delete-key', auth.delete_api_key),
    path('get-keys', auth.get_api_key_hmacs),
]

# Add optional format suffixes to the URLs,
# so users can explicitely specify a formatm e.g. .json.
# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# urlpatterns = format_suffix_patterns(urlpatterns)
