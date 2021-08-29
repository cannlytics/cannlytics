"""
URLs | Cannlytics API
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 4/21/2021
Updated: 7/19/2021
Description: API URLs to interface with cannabis analytics.
"""

# External imports
from django.urls import include, path
from rest_framework import urlpatterns

# Internal imports
from api import views
from api.analytics import analytics
from api.analyses import analyses
from api.analytes import analytes
from api.areas import areas
from api.auth import auth
from api.certificates import certificates
from api.contacts import contacts
from api.data import data
from api.instruments import instruments
from api.inventory import inventory
from api.invoices import invoices
from api.measurements import measurements
from api.organizations import organizations
from api.projects import projects
from api.results import results
from api.samples import samples
from api.settings import settings
from api.transfers import transfers
from api.traceability import traceability
from api.users import users

app_name = 'api' # pylint: disable=invalid-name

urlpatterns = [
    path('', views.index, name='index'),
    path('analytics', include([
        path('', analytics.analytics),
    ])),
    path('analyses', include([
        path('', analyses.analyses),
        path('/<analysis_id>', analyses.analyses),
    ])),
    path('analytes', include([
        path('', analytes.analytes),
        path('/<analyte_id>', analytes.analytes),
    ])),
    path('areas', include([
        path('', areas.areas),
        path('/<area_id>', areas.areas),
    ])),
    path('certificates', include([
        path('/generate', certificates.generate_coas),
        path('/review', certificates.review_coas),
        path('/approve', certificates.approve_coas),
        path('/post', certificates.post_coas),
        path('/release', certificates.release_coas),
    ])),
    path('contacts', include([
        path('', contacts.contacts),
        path('/<contact_id>', contacts.contacts),
    ])),
    # path('data', include([
    #     path('', data.datasets),
    #     path('/<state>', data.datasets),
    # ])),
    path('people', include([
        path('', contacts.people),
        path('/<person_id>', contacts.people),
    ])),
    path('inventory', include([
        path('', inventory.inventory),
        path('/<inventory_id>', inventory.inventory),
    ])),
    path('instruments', include([
        path('', instruments.instruments),
        path('/<instrument_id>', instruments.instruments),
    ])),
    path('invoices', include([
        path('', invoices.invoices),
        path('/<invoice_id>', invoices.invoices),
    ])),
    path('logs', include([
        path('', settings.logs),
        path('/<log_id>', settings.logs),
    ])),
    path('measurements', include([
        path('', measurements.measurements),
        path('/<measurement_id>', measurements.measurements),
    ])),
    path('projects', include([
        path('', projects.projects),
        path('/<project_id>', projects.projects),
    ])),
    path('users', include([
        path('', users.users),
        path('/<user_id>', users.users),
        path('/<user_id>/settings', users.users),
    ])),
    path('organizations', include([
        path('', organizations.organizations),
        path('/labs', organizations.labs),
        path('/<organization_id>', organizations.organizations),
        path('/<organization_id>/settings', organizations.organizations),
        path('/<organization_id>/team', organizations.organization_team),
        path('/<organization_id>/team/<user_id>', organizations.organization_team),
        path('/<organization_id>/join', organizations.join_organization),
    ])),
    path('results', include([
        path('', results.results),
        path('/<result_id>', results.results),
        path('/calculate', results.calculate_results),
        path('/post', results.post_results),
        path('/release', results.release_results),
        path('/send', results.send_results),
    ])),
    path('samples', include([
        path('', samples.samples),
        path('/<sample_id>', samples.samples),
    ])),
    path('templates', include([
        path('', results.templates),
        path('/<template_id>', results.templates),
    ])),
    path('transfers', include([
        path('', transfers.transfers),
        path('/<transfer_id>', transfers.transfers),
        path('/receive', transfers.receive_transfers),
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
    # path('data', include([
    #     path('/regulations', views.regulations),
    # ])),
    path('auth', include([
        path('/create-key', auth.create_api_key),
        path('/create-pin', auth.create_user_pin),
        path('/create-signature', auth.create_signature),
        path('/delete-key', auth.delete_api_key),
        path('/delete-pin', auth.delete_user_pin),
        path('/delete-signature', auth.delete_signature),
        path('/get-keys', auth.get_api_key_hmacs),
        path('/get-signature', auth.get_signature),
        path('/verify-pin', auth.verify_user_pin),
    ])),
]
