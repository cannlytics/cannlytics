"""
Results Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 12/6/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory results and CoA templates.
"""
# External imports.
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports.
from api.api import get, post, delete, handle_request

ACTIONS = {
    'GET': get,
    'POST': post,
    'DELETE': delete,
}


@api_view(['GET', 'POST', 'DELETE'])
def results(request: Response, result_id: str = '') -> Response:
    """Get, create, or update laboratory results."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='results',
        model_type_singular='result',
        model_id=result_id,
    )
    return Response(response, status=status_code)


#------------------------------------------------------------------
# Results functional views
#------------------------------------------------------------------

@api_view(['POST'])
def calculate_results(request):
    """Receive incoming transfers."""
    # TODO: Implement result calculation through the API logic.
    return NotImplementedError


@api_view(['POST'])
def post_results(request):
    """Receive incoming transfers."""
    # TODO: Implement post result through the API logic.
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
    # test_package_label =  'your-package-label'
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
    # TODO: Implement release results through the API logic.
    return NotImplementedError


@api_view(['POST'])
def send_results(request):
    """Receive incoming transfers."""
    # TODO: Implement send results through the API logic.
    return NotImplementedError


#------------------------------------------------------------------
# Templates
#------------------------------------------------------------------

@api_view(['GET', 'POST', 'DELETE'])
def templates(request: Response, template_id: str = '') -> Response:
    """Get, create, or update laboratory templates,
    such as for certificates of analysis."""
    response, status_code = handle_request(
        request,
        actions=ACTIONS,
        model_type='templates',
        model_type_singular='template',
        model_id=template_id,
    )
    return Response(response, status=status_code)
