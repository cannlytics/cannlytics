"""
Metrc Integration Test | Cannlytics

Author: Keegan Skeate
Contact: keegan@cannlytics.com
Created: Mon Mar 29 14:18:18 2021
License: MIT License

Description:

    Perform required tests for Metrc integration, recording verification items;

        - Result code: The status code of the response.
        - ID Number: The UID for a created object, typically a 5 digit number. 
        - Names: Names for created objects, such as strain or location name.
        - Tag Number: Plant and package tags
        - Last Modified Date: The time the test or actions were ran.
        - Request Sent: The requested URL.
        - JSON Body: Minified JSON response.

    All successful requests will return a 200 status code. Get support if you cannot
    obtain a 200 status code for any request.

Resources:

    [Metrc Oklahoma Docs](https://api-ok.metrc.com/Documentation)
    [Metrc Oregon Docs](https://api-or.metrc.com/Documentation)

"""

import os
from dotenv import dotenv_values
from datetime import datetime
from time import sleep

# Import cannlytics locally for testing.
import sys
sys.path.insert(0, os.path.abspath('../../'))
from cannlytics import firebase as fb
from cannlytics.traceability import metrc # pylint: disable=no-name-in-module, import-error
from cannlytics.traceability.metrc.exceptions import MetrcAPIError # pylint: disable=no-name-in-module, import-error
from cannlytics.traceability.metrc.utils import ( # pylint: disable=no-name-in-module, import-error
    clean_nested_dictionary,
    encode_pdf,
    get_timestamp,
)
     
from cannlytics.traceability.metrc.models import ( # pylint: disable=no-name-in-module, import-error
    Facility,
    Item,
    PlantBatch,
    TransferTemplate,
)


