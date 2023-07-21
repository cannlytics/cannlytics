"""
CCRS Data Endpoints | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/19/2022
Updated: 4/20/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with CCRS data and statistics.
"""
# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import get_collection


@api_view(['GET'])
def lab_results(request, license_number=None):
    """Get CCRS lab results (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/lab_results',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def licensees(request, license_number=None):
    """Get CCRS licensees (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/licensees',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def areas(request, license_number=None):
    """Get CCRS areas (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/areas',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def contacts(request, license_number=None):
    """Get CCRS contacts (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/contacts',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def integrators(request, license_number=None):
    """Get CCRS integrators (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/integrators',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def inventory(request, license_number=None):
    """Get CCRS inventory (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/inventory',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def inventory_adjustments(request, license_number=None):
    """Get CCRS inventory adjustments (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/inventory_adjustments',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def plants(request, license_number=None):
    """Get CCRS inventory adjustments (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/plants',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def plant_destructions(request, license_number=None):
    """Get CCRS plant destructions (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/plant_destructions',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def products(request, license_number=None):
    """Get CCRS products (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/products',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def sale_headers(request, license_number=None):
    """Get CCRS sale headers (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/sale_headers',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def sale_details(request, license_number=None):
    """Get CCRS sale details (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/sale_details',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def strains(request, license_number=None):
    """Get CCRS strains (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/strains',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET'])
def transfers(request, license_number=None):
    """Get CCRS transfers (public API endpoint)."""
    data = []
    if request.method == 'GET':

        # Optional: Implement API key.
        # claims = authenticate_request(request)
        # if claims.get('user') is None:
        #     message = 'Failure to authenticate with the credentials provided.'
        #     message += claims['message']
        #     return {'success': False, 'data': None, 'message': message}, 401

        # Define query parameters.
        filters = []
        order_by = request.query_params.get('order_by')
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
        # Optional: Implement more queries the user can use.
        # - name
        # - analyses?

        # Query and return the docs.
        data = get_collection(
            'data/ccrs/transfers',
            desc=False,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

    # Return data in a response.
    response = {'success': True, 'data': data}
    return Response(response, status=200)
