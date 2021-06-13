"""
Traceability API Views | Cannlytics API
Created: 6/13/2021
Updated: 6/13/2021
Description: API to interface with the Metrc API.
"""

# External imports
import google.auth
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.firebase import (
    access_secret_version,
)
from cannlytics.traceability.metrc import authorize
from api.auth import auth #pylint: disable=import-error


@api_view(['GET'])
def employees(request):
    """Get employees for a given license number from the Metrc API.
    Args:
        request (HTTPRequest): A `djangorestframework` request.
    """

    # Authenticate the user.
    claims = auth.verify_session(request)
    if not claims:
        message = 'Authentication failed. Please use the console or provide a valid API key.'
        return Response({'error': True, 'message': message}, status=403)
    _, project_id = google.auth.default()
    license_number = request.query_params.get('name')

    # Optional: Figure out how to pre-initialize a Metrc client.

    # Get Vendor API key using secret manager.
    # TODO: Determine where to store project_id, secret_id, and version_id.
    vendor_api_key = access_secret_version(
        project_id=project_id,
        secret_id='metrc_vendor_api_key',
        version_id='1'
    )

    # TODO: Get user API key using secret manager.
    user_api_key = access_secret_version(
        project_id=project_id,
        secret_id=f'{license_number}_secret',
        version_id='1'
    )

    # Create a Metrc client.
    track = authorize(vendor_api_key, user_api_key)

    # Make a request to the Metrc API.
    data = track.get_employees(license_number=license_number)

    # Return the requested data.
    return Response(data, content_type='application/json')
