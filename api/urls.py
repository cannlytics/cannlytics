"""
URLs | Cannlytics API
Created: 4/21/2021
Updated: 6/12/2021
Description: API URLs to interface with cannabis analytics.
"""

# External imports
from django.urls import include, path
from rest_framework import urlpatterns

# Internal imports
from api import views
from api.analyses import analyses
from api.areas import areas
from api.auth import auth
from api.contacts import contacts
from api.instruments import instruments
from api.inventory import inventory
from api.invoices import invoices
from api.organizations import organizations
from api.projects import projects
from api.results import results
from api.samples import samples
from api.transfers import transfers
from api.traceability import traceability
from api.users import users

app_name = 'api' # pylint: disable=invalid-name

urlpatterns = [
    path('', views.index, name='index'),
    path('analyses', include([
        path('', analyses.analyses),
        path('/<uuid:analysis_id>', analyses.analyses),
    ])),
    path('analytes', include([
        path('', analyses.analytes),
        path('/<uuid:analyte_id>', analyses.analytes),
    ])),
    # path('areas', inventory.areas),
    path('areas', include([
        path('', areas.areas),
        path('/<uuid:area_id>', areas.areas),
    ])),
    # path('batches', include([
    #     path('', views.index),
    #     path('/<uuid:batch_id>', views.index),
    # ])),
    path('contacts', include([
        path('', contacts.contacts),
        path('/<uuid:org_id>', contacts.contacts),
        path('/<uuid:org_id>/people', contacts.people),
        path('/<uuid:org_id>/people/<uuid:user_id>', contacts.people),
    ])),
    path('inventory', include([
        path('', inventory.inventory),
        path('/<uuid:inventory_id>', inventory.inventory),
    ])),
    path('instruments', include([
        path('', instruments.instruments),
        path('/<uuid:instruments_id>', instruments.instruments),
    ])),
    path('invoices', include([
        path('', invoices.invoices),
        path('/<uuid:invoice_id>', invoices.invoices),
    ])),
    path('projects', include([
        path('', projects.projects),
        path('/<uuid:project_id>', projects.projects),
    ])),
    path('users', include([
        path('', users.users),
        path('/<uuid:uid>', users.users),
        path('/<uuid:uid>/settings', users.users),
    ])),
    path('organizations', include([
        path('', organizations.organizations),
        path('/<org_id>', organizations.organizations),
        path('/<org_id>/settings', organizations.organizations),
        # TODO: Handle with post requests?
        # path('/<org_id>/join/', organizations.join_organization),
    ])),
    path('results', include([
        path('', results.results),
        path('/<uuid:result_id>', results.results),
    ])),
    path('samples', include([
        path('', samples.samples),
        path('/<uuid:sample_id>', samples.samples),
    ])),
    # path('tests', include([ # Alternatively measurements / calculations
    #     path('', tests.tests),
    #     path('/<uuid:test_id>', tests.tests),
    # ])),
    path('transfers', include([
        path('', transfers.transfers),
        path('/<uuid:transfer_id>', transfers.transfers),
    ])),
    path('traceability', include([
        path('/delete-license', traceability.delete_license),
        path('/employees', traceability.employees),
        path('/employees/<license_number>', traceability.employees),
        path('/items', traceability.items),
        path('/items/<item_id>', traceability.items),
        path('/lab-tests', traceability.lab_tests),
        path('/lab-tests/<test_id>', traceability.lab_tests),
        path('/locations', traceability.locations),
        path('/locations/<area_id>', traceability.locations),
        path('/packages', traceability.packages),
        path('/packages/<package_id>', traceability.packages),
        path('/strains', traceability.strains),
        path('/strains/<strain_id>', traceability.strains),
        path('/transfers', traceability.transfers),
        path('/transfers/<transfer_id>', traceability.transfers),
    ])),
    path('regulations', views.regulations),
    path('create-key', auth.create_api_key),
    path('delete-key', auth.delete_api_key),
    path('get-keys', auth.get_api_key_hmacs),
]
