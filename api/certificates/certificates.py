"""
Certificates Views | Cannlytics API
Created: 7/19/2021
Updated: 8/9/2021

API to interface with certificates of analysis (CoAs).
"""
# pylint:disable=line-too-long

# External imports
from json import loads
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.results.results import calculate_results
from api.auth.auth import authorize_user, sha256_hmac, verify_user_pin
from api.api import get_objects, update_object, delete_object
from cannlytics.firebase import get_collection, get_document
from cannlytics.lims.certificates import generate_coas


DEFAULT_TEMPLATE = 'public/lims/templates/coa_template.xlsm'


@api_view(['POST'])
def create_coas(request):
    """Generate certificates of analysis."""

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # Require pin.
    error_response = verify_user_pin(request)
    print(error_response)
    if error_response.status_code != 200:
        return error_response

    # Get posted samples.
    posted_data = loads(request.body.decode('utf-8'))
    sample_ids = posted_data['sample_ids']

    # Create certificates for each sample.
    data = []
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
        
        # Get the certificate template.
        template_name = sample_data.get('coa_template_ref', DEFAULT_TEMPLATE)

        # FIXME:
        # Create the PDF, keeping the data.
        # Efficiency gain: Keep the template in /tmp so they don't have
        # to be downloaded each iteration.
        certificate = generate_coas(
            context,
            coa_template=template_name,
            # output_pages=pages,
            # limits=limits
        )
        data.append(certificate)

    # Return list of certificate data.
    return Response({'data': data}, status=200)


@api_view(['POST'])
def review_coas(request):
    """Review certificates of analysis so that they can be approved
    and released."""

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # Require pin.
    error_response = verify_user_pin(request)
    print(error_response)
    if error_response.status_code != 200:
        return error_response     

    # Call generate_coas
    # - Make sure to fill-in reviewers signature.
    
    # Update the sample's certificate_status.

    return NotImplementedError


@api_view(['POST'])
def approve_coas(request):
    """Approve certificates of analysis for release after they have
    been reviewed."""

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # Restrict approving certificates to QA and owners.
    qa = claims.get('qa', [])
    owner = claims.get('owner', [])
    if org_id not in owner and org_id not in qa:
        message = f'Your must be an owner or quality assurance manager of this organization for this operation.'
        return Response({'error': True, 'message': message}, status=403)

    # Require pin.
    uid = claims['uid']
    post_data = loads(request.body.decode('utf-8'))
    pin = post_data['pin']
    message = f'{pin}:{uid}'
    app_secret = get_document('admin/api')['app_secret_key']
    code = sha256_hmac(app_secret, message)
    verified_claims = get_document(f'admin/api/pin_hmacs/{code}')
    if not verified_claims:
        return JsonResponse({'error': True, 'message': 'Invalid pin.'})
    elif verified_claims.get('uid') != uid:
        return JsonResponse({'error': True, 'message': 'Invalid pin.'})  

    # Call generate_coas
    # - Make sure to fill-in approvers signature.
    
    # Update the sample's certificate_status.

    return NotImplementedError


@api_view(['POST'])
def post_coas(request):
    """Post certificates of analysis to the state traceability system."""

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # Restrict approving certificates to QA and owners.
    qa = claims.get('qa', [])
    owner = claims.get('owner', [])
    if org_id not in owner and org_id not in qa:
        message = f'Your must be an owner or quality assurance manager of this organization for this operation.'
        return Response({'error': True, 'message': message}, status=403)

    # Get sample IDs.
    posted_data = loads(request.body.decode('utf-8'))
    sample_ids = posted_data['sample_ids']

    # Format data for API requests.

    # Post certificates 1 by 1.

    return NotImplementedError


@api_view(['POST'])
def release_coas(request):
    """Release certificates of analysis to the client."""

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # Restrict approving certificates to QA and owners.
    qa = claims.get('qa', [])
    owner = claims.get('owner', [])
    if org_id not in owner and org_id not in qa:
        message = f'Your must be an owner or quality assurance manager of this organization for this operation.'
        return Response({'error': True, 'message': message}, status=403)

    # Get the samples.
    posted_data = loads(request.body.decode('utf-8'))
    sample_ids = posted_data['sample_ids']

    # Update the certificate_status in Firestore.
    

    # Send (email and/or text) to the client's recipients.

    return NotImplementedError
