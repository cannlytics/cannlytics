"""
Metrc API Endpoint Tests | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 1/12/2023
Updated: 1/20/2023
License: MIT License <https://opensource.org/licenses/MIT>
"""
import os
import requests
from dotenv import dotenv_values

# Define the endpoint.
ENDPOINT = 'metrc'

# Dev: Test with the development server.
BASE = 'http://127.0.0.1:8000/api'

# Production: Uncomment to test with the production server once published.
# BASE = 'https://console.cannlytics.com/api'

# Load your API key to pass in the authorization header as a bearer token.
config = dotenv_values('../../.env')
API_KEY = config['CANNLYTICS_API_KEY']


# === Tests ===
if __name__ == '__main__':

    # Authentication a session.
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {API_KEY}'})  


    #-------------------------------------------------------------------
    # License management.
    #-------------------------------------------------------------------

    # [✓] Test adding a Metrc user API key.
    print('Adding a license...')
    url = f'{BASE}/metrc/admin/create-license'
    data = {
      'metrc_user_api_key': os.getenv('METRC_TEST_USER_API_KEY'),
      'license_number': '',
      'license_type': 'Processor',
      'org_id': 'test-processor',
      'state': 'ok',
    }
    response = session.post(url, json=data)
    assert response.json()['success']
    print('Added Metrc user API key.')

    # [✓] Delete a license.
    print('Deleting a license...')
    url = f'{BASE}/metrc/admin/delete-license'
    data = {
      'license_number': '',
      'org_id': 'test-processor',
      'deletion_reason': 'Test deletion.',
    }
    response = session.post(url, json=data)
    assert response.json()['success']
    print('Deleted Metrc user API key.')


    #-------------------------------------------------------------------
    # Facilities and employees
    #-------------------------------------------------------------------

    # [✓] Test facilities.
    response = session.get(f'{BASE}/metrc/facilities')
    assert response.status_code == 200
    facilities = response.json()['data']
    print('Found %i facilities' % len(facilities))

    # [✓] Test getting employees.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/employees', params=params)
    assert response.status_code == 200
    employees = response.json()['data']
    print('Found %i employees' % len(employees))


    #-------------------------------------------------------------------
    # Locations
    #-------------------------------------------------------------------

    # [✓] Test getting locations.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations', params=params)
    assert response.status_code == 200
    locations = response.json()['data']
    print('Found %i locations' % len(locations))

    # [✓] Get location types.
    params = {'license': facilities[5]['license']['number']}
    response = session.get(f'{BASE}/metrc/types/locations', params=params)
    assert response.status_code == 200
    location_types = response.json()['data']
    print('Found %i location types' % len(location_types))

    # [✓] Test creating a location.
    data = {
        'name': 'CAN API Test Location',
        'location_type': location_types[0]['name']
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/locations', json=data, params=params)
    assert response.status_code == 200
    print('Created location.')

    # [✓] Test update the name of the location.
    data = {
        'id': '61001',
        'name': 'CAN Test Location',
        'location_type_name': location_types[0]['name']
    }
    response = session.post(f'{BASE}/metrc/locations', json=data, params=params)
    assert response.status_code == 200
    print('Updated location.')

    # [✓] Test getting a specific location.
    uid = '61001'
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/locations/{uid}', params=params)
    assert response.status_code == 200
    location = response.json()['data']
    print('Found location.')

    # [✓] Test deleting a location.
    uid = '61001'
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/locations/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted location.')


    #-------------------------------------------------------------------
    # Strains
    #-------------------------------------------------------------------

    # [✓] Create a new strain.
    strain_name = 'Moonshine Haze'
    data = {
        'name': strain_name,
        'testing_status': 'None',
        'thc_level': 0.242,
        'cbd_level': 0.0333,
        'indica_percentage': 0.0,
        'sativa_percentage': 100.0
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/strains', json=data, params=params)
    assert response.status_code == 200
    print('Created strain.')

    # [✓] Get strains.
    response = session.get(f'{BASE}/metrc/strains', params=params)
    strains = response.json()['data']
    for strain in strains:
        if strain['name'] == strain_name:
            new_strain = strain
            break

    # [✓] Update a strain.
    data = {
        'id': new_strain['id'],
        'name': strain_name,
        'testing_status': 'None',
        'thc_level': 0.242,
        'cbd_level': 0.0333,
        'indica_percentage': 25.0,
        'sativa_percentage': 75.0
    }
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/strains', json=data, params=params)
    assert response.status_code == 200
    print('Updated strain.')

    # [✓] Get a strain.
    uid = new_strain['id']
    response = session.get(f'{BASE}/metrc/strains/{uid}', params=params)
    assert response.status_code == 200
    print('Retrieved strain.', response.json()['data'])

    # [✓] Delete a strain.
    uid = new_strain['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/strains/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted strain.')


    #-------------------------------------------------------------------
    # Items
    #-------------------------------------------------------------------

    # [✓] Get item categories.
    response = session.get(f'{BASE}/metrc/types/categories', params=params)
    assert response.status_code == 200
    categories = response.json()['data']

    # [✓] Create an item.
    item_name = 'Moonshine Haze Eighth'
    data = {
        'item_category': categories[7]['name'],
        'name': item_name,
        'unit_of_measure': 'Ounces',
        'strain': strain_name,
    }
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=data, params=params)
    assert response.status_code == 200
    print('Created item.')

    # [✓] Create multiple items.
    data = [
        {
            'item_category': categories[7]['name'],
            'name': 'Moonshine Haze Shake',
            'unit_of_measure': 'Ounces',
            'strain': strain_name,
        },
        {
            'item_category': categories[7]['name'],
            'name': 'Moonshine Haze Teener',
            'unit_of_measure': 'Grams',
            'strain': strain_name,
        }
    ]
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=data, params=params)
    assert response.status_code == 200
    print('Created items.')

    # [✓] Query items.
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/items', params=params)
    assert response.status_code == 200
    items = response.json()['data']
    for item in items:
        if 'Moonshine' in item['name']:
            print(item['id'], item['name'])
            break

    # [✓] Get an item.
    uid = item['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.get(f'{BASE}/metrc/items/{uid}', params=params)
    assert response.status_code == 200

    # [✓] Update an item.
    update = item.copy()
    update['unit_of_measure'] = 'Grams'
    params = {'license': facilities[0]['license']['number']}
    response = session.post(f'{BASE}/metrc/items', json=update, params=params)
    assert response.status_code == 200
    print('Updated item.')

    # [✓] Delete an item.
    uid = item['id']
    params = {'license': facilities[0]['license']['number']}
    response = session.delete(f'{BASE}/metrc/items/{uid}', params=params)
    assert response.status_code == 200
    print('Deleted item.')


    #-------------------------------------------------------------------
    # Batches
    #-------------------------------------------------------------------

    # [✓] Get batch types.
    response = session.get(f'{BASE}/metrc/types/batches', params=params)
    assert response.status_code == 200
    batch_types = response.json()['data']
    print('Found %i batch types' % len(batch_types))

    # [✓] Get waste methods.
    response = session.get(f'{BASE}/metrc/types/waste-methods', params=params)
    assert response.status_code == 200
    waste_methods = response.json()['data']
    print('Found %i waste methods' % len(waste_methods))

    # [✓] Get waste reasons.
    response = session.get(f'{BASE}/metrc/types/waste-reasons', params=params)
    assert response.status_code == 200
    waste_reasons = response.json()['data']
    print('Found %i waste reasons' % len(waste_reasons))

    # [✓] Get waste types.
    response = session.get(f'{BASE}/metrc/types/waste', params=params)
    assert response.status_code == 200
    waste_types = response.json()['data']
    print('Found %i waste types' % len(waste_types))

    # [✓] Create a new plant batch.
    today = '2023-01-20'
    batch_name = 'Moonshine Haze Hydroponics'
    data = {
        'name': batch_name,
        'type': 'Seed',
        'count': 6,
        'strain': strain_name,
        'location': 'CAN API Test Location',
        'actual_date': today,
        'patient_license_number': '',
        'source_plant_batches': None,
    }
    params = {'license': facilities[5]['license']['number']}
    response = session.post(f'{BASE}/metrc/batches', json=data, params=params)
    assert response.status_code == 200
    print('Created batch.')

    # [✓] Get a plant batch.
    uid = response.json()['data'][0]['id']
    params = {'license': facilities[5]['license']['number']}
    response = session.get(f'{BASE}/metrc/batches/{uid}', params=params)
    assert response.status_code == 200

    # [ ] Create a package from a batch.
    batch_tag = 'ENTER_YOUR_BATCH_TAG'
    package = {
        'id': traced_batch.uid,
        'count': 3,
        'location': 'MediGrow',
        'item': 'New Old-Time Moonshine Clone',
        'tag': batch_tag,
        'note': 'A package containing 3 clones from the Old-time Moonshine Plant Batch',
        'is_trade_sample': False,
        'is_donation': False,
        'actual_date': today
    }

    # [ ] Flower a batch.
    data = {
        'name': traced_batch.name,
        'count': 2,
        'starting_tag': plant_tag,
        'growth_phase': 'Vegetative',
        'new_location': 'MediGrow',
        'growth_date': today,
    }


    # [ ] Destroy a batch.
    data = {
        'count': 1,
        'reason': 'Male plant!'
    }


    # [ ] Get additives.


    # [ ] Manage waste.


    #-------------------------------------------------------------------
    # Plants
    #-------------------------------------------------------------------

    # [ ] Get a plant created in a plant batch.


    # [ ] Change the growth phase of a plant from `Vegetative` to `Flowering`.


    # [ ] Move a plant to a different room.


    # [ ] Destroy a plant.


    # [ ] Manicure a plant.


    # [ ] Harvest a plant.


    # [ ] Delete a harvest?


    #-------------------------------------------------------------------
    # Harvests
    #-------------------------------------------------------------------

    # [ ] Get a harvest.


    # [ ] Create a package.
    package_tag = 'YOUR_PACKAGE_TAG'
    package = {
        'Tag': package_tag,
        'Location': 'Harvest Location',
        'Item': 'New Old-Time Moonshine Teenth',
        'UnitOfWeight': 'Grams',
        # 'PatientLicenseNumber': 'X00001',
        'Note': 'Golden ticket in this package.',
        # 'IsProductionBatch': False,
        # 'ProductionBatchNumber': None,
        # 'IsTradeSample': False,
        # 'IsDonation': False,
        # 'ProductRequiresRemediation': False,
        # 'RemediateProduct': False,
        # 'RemediationMethodId': None,
        # 'RemediationDate': None,
        # 'RemediationSteps': None,
        'ActualDate': today,
        'Ingredients': [
            {
                'HarvestId': harvest_id,
                # 'HarvestName': None,
                'Weight': 28,
                'UnitOfWeight': 'Grams'
            },
        ]
    }


    # [ ] Remove waste weight from a harvest.


    # [ ] Finish a harvest.


    # [ ] Unfinish the harvest.


    # [ ] Delete a harvest?


    #-------------------------------------------------------------------
    # Packages
    #-------------------------------------------------------------------

    # [✓] Get package types.
    response = session.get(f'{BASE}/metrc/types/packages', params=params)
    assert response.status_code == 200
    package_types = response.json()['data']
    print('Found %i package types' % len(package_types))

    # [✓] Get package statuses.
    response = session.get(f'{BASE}/metrc/types/package-statuses', params=params)
    assert response.status_code == 200
    package_statuses = response.json()['data']
    print('Found %i package statuses' % len(package_statuses))

    # [✓] Get adjustment reasons.
    response = session.get(f'{BASE}/metrc/types/adjustments', params=params)
    assert response.status_code == 200
    adjustment_reasons = response.json()['data']
    print('Found %i adjustment reasons' % len(adjustment_reasons))

    # [ ] Get a package.


    # [ ] Create a package from another package.
    new_package_tag = 'YOUR_SECOND_PACKAGE_TAG'
    new_package_data = {
        'Tag': new_package_tag,
        'Location': 'Warehouse',
        'Item': 'New Old-Time Moonshine Teenth',
        'Quantity': 1.75,
        'UnitOfMeasure': 'Grams',
        # 'PatientLicenseNumber': 'redacted',
        'Note': '1st teenth for sale.',
        # 'IsProductionBatch': False,
        # 'ProductionBatchNumber': None,
        # 'IsDonation': False,
        # 'ProductRequiresRemediation': False,
        # 'UseSameItem': True,
        'ActualDate': today,
        'Ingredients': [
            {
                'Package': traced_package.label,
                'Quantity': 1.75,
                'UnitOfMeasure': 'Grams'
            }
        ]
    }


    # [ ] Change the item of a package.


    # [ ] Adjust the weight of a package.
    adjustment = {
        'Label': new_package_tag,
        'Quantity': -1.75,
        'UnitOfMeasure': 'Grams',
        'AdjustmentReason': 'Drying',
        'AdjustmentDate': today,
        'ReasonNote': None
    }


    # [ ] Finish a package.


    # [ ] Unfinish a package.


    # [ ] Delete a package?


    #-------------------------------------------------------------------
    # Transfers and transfer templates
    #-------------------------------------------------------------------

    # [✓] Get transfer types.
    # FIXME: The keys are not in snake_case.
    response = session.get(f'{BASE}/metrc/types/transfers', params=params)
    assert response.status_code == 200
    transfer_types = response.json()['data']
    print('Found %i transfer types' % len(transfer_types))

    # [ ] Get a licensed courier.


    # [ ] Create a testing package.
    test_package_tag = 'YOUR_TEST_PACKAGE_TAG'
    test_package_data = {
        'Tag': test_package_tag,
        'Location': 'Warehouse',
        'Item': 'New Old-Time Moonshine Teenth',
        'Quantity': 4.0,
        'UnitOfMeasure': 'Grams',
        'Note': 'Quality assurance test sample.',
        'ActualDate': today,
        'Ingredients': [
            {
                'Package': 'redacted',
                'Quantity': 4.0,
                'UnitOfMeasure': 'Grams'
            }
        ]
    }


    # [ ] Get the tested package.


    # [ ] Set up an external transfer.
    transfer_data = {
        'ShipperLicenseNumber': cultivator.license_number,
        'ShipperName': cultivator.name,
        'ShipperMainPhoneNumber': '18005555555',
        'ShipperAddress1': 'Mulberry Street',
        'ShipperAddress2': None,
        'ShipperAddressCity': 'Oklahoma City',
        'ShipperAddressState': 'OK',
        'ShipperAddressPostalCode': '123',
        'TransporterFacilityLicenseNumber': lab.license['number'],
        # 'DriverOccupationalLicenseNumber': grower.license['number'],
        # 'DriverName': grower.full_name,
        # 'DriverLicenseNumber': 'xyz',
        # 'PhoneNumberForQuestions': '18005555555',
        # 'VehicleMake': 'xyz',
        # 'VehicleModel': 'xyz',
        # 'VehicleLicensePlateNumber': 'xyz',
        'Destinations': [
            {
                'RecipientLicenseNumber': lab.license_number,
                'TransferTypeName': 'Lab Sample Transfer',
                'PlannedRoute': 'Hypertube.',
                'EstimatedDepartureDateTime': get_timestamp(),
                'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
                'GrossWeight': 4,
                # 'GrossUnitOfWeightId': None,
                'Transporters': [
                    {
                        'TransporterFacilityLicenseNumber': lab.license_number,
                        'DriverOccupationalLicenseNumber': courier.license['number'],
                        'DriverName': courier.full_name,
                        'DriverLicenseNumber': 'xyz',
                        'PhoneNumberForQuestions': '18005555555',
                        'VehicleMake': 'xyz',
                        'VehicleModel': 'xyz',
                        'VehicleLicensePlateNumber': 'xyz',
                        # 'IsLayover': False,
                        'EstimatedDepartureDateTime': get_timestamp(),
                        'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
                        # 'TransporterDetails': None
                    }
                ],
                'Packages': [
                    {
                        # 'PackageLabel': traced_package.label,
                        # 'HarvestName': '2nd New Old-Time Moonshine Harvest',
                        'ItemName': 'New Old-Time Moonshine Teenth',
                        'Quantity': 1,
                        'UnitOfMeasureName': 'Each',
                        'PackagedDate': get_timestamp(),
                        'GrossWeight': 4.0,
                        'GrossUnitOfWeightName': 'Grams',
                        'WholesalePrice': None,
                        # 'Source': '2nd New Old-Time Moonshine Harvest',
                    },
                ]
            }
        ]
    }


    # [ ] Get external transfers.


    # [ ] Update an external transfer.


    # [ ] Create a transfer template.
    template_data = {
        'Name': 'HyperLoop Template',
        'TransporterFacilityLicenseNumber': cultivator.license_number,
        'DriverOccupationalLicenseNumber': courier.license['number'],
        'DriverName': courier.full_name,
        # 'DriverLicenseNumber': None,
        # 'PhoneNumberForQuestions': None,
        # 'VehicleMake': None,
        # 'VehicleModel': None,
        # 'VehicleLicensePlateNumber': None,
        'Destinations': [
            {
                'RecipientLicenseNumber': lab.license_number,
                'TransferTypeName': 'Affiliated Transfer',
                'PlannedRoute': 'Take hyperlink A to hyperlink Z.',
                'EstimatedDepartureDateTime': get_timestamp(),
                'EstimatedArrivalDateTime': get_timestamp(future=360),
                'Transporters': [
                    {
                        'TransporterFacilityLicenseNumber': transporter.license_number,
                        'DriverOccupationalLicenseNumber': courier.license['number'],
                        'DriverName': courier.full_name,
                        'DriverLicenseNumber': 'dash',
                        'PhoneNumberForQuestions': '18005555555',
                        'VehicleMake': 'X',
                        'VehicleModel': 'X',
                        'VehicleLicensePlateNumber': 'X',
                        'IsLayover': False,
                        'EstimatedDepartureDateTime':get_timestamp(),
                        'EstimatedArrivalDateTime': get_timestamp(future=360),
                        'TransporterDetails': None
                    }
                ],
                # 'Packages': [
                #     {
                #         'PackageLabel': new_package_tag,
                #         'WholesalePrice': 13.33
                #     },
                # ]
            }
        ]
    }


    # [ ] Get transfer templates.


    # [ ] Update a transfer template.


    # [ ] Delete a transfer template.


    #-------------------------------------------------------------------
    # Lab results
    #-------------------------------------------------------------------

    # [✓] Get test statuses.
    response = session.get(f'{BASE}/metrc/types/test-statuses', params=params)
    assert response.status_code == 200
    test_statuses = response.json()['data']
    print('Found %i test statuses' % len(test_statuses))
    
    # [✓] Get test types.
    response = session.get(f'{BASE}/metrc/types/tests', params=params)
    assert response.status_code == 200
    test_types = response.json()['data']
    print('Found %i test types' % len(test_types))

    # [✓] Get units of measure.
    response = session.get(f'{BASE}/metrc/types/units', params=params)
    assert response.status_code == 200
    units = response.json()['data']
    print('Found %i units of measure' % len(units))

    # [ ] Record a lab test result.


    # [ ] Create the lab result record.
    lab_result_data = {
        'Label': test_package_label,
        'ResultDate': get_timestamp(),
        # 'LabTestDocument': {
            # 'DocumentFileName': 'new-old-time-moonshine.pdf',
            # 'DocumentFileBase64': 'encoded_pdf',
        # },
        'Results': [
            {
                'LabTestTypeName': 'THC',
                'Quantity': 0.07,
                'Passed': True,
                'Notes': ''
            },
            {
                'LabTestTypeName': 'CBD',
                'Quantity': 23.33,
                'Passed': True,
                'Notes': ''
            },
            # {
            #     'LabTestTypeName': 'Microbiologicals',
            #     'Quantity': 0,
            #     'Passed': True,
            #     'Notes': ''
            # },
            # {
            #     'LabTestTypeName': 'Pesticides',
            #     'Quantity': 0,
            #     'Passed': True,
            #     'Notes': ''
            # },
            # {
            #     'LabTestTypeName': 'Heavy Metals',
            #     'Quantity': 0,
            #     'Passed': True,
            #     'Notes': ''
            # },
        ]
    }


    # [ ] Get a package's lab results.


    # [ ] Get lab results for multiple packages.


    #-------------------------------------------------------------------
    # Sales
    #-------------------------------------------------------------------

    # [✓] Get customer types.
    response = session.get(f'{BASE}/metrc/types/customers', params=params)
    assert response.status_code == 200
    customer_types = response.json()['data']
    print('Found %i customer types' % len(customer_types))

    # [ ] Create a sales receipt for a package.
    receipt_data = {
        'SalesDateTime': get_timestamp(),
        'SalesCustomerType': 'Patient',
        'PatientLicenseNumber': '1',
        'Transactions': [
            {
                'PackageLabel': retailer_package.label,
                'Quantity': 1.75,
                'UnitOfMeasure': 'Grams',
                'TotalAmount': 25.00
            }
        ]
    }


    # [ ] Get a sale.


    # [ ] Get sales.


    # [ ] Update a sales receipt.


    # [ ] Void a sales receipt.


    #-------------------------------------------------------------------
    # Deliveries
    #-------------------------------------------------------------------

    # [ ] Get return reasons.
    response = session.get(f'{BASE}/metrc/types/return-reasons', params=params)
    assert response.status_code == 200
    return_reasons = response.json()['data']
    print('Found %i return reasons' % len(return_reasons))

    # [ ] Create a delivery.


    # [ ] Get deliveries.


    # [ ] Query deliveries.


    # [ ] Update a delivery.


    # [ ] Delete a delivery.


    # [ ] Complete a delivery.
