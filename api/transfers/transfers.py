"""
Transfers Views | Cannlytics API
Created: 4/21/2021
Updated: 9/4/2021

API to interface with laboratory transfers, transporters, and vehicles.
"""
# pylint:disable=line-too-long

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from api.auth.auth import authorize_user
from api.api import get_objects, update_object, delete_object


@api_view(['GET', 'POST', 'DELETE'])
def transfers(request, transfer_id=None):
    """Get, create, or update transfers."""

    # Initialize.
    model_id = transfer_id
    model_type = 'transfers'
    model_type_singular = 'transfer'

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
        # TODO:
        # 1. Send transfer to the receiving organization.
        print('\n-------------------')
        
        print('-------------------\n')
            # - Populate the transfer data in the receiving organization's transfers
            # ensuring that no existing transfer is overwritten.
        # 2. Notify the receiving organization.
        # 3. Optional: Post transfer to Metrc if user has traceability set up.
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


@api_view(['POST'])
def receive_transfers(request):
    """Receive incoming transfers."""
    return NotImplementedError


@api_view(['GET', 'POST', 'DELETE'])
def transporters(request, transporter_id=None):
    """Get, create, or update transporters."""

    # Initialize.
    model_id = transporter_id
    model_type = 'transporters'
    model_type_singular = 'transporter'

    # Authenticate the user.
    claims, status, org_id = authorize_user(request)
    print(claims)
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


@api_view(['GET', 'POST', 'DELETE'])
def vehicles(request, vehicle_id=None):
    """Get, create, or update vehicles."""

    # Initialize.
    model_id = vehicle_id
    model_type = 'vehicles'
    model_type_singular = 'vehicle'

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


