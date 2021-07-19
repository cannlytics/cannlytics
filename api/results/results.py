"""
Results Views | Cannlytics API
Created: 4/21/2021
Updated: 7/19/2021

API to interface with laboratory results.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authenticate_request
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def results(request, format=None, result_id=None):
    """Get, create, or update laboratory results."""

    # Initialize and authenticate.
    model_id = result_id
    model_type = 'results'
    model_type_singular = 'result'
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

    # Authorize that the user can work with the data.
    organization_id = request.query_params.get('organization_id')
    if organization_id not in authorized_ids:
        message = f'Your must be an owner, quality assurance, or a team member of this organization to manage {model_type}.'
        return Response({'error': True, 'message': message}, status=403)

    # GET data.
    if request.method == 'GET':
        docs = get_objects(request, authorized_ids, organization_id, model_id, model_type)
        return Response({'success': True, 'data': docs}, status=200)

    # POST data.
    elif request.method == 'POST':
        data = update_object(request, claims, model_type, model_type_singular, organization_id)
        if data:
            return Response({'success': True, 'data': data}, status=200)
        else:
            message = 'Data not recognized. Please post either a singular object or an array of objects.'
            return Response({'error': True, 'message': message}, status=400)

    # DELETE data.
    elif request.method == 'DELETE':
        success = delete_object(request, claims, model_id, model_type, model_type_singular, organization_id, owner, qa)
        if not success:
            message = f'Your must be an owner or quality assurance to delete {model_type}.'
            return Response({'error': True, 'message': message}, status=403)
        return Response({'success': True, 'data': []}, status=200)

    #------------------------------------------------------------------
    # Lab results ✓
    #------------------------------------------------------------------

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

