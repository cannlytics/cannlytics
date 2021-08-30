"""
Results Views | Cannlytics API
Created: 4/21/2021
Updated: 8/30/2021

API to interface with laboratory results and CoA templates.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authorize_user
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def results(request, result_id=None):
    """Get, create, or update laboratory results."""

    # Initialize.
    model_id = result_id
    model_type = 'results'
    model_type_singular = 'result'
    
    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, claims, org_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, org_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)

    # DELETE data.
    elif request.method == 'DELETE':
        success = delete_object(request, claims, model_id, model_type, model_type_singular, org_id)
        if not success:
            message = f'Your must be an owner or quality assurance to delete {model_type}.'
            return Response({'error': True, 'message': message}, status=403)
        return Response({'success': True, 'data': []}, status=200)


#------------------------------------------------------------------
# Results functional views
#------------------------------------------------------------------

# @api_view(['POST'])
# def generate_coas(request):
#     """Generate CoAs."""

#     # TODO: Get posted samples.
#         # - Get the results for each sample.
#         # - If not results, then
#             # - Get the measurements for each sample
#             # - Calculate results for each sample
    
#         # Get the template

#         # Create the PDF

#         # Generate download link for the PDF
#         # Optional: create short-link for the CoA.

#     # Return list of certificate data.
#     return NotImplementedError


@api_view(['POST'])
def calculate_results(request):
    """Receive incoming transfers."""
    return NotImplementedError


@api_view(['POST'])
def post_results(request):
    """Receive incoming transfers."""
    # # Record a lab test result using: POST /labtests/v1/record
    # test_package_data = {
    #     'Tag': test_package_tag,
    #     'Location': None,
    #     'Item': test_package.item['name'],
    #     'UnitOfWeight': 'Grams',
    #     # 'PatientLicenseNumber': 'X00001',
    #     'Note': 'Clean as a whistle.',
    #     'IsProductionBatch': False,
    #     'ProductionBatchNumber': None,
    #     'IsTradeSample': False,
    #     'IsDonation': False,
    #     'ProductRequiresRemediation': False,
    #     'RemediateProduct': False,
    #     'RemediationMethodId': None,
    #     'RemediationDate': None,
    #     'RemediationSteps': None,
    #     'ActualDate': today,
    #     'Ingredients': [
    #         {
    #             'HarvestId': 2,
    #             'HarvestName': None,
    #             'Weight': 100.23,
    #             'UnitOfWeight': 'Grams'
    #         },
    #     ]
    # }
    # track.create_harvest_testing_packages(test_package_data, license_number=cultivator.license_number)
    # packages = track.get_packages(license_number=cultivator.license_number)
    # lab_package = [0] # TODO: Get lab testing package

    # # Create the lab result record.
    # encoded_pdf = encode_pdf('../assets/pdfs/example_coa.pdf')
    # test_package_label =  'ABCDEF012345670000015141'
    # lab_result_data = {
    #     'Label': test_package_label,
    #     'ResultDate': get_timestamp(),
    #     # 'LabTestDocument': {
    #         # 'DocumentFileName': 'new-old-time-moonshine.pdf',
    #         # 'DocumentFileBase64': 'encoded_pdf',
    #     # },
    #     'Results': [
    #         {
    #             'LabTestTypeName': 'THC',
    #             'Quantity': 0.07,
    #             'Passed': True,
    #             'Notes': ''
    #         },
    #         {
    #             'LabTestTypeName': 'CBD',
    #             'Quantity': 23.33,
    #             'Passed': True,
    #             'Notes': ''
    #         },
    #         # {
    #         #     'LabTestTypeName': 'Microbiologicals',
    #         #     'Quantity': 0,
    #         #     'Passed': True,
    #         #     'Notes': ''
    #         # },
    #         # {
    #         #     'LabTestTypeName': 'Pesticides',
    #         #     'Quantity': 0,
    #         #     'Passed': True,
    #         #     'Notes': ''
    #         # },
    #         # {
    #         #     'LabTestTypeName': 'Heavy Metals',
    #         #     'Quantity': 0,
    #         #     'Passed': True,
    #         #     'Notes': ''
    #         # },
    #     ]
    # }
    # track.post_lab_results([lab_result_data], license_number=lab.license_number)

    # # Get tested package.
    # test_package = track.get_packages(label=test_package_label, license_number=lab.license_number)

    # # Get the tested package's lab result.
    # lab_results = track.get_lab_results(uid=test_package.id, license_number=lab.license_number)
    return NotImplementedError


@api_view(['POST'])
def release_results(request):
    """Receive incoming transfers."""
    return NotImplementedError


@api_view(['POST'])
def send_results(request):
    """Receive incoming transfers."""
    return NotImplementedError


#------------------------------------------------------------------
# Templates (draft)
#------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def templates(request, template_id=None):
    """Manage laboratory templates, such as for certificates of analysis."""

    # Initialize.
    model_id = template_id
    model_type = 'templates'
    model_type_singular = 'template'

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    if status != 200:
        return Response(claims, status=status)

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, claims, org_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, org_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)

    # DELETE data.
    elif request.method == 'DELETE':
        success = delete_object(request, claims, model_id, model_type, model_type_singular, org_id)
        if not success:
            message = f'Your must be an owner or quality assurance to delete {model_type}.'
            return Response({'error': True, 'message': message}, status=403)
        return Response({'success': True, 'data': []}, status=200)
