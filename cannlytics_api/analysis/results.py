"""
Results Views | Cannlytics API
Created: 4/21/2021

API to interface with laboratory results.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def results(request, format=None):
    """Get, create, or update laboratory results."""

    if request.method == 'GET':
        return Response({'error': 'not_implemented'}, content_type='application/json')

    elif request.method == 'POST':

        return Response({'error': 'not_implemented'}, content_type='application/json')

        # Return an error if no author is specified.
        # error_message = 'Unknown error, please notify <support@cannlytics.com>'
        # return Response(
        #     {'error': error_message},
        #     content_type='application/json',
        #     status=status.HTTP_400_BAD_REQUEST
        # )

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