if __name__ == '__main__':

    #------------------------------------------------------------------
    # Initialization
    #------------------------------------------------------------------
    
    # Initialize the current time.
    now = datetime.now()
    current_time = now.isoformat()
    current_date = now.strftime('%m/%d/%Y')
    today = current_time[:10]

    # Initialize Firebase.
    config = dotenv_values('../../.env')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['GOOGLE_APPLICATION_CREDENTIALS']
    db = fb.initialize_firebase()

    # Initialize a Metrc client.
    vendor_api_key = config['METRC_TEST_VENDOR_API_KEY']
    user_api_key = config['METRC_TEST_USER_API_KEY']
    track = metrc.authorize(vendor_api_key, user_api_key)

    print('--------------------------------------------')
    print('Performing Metrc Validation Test')
    print(current_time)
    print('--------------------------------------------')

    #------------------------------------------------------------------
    # Facilities
    #------------------------------------------------------------------

    # Unless facilities are not set, then get the facilities from Metrc.
    # Get facilities, with permissions set by the state for each facility type.
    facilities = track.get_facilities()

    # Define primary cultivator, lab, and retailer for tests.
    # cultivator, lab, retailer = None, None, None
    for facility in facilities:
        license_type = facility.license_type
        if cultivator is None and license_type == 'Grower':
            cultivator = facility
        elif lab is None and license_type == 'Testing Laboratory':
            lab = facility
        elif retailer is None and license_type == 'Dispensary':
            retailer = facility

        # Save facility to Firestore.
        license_number = facility.license_number
        ref = f'tests/metrc/organizations/1/facilities/{license_number}'
        data = clean_nested_dictionary(facility.to_dict())
        data['license_number'] = license_number
        fb.update_document(ref, data)
    
    # Get facilities from Firestore.
    ref = 'tests/metrc/organizations/1/facilities'
    cultivator = Facility.from_fb(track, f'{ref}/4b-X0002')
    retailer = Facility.from_fb(track, f'{ref}/3c-X0002')
    processor = Facility.from_fb(track, f'{ref}/5b-X0002')
    lab = Facility.from_fb(track, f'{ref}/6a-X0001')
    transporter = Facility.from_fb(track, f'{ref}/406-X0001')

    #------------------------------------------------------------------
    # Locations ✓
    #------------------------------------------------------------------

    # Create a new location using: POST /locations/v1/create
    cultivation_name = 'MediGrow'
    cultivation_original_name = 'medi grow'
    cultivator.create_locations([
        cultivation_original_name,
        'Harvest Location',
        'Plant Location',
        'Warehouse',
    ])
    
    # Get created location
    cultivation= None
    locations = track.get_locations(action='active', license_number=cultivator.license_number)
    for location in locations:
        if location.name == cultivation_original_name:
            cultivation = location

    # Update the name of the location using: POST /locations/v1/update
    cultivator.update_locations([cultivation.uid], [cultivation_name])

    # View the location using GET /locations/v1/{id}
    cultivation_uid = '10705'
    traced_location = cultivator.get_locations(uid=cultivation_uid)


    #------------------------------------------------------------------
    # Strains ✓
    #------------------------------------------------------------------

    # Create a new strain using: POST /strains/v1/create
    strain_name = 'New Old-Time Moonshine'
    strain = {
        'Name': strain_name,
        'TestingStatus': 'None',
        'ThcLevel': 0.2420,
        'CbdLevel': 0.0333,
        'IndicaPercentage': 0.0,
        'SativaPercentage': 100.0
    }
    try:
        track.create_strains([strain], license_number=cultivator.license_number)
    except MetrcAPIError:
        pass

    # Get the created strain's ID.
    new_strain = None
    strain_id = None
    strains = track.get_strains(license_number=cultivator.license_number)
    for s in strains:
        if s.name == strain_name:
            strain_id = s.uid
            new_strain = s

    # Change the THC and CBD levels using: POST /strains/v1/update
    new_strain.update(thc_level=0.1333, cbd_level=0.0777)

    # View the Strain using GET /strains/v1/{id}
    strain_uid = '14504'
    traced_strain = track.get_strains(uid=strain_uid, license_number=cultivator.license_number)
    print(traced_strain.name, '| THC:', traced_strain.thc_level, 'CBD:', traced_strain.cbd_level)


    #------------------------------------------------------------------
    # Items ✓
    #------------------------------------------------------------------
    
    # Create an item using: POST /items/v1/create
    item_name = 'New Old-Time Moonshine Teenth'
    item = Item.create_from_json(track, cultivator.license_number, {
        'ItemCategory': 'Flower & Buds',
        'Name': item_name,
        'UnitOfMeasure': 'Ounces',
        'Strain': strain_name,
    })

    # Create additional products for future use.
    item = Item.create_from_json(track, cultivator.license_number, {
        'ItemCategory': 'Shake/Trim',
        'Name': 'New Old-Time Moonshine Shake',
        'UnitOfMeasure': 'Grams',
        'Strain': strain_name,
    })


    # Get the item's UID.
    new_item = None
    items = track.get_items(license_number=cultivator.license_number)
    for i in items:
        print(i.name, '|', i.product_category_name)
        if i.name == item_name:
            new_item = i

    # Change the Unit Of Measure Type using: POST /items/v1/update
    new_item.update(unit_of_measure='Grams')

    # View the item using: GET /Items/v1/{id}
    traced_item = track.get_items(uid=new_item.id, license_number=cultivator.license_number)
    print('Successfully created, updated, and retrieved item:')
    print(traced_item.id, '|', traced_item.unit_of_measure)

    # Create items used for batches.
    clone = Item.create_from_json(track, cultivator.license_number, {
        'ItemCategory': 'Seeds',
        'Name': 'New Old-Time Moonshine Mature Plants',
        'UnitOfMeasure': 'Each',
        'Strain': strain_name,
    })

    # Get the clone for future use.
    clone_uid = '12324'
    clone_item = track.get_items(uid=clone_uid, license_number=cultivator.license_number)

    #------------------------------------------------------------------
    # Batches ✓
    #------------------------------------------------------------------

    # Create a new plant batch containing
    # 6 plants using: POST /plantbatches/v1/createplantings
    batch_name = 'New Old-Time Moonshine Table'
    batch = PlantBatch.create_from_json(track, cultivator.license_number, {
        'Name': batch_name,
        'Type': 'Seed',
        'Count': 6,
        'Strain': strain_name,
        'Location': 'MediGrow',
        'ActualDate': today,
    })
    sleep(10) # Hack to wait for Metrc to create the batch

    # Get the plant batch
    traced_batch = None
    batches = track.get_batches(license_number=cultivator.license_number)
    for b in batches:
        print(b.name, '|', b.type)
        if b.name == batch_name:
            traced_batch = b

    batch_uid = '8901'
    traced_batch = track.get_batches(uid=batch_uid, license_number=cultivator.license_number)

    # Create a package containing 3 clones from
    # The Plant Batch created in step 1 using: POST /plantbatches/v1/createpackages
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
    traced_batch.create_package(package)

    # Change the growth phase of 2 of the plants created in
    # Step 1 to the Vegetative Stage using:  POST /plantbatches/v1/changegrowthphase
    plant_tag = 'ENTER_YOUR_PLANT_TAG'
    growth_stage = {
        'name': traced_batch.name,
        'count': 2,
        'starting_tag': plant_tag,
        'growth_phase': 'Vegetative',
        'new_location': 'MediGrow',
        'growth_date': today,
    }
    traced_batch.change_growth_phase(growth_stage)

    # Destroy 1 of the plants using: POST /plantbatches/v1/destroy
    traced_batch.destroy_plants(count=1, reason='Male plant!')


    #------------------------------------------------------------------
    # Plants ✓
    #------------------------------------------------------------------

    # Get a plant created in the plant batches section for use.
    plants = track.get_plants(
        action='vegetative',
        license_number=cultivator.license_number,
        start=today
    )
    plant_id = '20604'
    traced_plant = track.get_plants(uid=plant_id, license_number=cultivator.license_number)

    # Change the growth phase from Vegetative to Flowering
    # using: POST /plants/v1/changegrowthphases
    mature_plant_tag = 'your-plant-tag'
    traced_plant.flower(tag=mature_plant_tag)


    # Using the now Flowering Plant in step above,
    # Move that plant to a different room using: POST /plants/v1/moveplants
    traced_plant.move(location_name='Plant Location')

    # Using the other Plant created by Step 3  in the Plant batch section,
    # Destroy that plant using: POST /plants/v1/destroyplants
    male_plant_id = '20605'
    male_plant = track.get_plants(uid=male_plant_id, license_number=cultivator.license_number)
    male_plant.destroy(
        weight=13.37,
        reason='Mother Plant Destruction',
        note='Male plant!!!'
    )

    # Using the Plant now in the Flowering Stage from Step 1
    # Manicure from the plant using: POST /plants/v1/manicureplants
    traced_plant.manicure(
        weight=9.63,
        harvest_name='1st New Old-Time Moonshine Harvest'
    )

    # Using the Plant in the Flowering Stage from Step 2
    # Harvest the plant using: POST /plants/v1/harvestplants
    traced_plant.harvest(
        harvest_name='2nd New Old-Time Moonshine Harvest',
        weight=828,
    )

    #------------------------------------------------------------------
    # Harvest ✓
    #------------------------------------------------------------------

    # Get the harvest
    harvests = track.get_harvests(
        action='active',
        license_number=cultivator.license_number,
        start=today
    )
    harvest_id = '4901'
    traced_harvest = track.get_harvests(uid=harvest_id, license_number=cultivator.license_number)

    # Step 1 Using the Harvest Created in Step 5 from Plants,
    # Create a package using: POST /harvests/v1/create/packages
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
    traced_harvest.create_packages([package])
    traced_harvest = track.get_harvests(uid=harvest_id, license_number=cultivator.license_number)
    print(traced_harvest.last_modified)

    # Step 2  Using the Harvest Created in Step 5 from Plants,
    # Remove the remaining weight as Waste
    # (MOISTURE LOSS IS NOT REMOVED AS WASTE): POST /harvests/v1/removewaste
    waste_weight = 828 - 28
    traced_harvest.remove_waste(weight=waste_weight)
    traced_harvest = track.get_harvests(uid=harvest_id, license_number=cultivator.license_number)
    print(traced_harvest.last_modified)

    # Step 3 Using the Harvest created in Plants Step 1
    # Finish that Harvest using: POST /harvests/v1/finish
    traced_harvest.finish()
    traced_harvest = track.get_harvests(uid=harvest_id, license_number=cultivator.license_number)
    print(traced_harvest.last_modified)

    # Step 4 Using the Harvest finished in Step 3
    # Unfinish that Harvest using: POST /harvests/v1/unfinish
    traced_harvest.unfinish()
    traced_harvest = track.get_harvests(uid=harvest_id, license_number=cultivator.license_number)
    print(traced_harvest.last_modified)


    #------------------------------------------------------------------
    # Packages ✓
    #------------------------------------------------------------------

    # Step 1 Using the Package created in Harvest Step 1 OR create a
    # package from an existing package that you have found.
    # Create a package from another package using: POST /packages/v1/create
    
    # Get the package created earlier.
    # packs = track.get_packages(license_number=cultivator.license_number)
    package_id = '13801'
    traced_package = track.get_packages(
        uid=package_id,
        license_number=cultivator.license_number
    )

    new_package_tag = 'YOUR_SECOND_PACKAGE_TAG'
    new_package_data = {
        'Tag': new_package_tag,
        'Location': 'Warehouse',
        'Item': 'New Old-Time Moonshine Teenth',
        'Quantity': 1.75,
        'UnitOfMeasure': 'Grams',
        # 'PatientLicenseNumber': 'X00001',
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
    traced_package.create_package(new_package_data)
    new_package = track.get_packages(label=new_package_tag, license_number=cultivator.license_number)
    print(new_package.last_modified)

    # Step 2 Using the new package created in Packages Step 1
    # change the item of a package using: POST/packages/v1/change/item
    new_package.change_item(item_name='New Old-Time Moonshine Kief')
    new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
    print(new_package.last_modified)

    # Step 3 Using the new package created in Packages Step 1
    # adjust the weight to 0 using: POST/packages/v1/adjust
    adjustment = {
        'Label': new_package_tag,
        'Quantity': -1.75,
        'UnitOfMeasure': 'Grams',
        'AdjustmentReason': 'Drying',
        'AdjustmentDate': today,
        'ReasonNote': None
    }
    new_package.adjust(weight=-1.75, note='Look ma, no weight!')
    new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
    print(new_package.last_modified)

    # Step 4 Using the new package created in Packages Step 1
    #  Finish a package using: POST/packages/v1/finish
    new_package.finish()
    new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
    print(new_package.last_modified)

    # Step 5 Using the new package created in Packages Step 1
    # Unfinish a package using: POST/packages/v1/unfinish
    new_package.unfinish()
    new_package = track.get_packages(uid=new_package.id, license_number=cultivator.license_number)
    print(new_package.last_modified)

    #------------------------------------------------------------------
    # Outgoing transfers (See Oregon test) ✓
    #------------------------------------------------------------------

    # Get licensed courier.
    courier = track.get_employees(license_number=lab.license_number)[0]

    # Create a testing package
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
                'Package': 'ABCDEF012345670000013677',
                'Quantity': 4.0,
                'UnitOfMeasure': 'Grams'
            }
        ]
    }
    track.create_packages(
        [test_package_data],
        license_number=cultivator.license_number,
        qa=True
    )

    # Get the tested package.
    test_package = track.get_packages(label=test_package_tag, license_number=cultivator.license_number)

    # Step 1a Set up an external Incoming transfer
    # using: POST/transfers/v1/external/incoming
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
    track.create_transfers(
        [transfer_data],
        license_number=cultivator.license_number,
    )


    # Step 1b Set up another external Incoming transfer
    # using: POST/transfers/v1/external/incoming
    second_transfer_data = {
        'ShipperLicenseNumber': cultivator.license_number,
        'ShipperName': cultivator.name,
        'ShipperMainPhoneNumber': '18005555555',
        'ShipperAddress1': 'Mulberry Street',
        'ShipperAddress2': None,
        'ShipperAddressCity': 'Oklahoma City',
        'ShipperAddressState': 'OK',
        'ShipperAddressPostalCode': '123',
        'TransporterFacilityLicenseNumber': cultivator.license['number'],
        'DriverOccupationalLicenseNumber': courier.license['number'],
        'DriverName': courier.full_name,
        'DriverLicenseNumber': 'xyz',
        'PhoneNumberForQuestions': '18005555555',
        'VehicleMake': 'xyz',
        'VehicleModel': 'xyz',
        'VehicleLicensePlateNumber': 'xyz',
        'Destinations': [
            {
                'RecipientLicenseNumber': cultivator.license_number,
                'TransferTypeName': 'Beginning Inventory Transfer',
                'PlannedRoute': 'Hypertube.',
                'EstimatedDepartureDateTime': get_timestamp(),
                'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
                'GrossWeight': 56,
                # 'GrossUnitOfWeightId': null,
                'Transporters': [
                    {
                        'TransporterFacilityLicenseNumber': cultivator.license_number,
                        'DriverOccupationalLicenseNumber': courier.license['number'],
                        'DriverName': courier.full_name,
                        'DriverLicenseNumber': 'xyz',
                        'PhoneNumberForQuestions': '18005555555',
                        'VehicleMake': 'xyz',
                        'VehicleModel': 'xyz',
                        'VehicleLicensePlateNumber': 'xyz',
                        # 'IsLayover': false,
                        'EstimatedDepartureDateTime': get_timestamp(),
                        'EstimatedArrivalDateTime': get_timestamp(future=60 * 24),
                        # 'TransporterDetails': null
                    }
                ],
                'Packages': [
                    {
                        # 'PackageLabel': traced_package.label,
                        # 'HarvestName': '2nd New Old-Time Moonshine Harvest',
                        'ItemName': 'New Old-Time Moonshine Teenth',
                        'Quantity': 2,
                        'UnitOfMeasureName': 'Ounces',
                        'PackagedDate': get_timestamp(),
                        'GrossWeight': 56.0,
                        'GrossUnitOfWeightName': 'Grams',
                        'WholesalePrice': 720,
                        # 'Source': '2nd New Old-Time Moonshine Harvest',
                    },
                ]
            }
        ]
    }
    track.create_transfers(
        [second_transfer_data],
        license_number=cultivator.license_number,
    )

    # Step 2 Find the two Transfers created in Step 1a and 1b
    # by using the date search: GET/transfers/v1/incoming
    traced_transfers = track.get_transfers(
        license_number=cultivator.license_number,
        start=today,
        end=get_timestamp()
    )

    # Step 3 Update one of the Transfers created in Step 1 by
    # using: PUT/transfers/v1/external/incoming
    second_transfer_data['TransferId'] = traced_transfers[0].id
    second_transfer_data['Destinations'][0]['Packages'][0]['Quantity'] = 3
    track.update_transfers(
        [second_transfer_data],
        license_number=cultivator.license_number,
    )

    updated_transfer = track.get_transfers(
        # uid=second_transfer_data['TransferId'],
        license_number=cultivator.license_number,
        start=get_timestamp(past=15),
        end=get_timestamp()
    )

    #------------------------------------------------------------------
    # Transfer templates ✓
    #------------------------------------------------------------------

    # Step 1a Set up a Template using: POST/transfers/v1/templates
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
    track.create_transfer_templates([template_data], license_number=cultivator.license_number)
    transfer_template = TransferTemplate.create_from_json(track, template_data)

    # Get the template
    templates = track.get_transfer_templates(license_number=cultivator.license_number, start=today)
    first_template = templates[0]

    # Step 1b Set up another Template using: POST/transfers/v1/templates
    second_template_data = {
        'Name': 'Tunnel Template',
        'TransporterFacilityLicenseNumber': cultivator.license_number,
        'DriverOccupationalLicenseNumber': courier.license['number'],
        'DriverName': courier.full_name,
        'Destinations': [
            {
                'RecipientLicenseNumber': lab.license_number,
                'TransferTypeName': 'Lab Sample Transfer',
                'PlannedRoute': 'Take the tunnel, turning left at the donut bar.',
                'EstimatedDepartureDateTime': get_timestamp(),
                'EstimatedArrivalDateTime': get_timestamp(future=360),
            }
        ]
    }
    track.create_transfer_templates([second_template_data], license_number=cultivator.license_number)
    templates = track.get_transfer_templates(license_number=cultivator.license_number, start=today, end='2021-04-10')
    second_template = templates[0]

    # Step 2 Find the two Templates created in Step 1a and 1b by
    # using the date search: GET/transfers/v1/templates
    templates = track.get_transfer_templates(license_number=cultivator.license_number, start=today)

    # Step 3 Find a Template by the Template ID number
    # using: GET/transfers/v1/templates/{id}/deliveries
    template_deliveries = track.get_transfer_templates(
        uid=templates[1].uid,
        action='deliveries',
        license_number=cultivator.license_number
    )

    # Step 4 Update one of the Templates created in Step 1
    # using: PUT/transfers/v1/templates
    templates[1].update(name='Premier Hyperloop Template')
    updated_template = {**template_data, **{
        'TransferTemplateId': templates[1].uid,
        'Name': 'Premier Hyperloop Template'
    }}
    track.update_transfer_templates([updated_template], license_number=cultivator.license_number)
    template = track.get_transfer_templates(uid=templates[1].uid, license_number=cultivator.license_number)
    print(template.last_modified)


    #------------------------------------------------------------------
    # Outgoing transfers ✓
    #------------------------------------------------------------------

    # Step 1 Find an Incoming Transfer: GET/transfers/v1/incoming
    incoming_transfers = track.get_transfers(license_number=retailer.license_number)

    # Step 2 Find an Outgoing Transfer: GET/transfers/v1/outgoing
    outgoing_transfers = track.get_transfers(
        transfer_type='outgoing',
        license_number=cultivator.license_number
    )
    facilities = track.get_facilities()
    for facility in facilities:
        print('Getting transfers for', facility.license['number'])
        outgoing_transfers = track.get_transfers(
            transfer_type='outgoing',
            license_number=facility.license['number']
        )
        if outgoing_transfers:
            break
        sleep(5)

    # Step 3 Find a Rejected Transfer: GET/transfers/v1/rejected
    rejected_transfers = track.get_transfers(
        transfer_type='rejected',
        license_number=cultivator.license_number
    )                            

    # Step 4 Find a Transfer by the Manifest ID number: GET/transfers/v1/{id}/deliveries
    transfer_id = 'YOUR_TRANSFER_ID'
    traced_transfer = track.get_transfers(uid=transfer_id, license_number=cultivator.license_number)

    # Step 5 Find The Packages Using the Delivery ID number: GET/transfers/v1/delivery/{id}/packages
    traced_transfer_package = track.get_transfer_packages(uid=transfer_id, license_number=cultivator.license_number)

    # Transfers Wholesale Step 6 Find Packages Wholesale Pricing
    # Using the Delivery ID GET/transfers/v1/delivery/{id}/packages/wholesale
    traced_wholesale_package = track.get_transfer_packages(
        uid=transfer_id,
        action='packages/wholesale',
        license_number=cultivator.license_number
    )


    #------------------------------------------------------------------
    # Lab results ✓
    #------------------------------------------------------------------

    # Record a lab test result using: POST /labtests/v1/record
    test_package_data = {
        'Tag': test_package_tag,
        'Location': None,
        'Item': test_package.item['name'],
        'UnitOfWeight': 'Grams',
        # 'PatientLicenseNumber': 'X00001',
        'Note': 'Clean as a whistle.',
        'IsProductionBatch': False,
        'ProductionBatchNumber': None,
        'IsTradeSample': False,
        'IsDonation': False,
        'ProductRequiresRemediation': False,
        'RemediateProduct': False,
        'RemediationMethodId': None,
        'RemediationDate': None,
        'RemediationSteps': None,
        'ActualDate': today,
        'Ingredients': [
            {
                'HarvestId': 2,
                'HarvestName': None,
                'Weight': 100.23,
                'UnitOfWeight': 'Grams'
            },
        ]
    }
    track.create_harvest_testing_packages(test_package_data, license_number=cultivator.license_number)
    packages = track.get_packages(license_number=cultivator.license_number)
    lab_package = [0] # TODO: Get lab testing package

    # Create the lab result record.
    encoded_pdf = encode_pdf('../assets/pdfs/example_coa.pdf')
    test_package_label =  'ABCDEF012345670000015141'
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
    track.post_lab_results([lab_result_data], license_number=lab.license_number)

    # Get tested package.
    test_package = track.get_packages(label=test_package_label, license_number=lab.license_number)

    # Get the tested package's lab result.
    lab_results = track.get_lab_results(uid=test_package.id, license_number=lab.license_number)

    #------------------------------------------------------------------
    # Sales ✓
    #------------------------------------------------------------------

    # Get a retail package.
    retailer_packages = track.get_packages(license_number=retailer.license_number)
    retailer_package = retailer_packages[1]

    # Step 1 Create a sales receipt for a package using: POST /sales/v1/receipts
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
    track.create_receipts([receipt_data], license_number=retailer.license_number)

    # Get the sale.
    sales = track.get_receipts(
        action='active',
        license_number=retailer.license_number,
        start=get_timestamp(past=30)
    )
    receipt = None
    for sale in sales:
        print(sale.total_price)
        if sale.total_price == 25.00:
            receipt = sale
            break
    # sale = track.get_receipts(uid='409', license_number=retailer.license_number)
    print('Sale:', receipt.id, 'Last modified:', receipt.last_modified)
    
    # Step 2 Update the sales receipt using: PUT /sales/v1/receipts
    sale.total_price = 30
    sale.transactions[0] = {
        'PackageLabel': retailer_package.label,
        'Quantity': 1.75,
        'UnitOfMeasure': 'Grams',
        'TotalAmount': 30.00
    }
    sale.update()

    # Get the sale to check it's modified time..
    sale = track.get_receipts(uid='409', license_number=retailer.license_number)
    print('Sale:', sale.id, 'Last modified:', sale.last_modified)

    # Step 3 Void the sales receipt using: DELETE /sales/v1/receipts/{id}
    sale.delete()

    # Get the sale to check it's modified time.
    sales = track.get_receipts(action='inactive', license_number=retailer.license_number)
    print('Sale:', sale.id, 'Last modified:', sale.last_modified)

