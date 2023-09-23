"""
Lab Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/30/2021
Updated: 12/31/2021
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with lab data, data about labs and data
that labs provide.
"""
# Standard imports
from datetime import datetime
import json
import re

# External imports
from django.template.defaultfilters import slugify
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth import auth
from cannlytics.firebase import (
    get_collection,
    get_document,
    update_document,
)

@api_view(['GET'])
def analyses_data(request, analysis_id=None):
    """Get data about lab test analyses (public API endpoint)."""
    data = []
    collection = 'public/data/analyses'
    if request.method == 'GET':

        # Get a specific observation.
        if analysis_id is not None:
            data = get_document(f'{collection}/{analysis_id}')

        # Otherwise query observations.
        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order_by', 'name')
            limit = request.query_params.get('limit')

            # Optional: Implement more queries the user can use.
            # Apply user-specified filters.
            # param = request.query_params.get('param')
            # if param:
            #     filters.append({'key': 'param', 'operation': '==', 'value': param})

            # Query and return the docs.
            data = get_collection(
                collection,
                desc=False,
                filters=filters,
                limit=limit,
                order_by=order_by,
            )

    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def analytes_data(request, analysis_id=None):
    """Get data about lab test analytes (public API endpoint)."""
    data = []
    collection = 'public/data/analyses'
    if request.method == 'GET':

        # Get a specific observation.
        if analysis_id is not None:
            data = get_document(f'{collection}/{analysis_id}')

        # Otherwise query observations.
        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order_by', 'name')
            limit = request.query_params.get('limit')

            # Optional: Implement more queries the user can use.
            # Apply user-specified filters.
            # param = request.query_params.get('param')
            # if param:
            #     filters.append({'key': 'param', 'operation': '==', 'value': param})

            # Query and return the docs.
            data = get_collection(
                collection,
                desc=False,
                filters=filters,
                limit=limit,
                order_by=order_by,
            )

    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def lab_data(request, license_number=None):
    """Get laboratory information (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Get a specific organization.
        organization_id = request.query_params.get('organization_id')
        if organization_id and organization_id != 'undefined':
            data = get_document(f'public/data/labs/{organization_id}')

        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order_by', 'name')
            limit = request.query_params.get('limit')
            state = request.query_params.get('state')
            # Optional: Implement more queries the user can use.
            # - name
            # - analyses?

            # Apply user-specified filters.
            if license_number:
                filters.append({'key': 'license', 'operation': '==', 'value': license_number})
            elif state:
                filters.append({'key': 'state', 'operation': '==', 'value': state})

            # Query and return the docs.
            data = get_collection(
                'public/data/labs',
                desc=False,
                filters=filters,
                limit=limit,
                order_by=order_by,
            )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET', 'POST'])
def lab_logs(request, org_id, format=None):
    """Get or create lab logs."""

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/logs')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create a log.
        return Response({'success': True, 'data': 'Under construction'}, content_type='application/json')


@api_view(['GET', 'POST'])
def lab_analyses(request, org_id, format=None):
    """
    Get or update (TODO) lab analyses.
    """

    if request.method == 'GET':
        data = get_collection(f'labs/{org_id}/analyses')
        return Response({ 'data': data}, content_type='application/json')

    elif request.method == 'POST':
        # TODO: Create an analysis.
        return Response({'success': True, 'data': 'Under construction'}, content_type='application/json')


def get_lab_results_filter():
    """Get any lab results filter."""
    raise NotImplementedError


# FIXME: Get these from `cannlytics.utils.constants`.
ANALYTES = [
    'cbc',
    'cbd',
    'cbda',
    'cbg',
    'cbga',
    'cbn',
    'delta_8_thc',
    'delta_9_thc',
    'thca',
    'thcv',
    'alpha_bisabolol',
    'alpha_pinene',
    'alpha_terpinene',
    'beta_caryophyllene',
    'beta_myrcene',
    'beta_pinene',
    'camphene',
    'carene',
    'caryophyllene_oxide',
    'd_limonene',
    'eucalyptol',
    'gamma_terpinene',
    'geraniol',
    'guaiol',
    'humulene',
    'isopulegol',
    'linalool',
    'nerolidol',
    'ocimene',
    'p_cymene',
    'terpinene',
    'terpinolene',
    'total_cannabinoids',
    'total_cbd',
    'total_cbg',
    'total_terpenes',
    'total_thc'
    'terpinenes',
]

OPERATIONS = {
    'ge': '>=',
    'le': '<=',
    'l': '<',
    'g': '>',
}


@api_view(['GET'])
def lab_results_data(request, strain_name=None):
    """Get lab results data (public API endpoint)."""
    data = []
    collection = 'public/data/lab_results'
    if request.method == 'GET':

        # FIXME: Search by metrc_id if passed as a parameter!

        # Get a specific observation.
        if strain_name is None:
            strain_name = request.query_params.get(
                'strain',
                request.query_params.get('strain_name'),
            )
        if strain_name is not None:
            strain_name = strain_name.replace('+', ' ')
            data = get_document(f'{collection}/{strain_name}')

        # Otherwise query observations.
        else:

            # Define query parameters.
            filters = []
            order_by = request.query_params.get('order', 'strain_name')
            desc = request.query_params.get('desc', False)
            limit = request.query_params.get('limit', None)
            if limit:
                limit = int(limit)

            # Allow user to specify whether to include all (default) or any.
            # FIXME: Currently any matches are returned, all matches would be nice.
            operation = 'array_contains_any'
            any = request.query_params.get('any')
            if any:
                operation = 'array_contains_any'

            # Allow user to query by effect or aroma.
            # Future work: Is there any way to query by effect AND aroma?
            effects = request.query_params.get('effects')
            aromas = request.query_params.get('aromas')
            if effects:
                outcomes = [f'effect_{x.replace(" ", "_").lower()}' for x in json.loads(effects)]
                filters.append({
                    'key': 'predicted_effects',
                    'operation': operation,
                    'value': outcomes,
                })
            elif aromas:
                outcomes = [f'aroma_{x.replace(" ", "_").lower()}' for x in json.loads(aromas)]
                filters.append({
                    'key': 'predicted_aromas',
                    'operation': operation,
                    'value': outcomes,
                })

            # Allow user to query by cannabinoid / terpene concentrations.
            # Handles open and closed ranges for a single analyte.
            # FIXME: This doesn't appear to work with 2 operations.
            for param in request.query_params:
                if param in ANALYTES:
                    order_by = param
                    desc = request.query_params.get('desc', True)
                    value = request.query_params[param]
                    ops = re.sub(r'\d.+', '', value).split('+')
                    values = [re.sub(r'[^0-9.]', '', x) for x in value.split('+')]
                    for i, op in enumerate(ops):
                        print(param, op, values[i])
                        filters.append({
                            'key': param,
                            'operation': OPERATIONS[op],
                            'value': float(values[i]),
                        })
                    break

            # Query and return the docs.
            data = get_collection(
                collection,
                desc=desc,
                filters=filters,
                limit=limit,
                order_by=order_by,
            )

    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)
