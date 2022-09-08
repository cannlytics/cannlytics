"""
URLs | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 9/8/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API URLs to interface with cannabis analytics.
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
import api.traceability

# Administrative API imports.
from api.organizations import organizations
from api.users import users
from api.settings import settings


app_name = 'api' # pylint: disable=invalid-name

urlpatterns = [

    # Base API endpoint.
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

    # Organization API endpoints.
    path('organizations', include([
        path('/<organization_id>', organizations.organizations),
        path('/<organization_id>/settings', organizations.organizations),
        path('/<organization_id>/team', organizations.organization_team),
        path('/<organization_id>/team/<user_id>', organizations.organization_team),
        path('/<organization_id>/join', organizations.join_organization),
    ])),

    # User API Endpoints
    path('users', include([
        path('', users.users),
        path('/<user_id>', users.users),
        path('/<user_id>/settings', users.users),
    ])),

    # Data API endpoints.
    path('data', include([

        # Base data endpoint.
        path('', api.data.data.datasets),

        # Analyses data API endpoints.
        path('/analyses', api.data.lab_analyses_data.analyses_data),
        path('/analyses/<analysis_id', api.data.lab_analyses_data.analyses_data),
        path('/analytes', api.data.lab_analyses_data.analytes_data),
        path('/analytes/<analyte_id', api.data.lab_analyses_data.analytes_data),

        # COA data and parser API endpoints.
        path('/coas', api.data.coa_data.coa_data),
        path('/coas/download', api.data.coa_data.download_coa_data),

        # Labs data API endpoints.
        path('labs', include([
            path('', api.data.lab_data.lab_data),
            path('/<license_number>', api.data.lab_data.lab_data),
            path('/<license_number>/analyses', api.data.lab_data.lab_analyses),
            path('/<license_number>/logs', api.data.lab_data.lab_logs),
        ])),

        # TODO: Licensee data - Get data about specific licenses.

        # Optional: Datasets data - Allow users to find available datasets.

        # CCRS data endpoints.
        # TODO: Re-design CCRS endpoints around timeseries statistics.
        # path('/ccrs/areas', ccrs_data.areas),
        # path('/ccrs/contacts', ccrs_data.contacts),
        # path('/ccrs/integrators', ccrs_data.integrators),
        # path('/ccrs/inventory', ccrs_data.inventory),
        # path('/ccrs/inventory_adjustments', ccrs_data.inventory_adjustments),
        # path('/ccrs/plants', ccrs_data.plants),
        # path('/ccrs/plant_destructions', ccrs_data.plant_destructions),
        # path('/ccrs/products', ccrs_data.products),
        # path('/ccrs/lab_results', ccrs_data.lab_results),
        # path('/ccrs/licensees', ccrs_data.licensees),
        # path('/ccrs/sale_headers', ccrs_data.sale_headers),
        # path('/ccrs/sale_details', ccrs_data.sale_details),
        # path('/ccrs/strains', ccrs_data.strains),
        # path('/ccrs/transfers', ccrs_data.transfers),

        # Regulation data API endpoints.
        path('/regulations', api.data.regulation_data),
        path('/regulations/<state>', api.data.regulation_data.regulation_data),

        # State data API endpoints.
        # TODO: Dynamically route states.
        # path('/state/<state>', state_data),
        path('/states', api.data.state_data.state_data),
        path('/states/ct', api.data.state_data.state_data_ct),
        path('/states/ma', api.data.state_data.state_data_ma),
        path('/states/ok', api.data.state_data.state_data_ok),
        path('/states/or', api.data.state_data.state_data_or),
        path('/states/wa', api.data.state_data.state_data_wa),

        # Strain data API endpoints.
        path('/strains', include([
            path('', api.data.strain_data.strain_data),
            path('/<strain_name>', api.data.strain_data.strain_data),
        ])),

        # TODO: Implement patents data endpoints.
        # path('/patents', include([
        #     path('', patent_data.patent_data),
        #     path('/<patent_number>', patent_data.patent_data),
        # ])),

    ])),

    # Stats endpoints.
    path('stats', include([
        path('', api.stats.effects_stats.effects_stats),
        path('/effects', api.stats.effects_stats.effects_stats),
        path('/effects/actual', api.stats.effects_stats.record_effects),
        path('/effects/<strain>', api.stats.effects_stats),
        path('/personality', api.stats.personality_stats.personality_stats),
        path('/recommendations', api.stats.recommendation_stats.recommendation_stats),
        path('/patents', api.stats.patent_stats.patent_stats),
    ])),

    # LIMS API endpoints.
    path('lims', include([
        path('analyses', include([
            path('', api.lims.analyses.analyses),
            path('/<analysis_id>', api.lims.analyses.analyses),
        ])),
        path('analytes', include([
            path('', api.lims.analytes.analytes),
            path('/<analyte_id>', api.lims.analytes.analytes),
        ])),
        path('areas', include([
            path('', api.lims.areas.areas),
            path('/<area_id>', api.lims.areas.areas),
        ])),
        path('certificates', include([
            path('/generate', api.lims.certificates.generate_coas),
            path('/review', api.lims.certificates.review_coas),
            path('/approve', api.lims.certificates.approve_coas),
            path('/post', api.lims.certificates.post_coas),
            path('/release', api.lims.certificates.release_coas),
        ])),
        path('contacts', include([
            path('', api.lims.contacts.contacts),
            path('/<contact_id>', api.lims.contacts.contacts),
        ])),
        path('people', include([
            path('', api.lims.contacts.people),
            path('/<person_id>', api.lims.contacts.people),
        ])),
        path('inventory', include([
            path('', api.lims.inventory.inventory),
            path('/<inventory_id>', api.lims.inventory.inventory),
        ])),
        path('instruments', include([
            path('', api.lims.instruments.instruments),
            path('/<instrument_id>', api.lims.instruments.instruments),
        ])),
        path('invoices', include([
            path('', api.lims.invoices.invoices),
            path('/<invoice_id>', api.lims.invoices.invoices),
        ])),
        path('measurements', include([
            path('', api.lims.measurements.measurements),
            path('/<measurement_id>', api.lims.measurements.measurements),
        ])),
        path('projects', include([
            path('', api.lims.projects.projects),
            path('/<project_id>', api.lims.projects.projects),
        ])),
        path('results', include([
            path('', api.lims.results.results),
            path('/<result_id>', api.lims.results.results),
            path('/calculate', api.lims.results.calculate_results),
            path('/post', api.lims.results.post_results),
            path('/release', api.lims.results.release_results),
            path('/send', api.lims.results.send_results),
        ])),
        path('samples', include([
            path('', api.lims.samples.samples),
            path('/<sample_id>', api.lims.samples.samples),
        ])),
        path('templates', include([
            path('', api.lims.results.templates),
            path('/<template_id>', api.lims.results.templates),
        ])),
        path('transfers', include([
            path('', api.lims.transfers.transfers),
            path('/<transfer_id>', api.lims.transfers.transfers),
            path('/receive', api.lims.transfers.receive_transfers),
        ])),
        path('transporters', include([
            path('', api.lims.transfers.transporters),
            path('/<transporter_id>', api.lims.transfers.transporters),
        ])),
        path('vehicles', include([
            path('', api.lims.transfers.vehicles),
            path('/<vehicle_id>', api.lims.transfers.vehicles),
        ])),
        path('waste', include([
            path('', api.lims.waste.waste),
            path('/<waste_item_id>', api.lims.waste.waste),
        ])),
    ])),

    # Traceability API endpoints.
    # TODO: Implement remaining Metrc endpoints.
    path('traceability', include([
        path('/delete-license', api.traceability.traceability.delete_license),
        path('/employees', api.traceability.traceability.employees),
        path('/employees/<license_number>', api.traceability.traceability.employees),
        path('/items', api.traceability.traceability.items),
        path('/items/<item_id>', api.traceability.traceability.items),
        path('/lab-tests', api.traceability.traceability.lab_tests),
        path('/lab-tests/<test_id>', api.traceability.traceability.lab_tests),
        path('/locations', api.traceability.traceability.locations),
        path('/locations/<area_id>', api.traceability.traceability.locations),
        path('/packages', api.traceability.traceability.packages),
        path('/packages/<package_id>', api.traceability.traceability.packages),
        path('/strains', api.traceability.traceability.strains),
        path('/strains/<strain_id>', api.traceability.traceability.strains),
        path('/transfers', api.traceability.traceability.transfers),
        path('/transfers/<transfer_id>', api.traceability.traceability.transfers),
    ])),

    # Logs API Endpoints.
    path('logs', include([
        path('', settings.logs),
        path('/<log_id>', settings.logs),
    ])),
]
