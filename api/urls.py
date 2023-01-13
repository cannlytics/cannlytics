"""
URLs | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 1/13/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API URLs to interface with cannabis data and analytics.
"""
# External imports.
from django.urls import include, path
from rest_framework import urlpatterns #pylint: disable=unused-import

# Core API imports.
from api.auth import auth
from api.base import base

# Functional API imports.
import api.data
import api.lims
import api.stats
import api.metrc

# Administrative API imports.
from api.organizations import organizations
from api.users import users
from api.settings import settings


app_name = 'api' # pylint: disable=invalid-name

urlpatterns = [

    # Base API endpoint for users to discover an index of endpoints.
    path('', base.index, name='index'),

    # Authentication API endpoints.
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

    # Data API endpoints.
    path('data', include([

        # Base data API endpoint for users to find available datasets.
        path('', api.data.data_base),

        # Analyses and analytes data API endpoints.
        path('/analyses', api.data.analyses_data),
        path('/analyses/<analysis_id', api.data.analyses_data),
        path('/analytes', api.data.analytes_data),
        path('/analytes/<analyte_id', api.data.analytes_data),

        # COA data and parser API endpoints.
        path('/coas', api.data.coa_data),
        path('/coas/download', api.data.download_coa_data),

        # Labs data API endpoints.
        path('labs', include([
            path('', api.data.lab_data),
            path('/<license_number>', api.data.lab_data),
            path('/<license_number>/analyses', api.data.lab_analyses),
            path('/<license_number>/logs', api.data.lab_logs),
        ])),

        # License data.
        path('/licenses', include([
            path('', api.data.license_data),
            path('/<license_number>', api.data.license_data),
        ])),

        # CCRS data endpoints.
        # FIXME: Re-design CCRS endpoints around timeseries statistics.
        # path('ccrs', include([
        #     path('/areas', ccrs_data.areas),
        #     path('/contacts', ccrs_data.contacts),
        #     path('/integrators', ccrs_data.integrators),
        #     path('/inventory', ccrs_data.inventory),
        #     path('/inventory_adjustments', ccrs_data.inventory_adjustments),
        #     path('/plants', ccrs_data.plants),
        #     path('/plant_destructions', ccrs_data.plant_destructions),
        #     path('/products', ccrs_data.products),
        #     path('/lab_results', ccrs_data.lab_results),
        #     path('/licensees', ccrs_data.licensees),
        #     path('/sale_headers', ccrs_data.sale_headers),
        #     path('/sale_details', ccrs_data.sale_details),
        #     path('/strains', ccrs_data.strains),
        #     path('/transfers', ccrs_data.transfers),
        # ])),

        # Lab result data API endpoints.
        path('/results', include([
            path('', api.data.strain_data),
            path('/<lab_result_id>', api.data.strain_data),
        ])),

        # Strain data API endpoints.
        path('/strains', include([
            path('', api.data.strain_data),
            path('/<strain_name>', api.data.strain_data),
        ])),

        # Regulation data API endpoints.
        path('/regulations', api.data.regulation_data),
        path('/regulations/<state>', api.data.regulation_data),

        # State data API endpoints.
        path('/states', api.data.state_data),
        path('/states/<state>', api.data.state_data),

    ])),

    # Stats endpoints.
    path('stats', include([
        path('', api.stats.effects_stats),
        path('/effects', api.stats.effects_stats),
        path('/effects/actual', api.stats.record_effects),
        path('/effects/<strain>', api.stats.effects_stats),
        path('/personality', api.stats.personality_stats),
        path('/recommendations', api.stats.recommendation_stats),
        path('/patents', api.stats.patent_stats),
        # TODO: Flower Art API endpoint.
    ])),

    # LIMS API endpoints.
    path('lims', include([
        path('analyses', include([
            path('', api.lims.analyses),
            path('/<analysis_id>', api.lims.analyses),
        ])),
        path('analytes', include([
            path('', api.lims.analytes),
            path('/<analyte_id>', api.lims.analytes),
        ])),
        path('areas', include([
            path('', api.lims.areas),
            path('/<area_id>', api.lims.areas),
        ])),
        path('certificates', include([
            path('/generate', api.lims.generate_coas),
            path('/review', api.lims.review_coas),
            path('/approve', api.lims.approve_coas),
            path('/post', api.lims.post_coas),
            path('/release', api.lims.release_coas),
        ])),
        path('contacts', include([
            path('', api.lims.contacts),
            path('/<contact_id>', api.lims.contacts),
        ])),
        path('people', include([
            path('', api.lims.people),
            path('/<person_id>', api.lims.people),
        ])),
        path('inventory', include([
            path('', api.lims.inventory),
            path('/<inventory_id>', api.lims.inventory),
        ])),
        path('instruments', include([
            path('', api.lims.instruments),
            path('/<instrument_id>', api.lims.instruments),
        ])),
        path('invoices', include([
            path('', api.lims.invoices),
            path('/<invoice_id>', api.lims.invoices),
        ])),
        path('measurements', include([
            path('', api.lims.measurements),
            path('/<measurement_id>', api.lims.measurements),
        ])),
        path('projects', include([
            path('', api.lims.projects),
            path('/<project_id>', api.lims.projects),
        ])),
        path('results', include([
            path('', api.lims.results),
            path('/<result_id>', api.lims.results),
            path('/calculate', api.lims.calculate_results),
            path('/post', api.lims.post_results),
            path('/release', api.lims.release_results),
            path('/send', api.lims.send_results),
        ])),
        path('samples', include([
            path('', api.lims.samples),
            path('/<sample_id>', api.lims.samples),
        ])),
        path('templates', include([
            path('', api.lims.templates),
            path('/<template_id>', api.lims.templates),
        ])),
        path('transfers', include([
            path('', api.lims.transfers),
            path('/<transfer_id>', api.lims.transfers),
            path('/receive', api.lims.receive_transfers),
        ])),
        path('transporters', include([
            path('', api.lims.transporters),
            path('/<transporter_id>', api.lims.transporters),
        ])),
        path('vehicles', include([
            path('', api.lims.vehicles),
            path('/<vehicle_id>', api.lims.vehicles),
        ])),
        path('waste', include([
            path('', api.lims.waste),
            path('/<waste_item_id>', api.lims.waste),
        ])),
    ])),

    # Metrc API endpoints.
    path('metrc', include([
        path('/admin/delete-license', api.metrc.delete_license),
        path('/batches/<batch_id>', api.metrc.batches),
        path('/deliveries/<delivery_id>', api.metrc.deliveries),
        path('/employees', api.metrc.employees),
        path('/employees/<license_number>', api.metrc.employees),
        path('/facilities/<license_number>', api.metrc.facilities),
        path('/harvests/<harvest_id>', api.metrc.harvests),
        path('/items', api.metrc.items),
        path('/items/<item_id>', api.metrc.items),
        path('/locations', api.metrc.locations),
        path('/locations/<area_id>', api.metrc.locations),
        path('/packages', api.metrc.packages),
        path('/packages/<package_id>', api.metrc.packages),
        path('/patients/<patient_id>', api.metrc.patients),
        path('/plants/<plant_id>', api.metrc.plants),
        path('/results', api.metrc.lab_tests),
        path('/results/<test_id>', api.metrc.lab_tests),
        path('/sales/<sale_id>', api.metrc.sales),
        path('/strains', api.metrc.strains),
        path('/strains/<strain_id>', api.metrc.strains),
        path('/transfers', api.metrc.transfers),
        path('/transfers/<transfer_id>', api.metrc.transfers),
        # TODO: Implement remaining Metrc endpoints:
        # - additives
        # - categories
        # - customer types
        # - Test statuses
        # - Test types
        # - transfers/templates
        # - transaction?
        # - units of measure
        # - waste
    ])),

    # Organization API endpoints.
    path('organizations', include([
        path('/<organization_id>', organizations.organizations),
        path('/<organization_id>/settings', organizations.organizations),
        path('/<organization_id>/team', organizations.organization_team),
        path('/<organization_id>/team/<user_id>', organizations.organization_team),
        path('/<organization_id>/join', organizations.join_organization),
    ])),

    # User API Endpoints.
    path('users', include([
        path('', users.users),
        path('/<user_id>', users.users),
        path('/<user_id>/about', users.users),
        path('/<user_id>/consumption', users.users),
        path('/<user_id>/spending', users.users),
        path('/<user_id>/logs', include([
            path('', settings.logs),
            path('/<log_id>', settings.logs),
        ])),
        path('/<user_id>/settings', users.users),
    ])),
]
