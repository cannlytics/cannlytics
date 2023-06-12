"""
License Data Endpoints | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2022
Updated: 6/9/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    API endpoints to interface with cannabis license data.

"""
# External imports:
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports:
from cannlytics.firebase import get_collection


# TODO: Make obsolete by re-uploading the data.
import math
def replace_nan_with_none(data):
    for dict_item in data:
        for key, value in dict_item.items():
            if isinstance(value, float) and math.isnan(value):
                dict_item[key] = None
    return data


@api_view(['GET'])
def api_data_licenses(request, license_number=None):
    """Get data about cannabis licenses. You can query by `license_number`,
    `type`, or `name`, which searches both the business legal name
    and the business dba name. You can also filter by `zipcode` or
    `county`. You can also sort by `order_by` and limit the number of
    results with `limit`.
    Query parameters:
        * order_by
        * limit
        * license_number
        * type
        * name
        * county
        * zipcode
    """
    data = []
    collection = 'data/licenses/%s'
    if request.method == 'GET':

        # Define query parameters.
        order_by = request.query_params.get('order_by', 'business_dba_name')
        desc = request.query_params.get('desc', False)
        limit = request.query_params.get('limit', 100)
        license_type = request.query_params.get('type')
        license_number = request.query_params.get('license_number', license_number)
        name = request.query_params.get('name')
        premise_state = request.query_params.get('state')
        premise_zip_code = request.query_params.get('zipcode')
        premise_county = request.query_params.get('county')

        # Restrict the number of results.
        # TODO: Allow paid users to get more results.
        if limit > 1000:
            limit = 1000

        # Define query parameters.
        kwargs = {
            'desc': desc,
            'filters': [],
            'limit': limit,
            'order_by': order_by,
        }

        # Specify the Firestore collection.
        if premise_state:
            collection = collection % premise_state.lower()
        else:
            collection = collection % 'all'

        # Get a specific license.
        if license_number:
            kwargs['order_by'] = None
            kwargs['filters'].append({'key': 'license_number', 'operation': '==', 'value': license_number})

        # Search licenses by name.
        elif name:

            # Try to get licenses by their business legal name.
            kwargs['filters'] = [{'key': 'business_dba_name', 'operation': '==', 'value': name}]
            data = get_collection(collection, **kwargs)

            # Also try to get licenses by their business dba name.
            kwargs['filters'] = [{'key': 'business_legal_name', 'operation': '==', 'value': name}]
            data.extend(get_collection(collection, **kwargs))

            # Remove duplicates.
            data = list({x['id']: x for x in data}.values())

        # Apply license type filter.
        elif license_type:
            kwargs['filters'].append({'key': 'license_type', 'operation': '==', 'value': license_type})

        # Apply zip code or county filters.
        if premise_zip_code:
            kwargs['order_by'] = None
            kwargs['filters'].append({'key': 'premise_zip_code', 'operation': '==', 'value': premise_zip_code})
        elif premise_county:
            kwargs['order_by'] = None
            kwargs['filters'].append({'key': 'premise_county', 'operation': '==', 'value': premise_county})

        # Query and return the docs.
        if not data:
            data = get_collection(collection, **kwargs)

    # Return the data.
    data = replace_nan_with_none(data)
    response = {'success': True, 'data': data}
    return Response(response, status=200)
