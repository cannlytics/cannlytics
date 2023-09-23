"""
Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/30/2021
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with datasets.
"""
# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth import api_auth


@api_view(['GET', 'POST'])
def algorithm_nfts(request, state=None):

    # Get a specific algorithm or query open-source algorithms.
    if request.method == 'GET':

        params = request.query_params
        ref = 'public/algorithms/algorithm_nfts'

    # Publish an algorithm.
    if request.meth == 'POST':

        ref = 'public/algorithms/algorithm_nfts'


@api_view(['GET', 'POST'])
def data_nfts(request, state=None):

    # Get a specific data NFT or query open-source data NFT.
    if request.method == 'GET':

        params = request.query_params
        ref = 'public/data/data_nfts'

    # Publish a data NFT.
    if request.meth == 'POST':

        ref = 'public/data/data_nfts'


@api_view(['GET', 'POST'])
def data_base(request, state=None):
    """Get or update information about datasets."""

    # Authenticate the user.
    claims = api_auth.authenticate_request(request)
    uid = claims['uid']

    # TODO: Allow user to pass state as a parameter.

    if request.method == 'GET':

        org_id = ''
        ref = '/organizations/%s/areas'

        # TODO: If no organization is specified, get the user's
        # organizations and get all areas for all licenses.

        # IF the organization is specified, get all areas for all
        # licenses of the organization.

        # If the organization and license is specified, get all areas
        # for the given organization's license.

        # If a specific area ID is given, get only that area.

        # If a filter parameter is given, then return only the areas
        # that match the query.
        # limit = request.query_params.get('limit', None)
        # order_by = request.query_params.get('order_by', 'state')
        # data = get_collection(ref, order_by=order_by, limit=limit, filters=[])

        # Optional: If a user is using traceability, then is there any
        # need to get location data from the API, or is the data in
        # Firestore sufficient (given Firestore is syncing with Metrc).
        # Otherwise, initialize a Metrc client and get areas from Metrc.
        # traced_location = cultivator.get_locations(uid=cultivation_uid)

        # # Optional: Get any filters from dict(request.query_params)

        message = """You're in the right place to get rich cannabis data.
        
        Currently, you can get data from the following endpoints:
        
          - `/data/analyses`
          - `/data/regulations`
          - `/data/states`
          - `/data/strains`
        
        Please stay tuned for further documentation or get in touch with
        the Cannlytics Team.
        """
        return Response({'message': message}, content_type='application/json')

    elif request.method == 'POST':

        # TODO: Either create or update the area.

            # # Create a new location using: POST /locations/v1/create
            # cultivation_name = 'Medical Grow'
            # cultivation_original_name = 'medical_grow'
            # cultivator.create_locations([
            #     cultivation_original_name,
            #     'Harvest Location',
            #     'Plant Location',
            #     'Warehouse',
            # ])

            # # Get created location
            # cultivation= None
            # locations = track.get_locations(
            #     action='active',
            #     license_number=cultivator.license_number
            # )
            # for location in locations:
            #     if location.name == cultivation_original_name:
            #         cultivation = location

            # # Update the name of the location using: POST /locations/v1/update
            # cultivator.update_locations([cultivation.uid], [cultivation_name])

        return Response({'data': []})

    elif request.method == 'Delete':

        # TODO: Archive the area data and delete from Metrc.

        return Response({'data': []})
