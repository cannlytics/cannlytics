"""
State Data Endpoints | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/9/2022
Updated: 7/10/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API endpoints to interface with datasets.
"""
# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import (
    get_collection,
    get_document,
)


@api_view(['GET'])
def state_data(request, state=None):
    """Get or update data for a given state."""

    # TODO: Get national statistics (as a timeseries).

    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)


# Future work: state_data_co


@api_view(['GET'])
def state_data_ct(request, state=None):
    """Get data for Connecticut."""
    
    # TODO: Get Licensees
    # Filter licensees by approved, pending, under-review

    # Optional: Get sales: flower, oil, vape, beverage, edible, preroll

    # Optional: Get prices: flower, oil, vape, beverage, edible, preroll

    # Optional: Get plants

    
    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)


@api_view(['GET'])
def state_data_ma(request, state=None):
    """Get data for Massachusetts."""
    
    # TODO: Get Licensees
    # Filter licensees by approved, pending, under-review

    # TODO: Get sales: flower, oil, vape, beverage, edible, preroll

    # TODO: Get prices: flower, oil, vape, beverage, edible, preroll

    # TODO: Get plants

    
    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)


@api_view(['GET'])
def state_data_ok(request, state=None):
    """Get data for Oklahoma."""
    
    # TODO: Get Licensees
    # Filter licensees by approved, pending, under-review

    # Optional: Get sales: flower, oil, vape, beverage, edible, preroll

    # Optional: Get prices: flower, oil, vape, beverage, edible, preroll

    # Optional: Get plants

    
    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)


# Future work: state_data_or


@api_view(['GET'])
def state_data_or(request, state=None):
    """Get data for Oregon."""
    
    # TODO: Get Licensees
    # Filter licensees by approved, pending, under-review

    # Optional: Get sales: flower, oil, vape, beverage, edible, preroll

    # Optional: Get prices: flower, oil, vape, beverage, edible, preroll

    # Optional: Get plants

    
    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)


@api_view(['GET'])
def state_data_wa(request, state=None):
    """Get data for Washington."""
    
    # TODO: Get Licensees
    # Filter licensees by approved, pending, under-review

    # Optional: Get sales: flower, oil, vape, beverage, edible, preroll

    # Optional: Get prices: flower, oil, vape, beverage, edible, preroll

    # Optional: Get plants

    
    if state:
        data = get_document(f'public/data/state_data/{state}')
    else:
        data = get_collection('public/data/state_data', order_by='state')
    response = {'success': True, 'message': '', 'data': data}
    return Response(response)
