"""
Areas Endpoints | Cannlytics API
Created: 5/8/2021
Updated: 5/8/2021

API endpoints to interface with areas.
"""

# External imports
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics_api.auth import authenticate_request


@api_view(['GET', 'POST'])
def areas(request, format=None):
    """Get or update information about a areas / locations."""

    if request.method == 'GET':

        # TODO: Authenticate the user
        user = authenticate_request(request)
        print('User:', user)

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
        
        return Response([{'make': "Subaru", 'model': "WRX", 'price': 21000}])
    
    elif request.method == 'POST':

        # TODO: Either create or update the area.

            # # Create a new location using: POST /locations/v1/create
            # cultivation_name = 'MediGrow'
            # cultivation_original_name = 'medi grow'
            # cultivator.create_locations([
            #     cultivation_original_name,
            #     'Harvest Location',
            #     'Plant Location',
            #     'Warehouse',
            # ])
            
            # # Get created location
            # cultivation= None
            # locations = track.get_locations(action='active', license_number=cultivator.license_number)
            # for location in locations:
            #     if location.name == cultivation_original_name:
            #         cultivation = location

            # # Update the name of the location using: POST /locations/v1/update
            # cultivator.update_locations([cultivation.uid], [cultivation_name])

        return Response({'data': []})

    elif request.method == 'Delete':

        # TODO: Archive the area data and delete from Metrc.

        return Response({'data': []})