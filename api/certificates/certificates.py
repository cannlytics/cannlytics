"""
Certificates Views | Cannlytics API
Created: 7/19/2021
Updated: 8/4/2021

API to interface with certificates of analysis (CoAs).
"""
# pylint:disable=line-too-long

# External imports
from json import loads
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.results.results import calculate_results
from api.auth.auth import authenticate_request
from api.api import get_objects, update_object, delete_object
from cannlytics.firebase import get_collection, get_document
from cannlytics.lims.certificates import generate_coas


@api_view(['POST'])
def create_coas(request):
    """Generate certificates of analysis."""

    # Authenticate the user.
    claims = authenticate_request(request)
    try:
        uid = claims['uid']
        owner = claims.get('owner', [])
        team = claims.get('team', [])
        qa = claims.get('qa', [])
        authorized_ids = owner + team + qa
    except KeyError:
        message = 'Your request was not authenticated. Ensure that you have a valid session or API key.'
        return Response({'error': True, 'message': message}, status=401)

    # Authorize that the user can work with the organization's data.
    org_id = request.query_params.get('organization_id')
    if org_id not in authorized_ids:
        message = f'Your must be an owner, quality assurance, or a team member of this organization for this operation.'
        return Response({'error': True, 'message': message}, status=403)

    # Get posted samples.
    posted_data = loads(request.body.decode('utf-8'))
    sample_ids = posted_data['samples']

    # Create certificates for each sample.
    certificates = []
    templates = {}
    for sample_id in sample_ids:

        # Get the sample data.
        sample_data = get_document(f'organizations/{org_id}/samples/{sample_id}')

        # Get the results for each sample. If there are no results,
        # then get the measurements for each sample and calculate
        # the results for each sample. Add a empty dictionary if missing everything.
        sample_results = get_collection(
            f'organization/{org_id}/results',
            order_by='updated_at',
            desc=True,
            filters=[
                {'key': 'sample_id', 'operation': '==', 'value': sample_id}
            ]
        )
        if not sample_results:
            sample_results = calculate_results(request)
            if not sample_results:
                sample_results = [{}]
        
        # Define the certificate context.
        context = {**sample_data, **sample_results[0]}
        
        # Get the template
        template_name = sample_data.get('coa_template_ref', 'public/lims/templates/coa_template.xlsm')

        # Create the PDF
        certificate = generate_coas(
            context,
            coa_template=template_name,
            # output_pages=pages,
            # limits=limits
        )

        # Generate download link for the PDF
        # Optional: create short-link for the CoA.

    # Return list of certificate data.
    return NotImplementedError


@api_view(['POST'])
def review_coas(request):
    """Review certificates of analysis."""
    return NotImplementedError


@api_view(['POST'])
def approve_coas(request):
    """Approve certificates of analysis."""
    return NotImplementedError
