"""
URLs | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 7/28/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API URLs to interface with cannabis data and analytics.
"""
# External imports.
from django.urls import include, path
from rest_framework import urlpatterns #pylint: disable=unused-import

# Core API imports.
from api.auth import api_auth
from api.base import api_base

# Functional API imports.
import api.ai
# import api.data
# import api.lims
# import api.stats
import api.metrc

# Administrative API imports.
from api.organizations import api_organizations
from api.users import api_users
from api.settings import api_settings


app_name = 'api' # pylint: disable=invalid-name

urlpatterns = [

    # Base API endpoint for users to discover an index of endpoints.
    path('', api_base.index, name='index'),

    # Authentication API endpoints.
    path('auth', include([
        path('/create-key', api_auth.create_api_key),
        path('/delete-key', api_auth.delete_api_key),
        path('/get-keys', api_auth.get_api_key_hmacs),
    ])),

    # AI API endpoints.
    path('ai', include([

        # Base AI API endpoint for users to find available AI tools.
        path('', api.ai.ai_base),

        # Recipes AI.
        path('/recipes', api.ai.recipes_api),
        path('/recipes/<recipe_id>', api.ai.recipes_api),

        # AI utilities.
        path('/color', api.ai.text_to_color_api),
        path('/emoji', api.ai.text_to_emoji_api),

        # Strain AI utilities: art, description, and name identification.
        # path('/strains', api.data.api_data_strains),
        # path('/strains/<strain_id>', api.data.api_data_strains),

    ])),

    # Data API endpoints.
    path('data', include([

        # Base data API endpoint for users to find available datasets.
        # path('', api.data.data_base),

        # Analyses and analytes data API endpoints.
        # path('/analyses', api.data.analyses_data),
        # path('/analyses/<analysis_id', api.data.analyses_data),
        # path('/analytes', api.data.analytes_data),
        # path('/analytes/<analyte_id', api.data.analytes_data),

        # COA data and parser API endpoints.
        # path('/coas', api.data.api_data_coas),
        # path('/coas/download', api.data.download_coa_data),
        # path('/coas/<coa_id>', api.data.api_data_coas),

        # Receipt data API endpoints.
        # path('/receipts', api.data.api_data_receipts),
        # path('/receipts/download', api.data.download_receipts_data),
        # path('/receipts/<receipt_id>', api.data.api_data_receipts),

        # Labs data API endpoints.
        # path('labs', include([
        #     path('', api.data.lab_data),
        #     path('/<license_number>', api.data.lab_data),
        #     path('/<license_number>/analyses', api.data.lab_analyses),
        #     path('/<license_number>/logs', api.data.lab_logs),
        # ])),

        # # License data.
        # path('/licenses', include([
        #     path('', api.data.api_data_licenses),
        #     path('/<license_number>', api.data.api_data_licenses),
        # ])),

        # # Lab result data API endpoints.
        # path('/results', include([
        #     path('', api.data.strain_data),
        #     path('/<lab_result_id>', api.data.strain_data),
        # ])),

        # # Strain data API endpoints.
        # path('/strains', include([
        #     path('', api.data.strain_data),
        #     path('/<strain_name>', api.data.strain_data),
        # ])),

        # # Regulation data API endpoints.
        # path('/regulations', api.data.regulation_data),
        # path('/regulations/<state>', api.data.regulation_data),

        # Patent data.
        # path('/patents', api.stats.patent_stats),

    ])),

    # # Stats endpoints.
    # path('stats', include([
    #     path('', api.stats.effects_stats),
    #     path('/effects', api.stats.effects_stats),
    #     path('/effects/actual', api.stats.record_effects),
    #     path('/effects/<strain>', api.stats.effects_stats),
    # TODO: Make the personality test cannabis related!
    #     path('/personality', api.stats.personality_stats),
    #     path('/recommendations', api.stats.recommendation_stats),
    #     # TODO: Flower Art API endpoint.
    # ])),

    # Metrc API endpoints.
    path('metrc', include([
        path('/admin/add-key', api.metrc.add_metrc_user_api_key),
        path('/admin/delete-key', api.metrc.delete_metrc_user_api_key),
        path('/batches', api.metrc.batches),
        path('/batches/<batch_id>', api.metrc.batches),
        path('/deliveries', api.metrc.deliveries),
        path('/deliveries/<delivery_id>', api.metrc.deliveries),
        path('/employees', api.metrc.employees),
        path('/employees/<employee_id>', api.metrc.employees),
        path('/facilities', api.metrc.facilities),
        path('/facilities/<facility_id>', api.metrc.facilities),
        path('/harvests', api.metrc.harvests),
        path('/harvests/<harvest_id>', api.metrc.harvests),
        path('/items', api.metrc.items),
        path('/items/<item_id>', api.metrc.items),
        path('/locations', api.metrc.locations),
        path('/locations/<area_id>', api.metrc.locations),
        path('/packages', api.metrc.packages),
        path('/packages/<package_id>', api.metrc.packages),
        path('/patients', api.metrc.patients),
        path('/patients/<patient_id>', api.metrc.patients),
        path('/plants', api.metrc.plants),
        path('/plants/<plant_id>', api.metrc.plants),
        path('/tests', api.metrc.lab_tests),
        path('/tests/<test_id>', api.metrc.lab_tests),
        path('/tests/<test_id>/<coa_id>', api.metrc.lab_tests),
        path('/sales', api.metrc.sales),
        path('/sales/<sale_id>', api.metrc.sales),
        path('/transactions', api.metrc.transactions),
        path('/transactions/<start>', api.metrc.transactions),
        path('/transactions/<start>/<end>', api.metrc.transactions),
        path('/strains', api.metrc.strains),
        path('/strains/<strain_id>', api.metrc.strains),
        path('/transfers/templates', api.metrc.transfer_templates),
        path('/transfers/templates/<template_id>', api.metrc.transfer_templates),
        path('/transfers', api.metrc.transfers),
        path('/transfers/<transfer_id>', api.metrc.transfers),
        path('/drivers/<driver_id>', api.metrc.drivers),
        path('/vehicles/<vehicle_id>', api.metrc.vehicles),
        path('/types', include([
            path('/additives', api.metrc.additive_types),
            path('/adjustments', api.metrc.adjustment_reasons),
            path('/batches', api.metrc.batch_types),
            path('/categories', api.metrc.categories),
            path('/customers', api.metrc.customer_types),
            path('/locations', api.metrc.location_types),
            path('/growth-phases', api.metrc.growth_phases),
            path('/packages', api.metrc.package_types),
            path('/package-statuses', api.metrc.package_statuses),
            path('/return-reasons', api.metrc.return_reasons),
            path('/test-statuses', api.metrc.test_statuses),
            path('/tests', api.metrc.test_types),
            path('/transfers', api.metrc.transfer_types),
            path('/units', api.metrc.units),
            path('/waste', api.metrc.waste_types),
            path('/waste-methods', api.metrc.waste_methods),
            path('/waste-reasons', api.metrc.waste_reasons),
        ])),
    ])),

    # Organization API endpoints.
    path('organizations', include([
        path('', api_organizations.organizations),
        path('/<organization_id>', api_organizations.organizations),
        path('/<organization_id>/settings', api_organizations.organizations),
        path('/<organization_id>/team', api_organizations.organization_team),
        path('/<organization_id>/team/<user_id>', api_organizations.organization_team),
        path('/<organization_id>/join', api_organizations.join_organization),
    ])),

    # User API Endpoints.
    path('users', include([
        path('', api_users.users),
        path('/<user_id>', api_users.users),
        path('/<user_id>/about', api_users.users),
        path('/<user_id>/consumption', api_users.users),
        path('/<user_id>/spending', api_users.users),
        path('/<user_id>/logs', include([
            path('', api_settings.logs),
            path('/<log_id>', api_settings.logs),
        ])),
        path('/<user_id>/settings', api_users.users),
    ])),

    # # LIMS API endpoints.
    # path('lims', include([
    #     path('analyses', include([
    #         path('', api.lims.analyses),
    #         path('/<analysis_id>', api.lims.analyses),
    #     ])),
    #     path('analytes', include([
    #         path('', api.lims.analytes),
    #         path('/<analyte_id>', api.lims.analytes),
    #     ])),
    #     path('areas', include([
    #         path('', api.lims.areas),
    #         path('/<area_id>', api.lims.areas),
    #     ])),
    #     path('certificates', include([
    #         path('/generate', api.lims.generate_coas),
    #         path('/review', api.lims.review_coas),
    #         path('/approve', api.lims.approve_coas),
    #         path('/post', api.lims.post_coas),
    #         path('/release', api.lims.release_coas),
    #     ])),
    #     path('contacts', include([
    #         path('', api.lims.contacts),
    #         path('/<contact_id>', api.lims.contacts),
    #     ])),
    #     path('people', include([
    #         path('', api.lims.people),
    #         path('/<person_id>', api.lims.people),
    #     ])),
    #     path('inventory', include([
    #         path('', api.lims.inventory),
    #         path('/<inventory_id>', api.lims.inventory),
    #     ])),
    #     path('instruments', include([
    #         path('', api.lims.instruments),
    #         path('/<instrument_id>', api.lims.instruments),
    #     ])),
    #     path('invoices', include([
    #         path('', api.lims.invoices),
    #         path('/<invoice_id>', api.lims.invoices),
    #     ])),
    #     path('measurements', include([
    #         path('', api.lims.measurements),
    #         path('/<measurement_id>', api.lims.measurements),
    #     ])),
    #     path('projects', include([
    #         path('', api.lims.projects),
    #         path('/<project_id>', api.lims.projects),
    #     ])),
    #     path('results', include([
    #         path('', api.lims.results),
    #         path('/<result_id>', api.lims.results),
    #         path('/calculate', api.lims.calculate_results),
    #         path('/post', api.lims.post_results),
    #         path('/release', api.lims.release_results),
    #         path('/send', api.lims.send_results),
    #     ])),
    #     path('samples', include([
    #         path('', api.lims.samples),
    #         path('/<sample_id>', api.lims.samples),
    #     ])),
    #     path('templates', include([
    #         path('', api.lims.templates),
    #         path('/<template_id>', api.lims.templates),
    #     ])),
    #     path('transfers', include([
    #         path('', api.lims.transfers),
    #         path('/<transfer_id>', api.lims.transfers),
    #         path('/receive', api.lims.receive_transfers),
    #     ])),
    #     path('transporters', include([
    #         path('', api.lims.transporters),
    #         path('/<transporter_id>', api.lims.transporters),
    #     ])),
    #     path('vehicles', include([
    #         path('', api.lims.vehicles),
    #         path('/<vehicle_id>', api.lims.vehicles),
    #     ])),
    #     path('waste', include([
    #         path('', api.lims.waste),
    #         path('/<waste_item_id>', api.lims.waste),
    #     ])),
    # ])),
]