#-----------------------------------------------------------------------
# Draft functionality
#-----------------------------------------------------------------------

    # Get licensed courier.
    # courier = track.get_employees(license_number=lab.license_number)[0]

    # # Create a testing package
    # test_package_tag = 'YOUR_TEST_PACKAGE_TAG'
    # test_package_data = {
    #     'Tag': test_package_tag,
    #     'Location': 'Warehouse',
    #     'Item': 'New Old-Time Moonshine Teenth',
    #     'Quantity': 4.0,
    #     'UnitOfMeasure': 'Grams',
    #     'Note': 'Quality assurance test sample.',
    #     'ActualDate': today,
    #     'Ingredients': [
    #         {
    #             'Package': 'ABCDEF012345670000013677',
    #             'Quantity': 4.0,
    #             'UnitOfMeasure': 'Grams'
    #         }
    #     ]
    # }
    # track.create_packages(
    #     [test_package_data],
    #     license_number=cultivator.license_number,
    #     qa=True
    # )

    # # Get the tested package.
    # test_package = track.get_packages(label=test_package_tag, license_number=cultivator.license_number)

    # # Step 1a Set up an external Incoming transfer
    # # using: POST/transfers/v1/external/incoming
    # transfer_data = {
    #     'ShipperLicenseNumber': cultivator.license_number,
    #     'ShipperName': cultivator.name,
    #     'ShipperMainPhoneNumber': '18005555555',
    #     'ShipperAddress1': 'Mulberry Street',
    #     'ShipperAddress2': None,
    #     'ShipperAddressCity': 'Oklahoma City',
    #     'ShipperAddressState': 'OK',
    #     'ShipperAddressPostalCode': '123',
    #     'TransporterFacilityLicenseNumber': lab.license['number'],
    #     # 'DriverOccupationalLicenseNumber': grower.license['number'],
    #     # 'DriverName': grower.full_name,
    #     # 'DriverLicenseNumber': 'xyz',
    #     # 'PhoneNumberForQuestions': '18005555555',
    #     # 'VehicleMake': 'xyz',
    #     # 'VehicleModel': 'xyz',
    #     # 'VehicleLicensePlateNumber': 'xyz',
    #     'Destinations': [
    #         {
    #             'RecipientLicenseNumber': lab.license_number,
    #             'TransferTypeName': 'Lab Sample Transfer',
    #             'PlannedRoute': 'Hypertube.',
    #             'EstimatedDepartureDateTime': get_timestamp(),
    #             'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
    #             'GrossWeight': 4,
    #             # 'GrossUnitOfWeightId': None,
    #             'Transporters': [
    #                 {
    #                     'TransporterFacilityLicenseNumber': lab.license_number,
    #                     'DriverOccupationalLicenseNumber': courier.license['number'],
    #                     'DriverName': courier.full_name,
    #                     'DriverLicenseNumber': 'xyz',
    #                     'PhoneNumberForQuestions': '18005555555',
    #                     'VehicleMake': 'xyz',
    #                     'VehicleModel': 'xyz',
    #                     'VehicleLicensePlateNumber': 'xyz',
    #                     # 'IsLayover': False,
    #                     'EstimatedDepartureDateTime': get_timestamp(),
    #                     'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
    #                     # 'TransporterDetails': None
    #                 }
    #             ],
    #             'Packages': [
    #                 {
    #                     # 'PackageLabel': traced_package.label,
    #                     # 'HarvestName': '2nd New Old-Time Moonshine Harvest',
    #                     'ItemName': 'New Old-Time Moonshine Teenth',
    #                     'Quantity': 1,
    #                     'UnitOfMeasureName': 'Each',
    #                     'PackagedDate': get_timestamp(),
    #                     'GrossWeight': 4.0,
    #                     'GrossUnitOfWeightName': 'Grams',
    #                     'WholesalePrice': None,
    #                     # 'Source': '2nd New Old-Time Moonshine Harvest',
    #                 },
    #             ]
    #         }
    #     ]
    # }
    # track.create_transfers(
    #     [transfer_data],
    #     license_number=cultivator.license_number,
    # )


    # # Step 1b Set up another external Incoming transfer
    # # using: POST/transfers/v1/external/incoming
    # second_transfer_data = {
    #     'ShipperLicenseNumber': cultivator.license_number,
    #     'ShipperName': cultivator.name,
    #     'ShipperMainPhoneNumber': '18005555555',
    #     'ShipperAddress1': 'Mulberry Street',
    #     'ShipperAddress2': None,
    #     'ShipperAddressCity': 'Oklahoma City',
    #     'ShipperAddressState': 'OK',
    #     'ShipperAddressPostalCode': '123',
    #     'TransporterFacilityLicenseNumber': cultivator.license['number'],
    #     'DriverOccupationalLicenseNumber': courier.license['number'],
    #     'DriverName': courier.full_name,
    #     'DriverLicenseNumber': 'xyz',
    #     'PhoneNumberForQuestions': '18005555555',
    #     'VehicleMake': 'xyz',
    #     'VehicleModel': 'xyz',
    #     'VehicleLicensePlateNumber': 'xyz',
    #     'Destinations': [
    #         {
    #             'RecipientLicenseNumber': cultivator.license_number,
    #             'TransferTypeName': 'Beginning Inventory Transfer',
    #             'PlannedRoute': 'Hypertube.',
    #             'EstimatedDepartureDateTime': get_timestamp(),
    #             'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
    #             'GrossWeight': 56,
    #             # 'GrossUnitOfWeightId': null,
    #             'Transporters': [
    #                 {
    #                     'TransporterFacilityLicenseNumber': cultivator.license_number,
    #                     'DriverOccupationalLicenseNumber': courier.license['number'],
    #                     'DriverName': courier.full_name,
    #                     'DriverLicenseNumber': 'xyz',
    #                     'PhoneNumberForQuestions': '18005555555',
    #                     'VehicleMake': 'xyz',
    #                     'VehicleModel': 'xyz',
    #                     'VehicleLicensePlateNumber': 'xyz',
    #                     # 'IsLayover': false,
    #                     'EstimatedDepartureDateTime': get_timestamp(),
    #                     'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
    #                     # 'TransporterDetails': null
    #                 }
    #             ],
    #             'Packages': [
    #                 {
    #                     # 'PackageLabel': traced_package.label,
    #                     # 'HarvestName': '2nd New Old-Time Moonshine Harvest',
    #                     'ItemName': 'New Old-Time Moonshine Teenth',
    #                     'Quantity': 2,
    #                     'UnitOfMeasureName': 'Ounces',
    #                     'PackagedDate': get_timestamp(),
    #                     'GrossWeight': 56.0,
    #                     'GrossUnitOfWeightName': 'Grams',
    #                     'WholesalePrice': 720,
    #                     # 'Source': '2nd New Old-Time Moonshine Harvest',
    #                 },
    #             ]
    #         }
    #     ]
    # }
    # track.create_transfers(
    #     [second_transfer_data],
    #     license_number=cultivator.license_number,
    # )

    # # Step 2 Find the two Transfers created in Step 1a and 1b
    # # by using the date search: GET/transfers/v1/incoming
    # traced_transfers = track.get_transfers(
    #     license_number=cultivator.license_number,
    #     start=today,
    #     end=get_timestamp()
    # )

    # # Step 3 Update one of the Transfers created in Step 1 by
    # # using: PUT/transfers/v1/external/incoming
    # second_transfer_data['TransferId'] = traced_transfers[0].id
    # second_transfer_data['Destinations'][0]['Packages'][0]['Quantity'] = 3
    # track.update_transfers(
    #     [second_transfer_data],
    #     license_number=cultivator.license_number,
    # )

    # updated_transfer = track.get_transfers(
    #     # uid=second_transfer_data['TransferId'],
    #     license_number=cultivator.license_number,
    #     start=get_timestamp(past=15),
    #     end=get_timestamp()
    # )

    # #------------------------------------------------------------------
    # # Transfer templates ✓
    # #------------------------------------------------------------------

    # # Step 1a Set up a Template using: POST/transfers/v1/templates
    # template_data = {
    #     'Name': 'HyperLoop Template',
    #     'TransporterFacilityLicenseNumber': cultivator.license_number,
    #     'DriverOccupationalLicenseNumber': courier.license['number'],
    #     'DriverName': courier.full_name,
    #     # 'DriverLicenseNumber': None,
    #     # 'PhoneNumberForQuestions': None,
    #     # 'VehicleMake': None,
    #     # 'VehicleModel': None,
    #     # 'VehicleLicensePlateNumber': None,
    #     'Destinations': [
    #         {
    #             'RecipientLicenseNumber': lab.license_number,
    #             'TransferTypeName': 'Affiliated Transfer',
    #             'PlannedRoute': 'Take hyperlink A to hyperlink Z.',
    #             'EstimatedDepartureDateTime': get_timestamp(),
    #             'EstimatedArrivalDateTime': get_timestamp(future=360),
    #             'Transporters': [
    #                 {
    #                     'TransporterFacilityLicenseNumber': transporter.license_number,
    #                     'DriverOccupationalLicenseNumber': courier.license['number'],
    #                     'DriverName': courier.full_name,
    #                     'DriverLicenseNumber': 'dash',
    #                     'PhoneNumberForQuestions': '18005555555',
    #                     'VehicleMake': 'X',
    #                     'VehicleModel': 'X',
    #                     'VehicleLicensePlateNumber': 'X',
    #                     'IsLayover': False,
    #                     'EstimatedDepartureDateTime':get_timestamp(),
    #                     'EstimatedArrivalDateTime': get_timestamp(future=360),
    #                     'TransporterDetails': None
    #                 }
    #             ],
    #             # 'Packages': [
    #             #     {
    #             #         'PackageLabel': new_package_tag,
    #             #         'WholesalePrice': 13.33
    #             #     },
    #             # ]
    #         }
    #     ]
    # }
    # track.create_transfer_templates([template_data], license_number=cultivator.license_number)
    # transfer_template = TransferTemplate.create_from_json(track, template_data)

    # # Get the template
    # templates = track.get_transfer_templates(license_number=cultivator.license_number, start=today)
    # first_template = templates[0]

    # # Step 1b Set up another Template using: POST/transfers/v1/templates
    # second_template_data = {
    #     'Name': 'Tunnel Template',
    #     'TransporterFacilityLicenseNumber': cultivator.license_number,
    #     'DriverOccupationalLicenseNumber': courier.license['number'],
    #     'DriverName': courier.full_name,
    #     'Destinations': [
    #         {
    #             'RecipientLicenseNumber': lab.license_number,
    #             'TransferTypeName': 'Lab Sample Transfer',
    #             'PlannedRoute': 'Take the tunnel, turning left at the donut bar.',
    #             'EstimatedDepartureDateTime': get_timestamp(),
    #             'EstimatedArrivalDateTime': get_timestamp(future=360),
    #         }
    #     ]
    # }
    # track.create_transfer_templates([second_template_data], license_number=cultivator.license_number)
    # templates = track.get_transfer_templates(license_number=cultivator.license_number, start=today, end='2021-04-10')
    # second_template = templates[0]

    # # Step 2 Find the two Templates created in Step 1a and 1b by
    # # using the date search: GET/transfers/v1/templates
    # templates = track.get_transfer_templates(license_number=cultivator.license_number, start=today)

    # # Step 3 Find a Template by the Template ID number
    # # using: GET/transfers/v1/templates/{id}/deliveries
    # template_deliveries = track.get_transfer_templates(
    #     uid=templates[1].uid,
    #     action='deliveries',
    #     license_number=cultivator.license_number
    # )

    # # Step 4 Update one of the Templates created in Step 1
    # # using: PUT/transfers/v1/templates
    # templates[1].update(name='Premier Hyperloop Template')
    # updated_template = {**template_data, **{
    #     'TransferTemplateId': templates[1].uid,
    #     'Name': 'Premier Hyperloop Template'
    # }}
    # track.update_transfer_templates([updated_template], license_number=cultivator.license_number)
    # template = track.get_transfer_templates(uid=templates[1].uid, license_number=cultivator.license_number)
    # print(template.last_modified)


    # #------------------------------------------------------------------
    # # Outgoing transfers ✓
    # #------------------------------------------------------------------

    # # Step 1 Find an Incoming Transfer: GET/transfers/v1/incoming
    # incoming_transfers = track.get_transfers(license_number=retailer.license_number)

    # # Step 2 Find an Outgoing Transfer: GET/transfers/v1/outgoing
    # outgoing_transfers = track.get_transfers(
    #     transfer_type='outgoing',
    #     license_number=cultivator.license_number
    # )
    # facilities = track.get_facilities()
    # for facility in facilities:
    #     print('Getting transfers for', facility.license['number'])
    #     outgoing_transfers = track.get_transfers(
    #         transfer_type='outgoing',
    #         license_number=facility.license['number']
    #     )
    #     if outgoing_transfers:
    #         break
    #     sleep(5)

    # # Step 3 Find a Rejected Transfer: GET/transfers/v1/rejected
    # rejected_transfers = track.get_transfers(
    #     transfer_type='rejected',
    #     license_number=cultivator.license_number
    # )

    # # Step 4 Find a Transfer by the Manifest ID number: GET/transfers/v1/{id}/deliveries
    # transfer_id = 'YOUR_TRANSFER_ID'
    # traced_transfer = track.get_transfers(uid=transfer_id, license_number=cultivator.license_number)

    # # Step 5 Find The Packages Using the Delivery ID number: GET/transfers/v1/delivery/{id}/packages
    # traced_transfer_package = track.get_transfer_packages(uid=transfer_id, license_number=cultivator.license_number)

    # # Transfers Wholesale Step 6 Find Packages Wholesale Pricing
    # # Using the Delivery ID GET/transfers/v1/delivery/{id}/packages/wholesale
    # traced_wholesale_package = track.get_transfer_packages(
    #     uid=transfer_id,
    #     action='packages/wholesale',
    #     license_number=cultivator.license_number
    # )
