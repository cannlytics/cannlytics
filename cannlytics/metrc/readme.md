# Cannlytics Metrc Module

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_metrc_logo.png?alt=media&token=8087c714-c03f-47f1-9196-7353cc887ead">
</div>

<!-- Optional: Is a table of contents necessary? -->
<!-- - [Metrc Client]
- [Metrc Models]
- [Metrc Constants]
- [References] -->

[Metrc](https://metrc.com) is the predominant tracking and traceability system mandated for use by cannabis licensees in the majority of states that permit cannabis markets. Cannabis licensees and verified software integrators use Metrc to compliantly track cannabis at each point of the supply chain. You can use the `cannlytics.metrc` module to securely interface with the Metrc API and perform all operations needed for compliance. Simply plug in your vendor and user API keys, specify your state of operations, and you're off to the races.

```py
from cannlytics import metrc

# Initialize a Metrc API client.
track = metrc.authorize(
    'your-vendor-api-key',
    'your-user-api-key',
    primary_license='your-user-license-number',
    state='ca',
)
```

Producer / processor workflow:

```py
# Get a plant by it's ID.
plant = track.get_plants(uid='123')

# Change the growth phase from vegetative to flowering.
plant.flower(tag='your-plant-tag')

# Move the flowering plant to a new room.
plant.move(location_name='The Flower Room')

# Manicure useable cannabis from the flowering plant.
plant.manicure(harvest_name='Old-Time Moonshine', weight=4.20)

# Harvest the flowering plant.
plant.harvest(harvest_name='Old-Time Moonshine', weight=420)
```

Lab workflow:

```py
# Post lab results.
track.post_lab_results([{...}, {...}])

# Get a tested package.
test_package = track.get_packages(label='abc')

# Get the tested package's lab result.
lab_results = track.get_lab_results(uid=test_package.id)
```

Retail workflow:

```py
# Get a retail package.
package = track.get_packages(label='abc')

# Create a sales receipts.
track.create_receipts([{...}, {...}])

# Get recent receipts.
sales = track.get_receipts(action='active', start='2021-04-20')

# Update the sales receipt.
sale = track.get_receipts(uid='420')
sale.total_price = 25
sale.update()
```

## Metrc Client

The `cannlytics.metrc.client` submodule contains the `Metrc` class responsible for communicating with the Metrc API. You can use the `authorize` function to initiate a `Metrc` client, or you can call the class directly as follows.

```py
from cannlytics.metrc import Metrc

# Initialize a Metrc API client.
track = Metrc(
    vendor_api_key,
    user_api_key,
    logs=True,
    primary_license='',
    test=True,
)
```

The table below contains all of the methods of the `Metrc` class. In general, you can pass ISO-formatted times to `start` and `end` arguments, specify `action` where applicable, and specify `license_number` to perform operations for a specific licensee. Methods that create or update data accept an optional argument `return_obs` for you to specify if you wish for the created or updated data to be returned. Note that this requires subsequent requests to the Metrc API, so, the default is for create or update methods to return `None`. Methods to get data usually accept a `uid` argument for you to specify a specific Metrc tag or label.

*Employees and Facilities*
| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_employees(license_number='')` | Get all employees. | `/employees/v1/`|
| `get_facilities()` | Get all facilities. | `/employees/v1/`|
| `get_facility(license_number='')` | Get a given facility by its license number. | `/employees/v1/`|

*Deliveries*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_deliveries(data, license_number='', return_obs=False)` | Create home deliver(ies). | `/sales/v1/deliveries` |
| `get_deliveries(uid='', action='active', license_number='', start='', end='', sales_start='', sales_end='')` | Get sale(s). Actions: `active`, `inactive`. | `/sales/v1/deliveries` |
| `get_return_reasons(license_number='')` | Get the possible return reasons for home delivery items. | `/sales/v1/deliveries/delivery/returnreasons` |
| `complete_deliveries(data, license_number='')` | Complete home delivery(ies). | `/sales/v1/deliveries` |
| `delete_delivery(uid, license_number='')` | Delete a home delivery. | `/sales/v1/deliveries` |
| `update_deliveries(data, license_number='')` | Update home delivery(ies). | `/sales/v1/deliveries` |

*Harvests*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_harvests(uid='', action='active', license_number='', start='', end='')` | Get harvests. Actions: `active`, `onhold`, `inactive`, `waste/types`. | `/harvests/v1/` |
| `finish_harvests(data, license_number='')` | Finish harvests. | `/harvests/v1/finish` |
| `unfinish_harvests(data, license_number='')` | Unfinish harvests. | `/harvests/v1/unfinish` |
| `remove_waste(data, license_number='')` | Remove's waste from a harvest. | `/harvests/v1/removewaste` |
| `move_harvests(data, license_number='')` | Move a harvests. | `/harvests/v1/move` |
| `create_harvest_packages(data, license_number='', return_obs=False)` | Create packages from a harvest. | `/harvests/v1/create/packages` |
| `create_harvest_testing_packages(data, license_number='', return_obs=False)` | Create packages from a harvest for testing. | `/harvests/v1/create/packages/testing` |

*Items*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_item_categories(license_number='')` | Get all item categories. | `/items/v1/categories` |
| `get_item(uid='', action='active', license_number='')` | Get an item. Actions: `active`, `categories`, `brands`. | `/items/v1/` |
| `get_items(uid='', action='active', license_number='')` | Get items. Actions: `active`, `categories`, `brands`. | `/items/v1/` |
| `create_item(data, license_number='', return_obs=False)` | Create an item. | `/items/v1/create` |
| `create_items(data, license_number='', return_obs=False)` | Create items. | `/items/v1/create` |
| `update_item(data, license_number='', return_obs=False)` | Update an item. | `/items/v1/update` |
| `update_items(data, license_number='', return_obs=False)` | Update items. | `/items/v1/update` |
| `delete_item(uid, license_number='')` | Delete item. | `/items/v1/` |

*Lab Results*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_lab_results(uid='', license_number='')` | Get lab results. | `/labtests/v1/results` |
| `get_test_types(license_number='')` | Get required quality assurance analyses. | `/labtests/v1/types` |
| `get_test_statuses(license_number='')` | Get pre-defined lab statuses. | `/labtests/v1/states` |
| `post_lab_results(data, license_number='', return_obs=False)` | Post lab result(s). | `/labtests/v1/record` |
| `upload_coas(data, license_number='')` | Upload lab result CoA(s). | `/labtests/v1/labtestdocument` |
| `release_lab_results(data, license_number='')` | Release lab result(s). | `/labtests/v1/results/release` |

*Locations*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_location_types(license_number='')` | Get all location types for a given license. | `/locations/v1/types` |
| `get_location(uid='', license_number='')` | Get a location. | `/locations/v1/` |
| `get_locations(uid='', action='active', license_number='')` | Get locations. Action: `active`, `types`. | `/locations/v1/` |
| `create_location(name, location_type='default', license_number='', return_obs=False)` | Create location. | `/locations/v1/create` |
| `create_locations(names, types=[], license_number='', return_obs=False)` | Create location(s). | `/locations/v1/create` |
| `update_locations(data, license_number='', return_obs=False)` | Update location(s). | `/locations/v1/update` |
| `delete_location(uid, license_number='')` | Delete location. | `/locations/v1/` |

*Packages*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_adjustment_reasons(license_number='')` | Get reasons for adjusting packages. | `/packages/v1/adjust/reasons` |
| `get_package_types(license_number='')` | Get all facilities. | `/packages/v1/types` |
| `get_package(uid='', label='active', action='active', license_number='')` | Get a package. Action: `active`, `onhold`, `inactive`, `types`, `adjust/reasons`. | `/packages/v1/` |
| `get_packages(uid='', label='', action='active', license_number='', start='', end='')` | Get package(s). Action: `active`, `onhold`, `inactive`, `types`, `adjust/reasons`. | `/packages/v1/` |
| `create_packages(data, license_number='', qa=False, plantings=False, return_obs=False)` | Create packages. | `/packages/v1/create` |
| `update_packages(data, license_number='', return_obs=False)` | Update packages. | `/packages/v1/update` |
| `delete_package(uid, license_number='')` | Delete a package. | `/packages/v1/` |
| `change_package_items(data, license_number='', return_obs=False)` | Update package items. | `/packages/v1/change/item` |
| `update_package_item_locations(data, license_number='', return_obs=False)` | Update package item location(s). | `/packages/v1/change/locations` |
| `manage_packages(data, action='adjust', license_number='', return_obs=False)` | Adjust package(s). Actions: `adjust`, `finish`, `unfinish`, `remediate`. | `/packages/v1/` |
| `update_package_notes(data, license_number='', return_obs=False)` | Update package note(s). | `/packages/v1/change/note` |

*Patients*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_patients(uid='', action='active', license_number='')` | Get licensee member patients. Action: `active`. | `/patients/v1/` |
| `create_patients(data, license_number='', return_obs=False)` | Create patient(s). | `/patients/v1/` |
| `update_patients(data, license_number='', return_obs=False)` | Update strain(s). | `/patients/v1/` |
| `delete_patient(uid, license_number='')` | Delete patient. | `/patients/v1/` |

*Plant Batches*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_plant_batch(data, license_number='', return_obs=False)` | Create a plant batch. | `/plantbatches/v1/createplantings` |
| `create_plant_batches(data, license_number='', return_obs=False)` | Create plant batches. | `/plantbatches/v1/createplantings` |
| `get_batch_types(license_number='')` | Get plant batch types. | `/plantbatches/v1/types` |
| `get_batches(uid='', action='active', license_number='', start='', end='')` | Get plant batches(s). Actions: `active`, `inactive`, `types`. | `/plantbatches/v1/` |
| `manage_batches(data, action, license_number='', from_mother=False, return_obs=False)` | Manage plant batch(es) by applying a given action. Actions: `createplantings`, `createpackages`, `split`, `/create/packages/frommotherplant`, `changegrowthphase`, `additives`, `destroy`. | `/plantbatches/v1/` |
| `create_plant_package_from_batch(data, license_number='', return_obs=False)` | Create a plant package from a batch. | `/plantbatches/v1/create/packages/frommotherplant` |
| `move_batch(data, license_number='', return_obs=False)` | Move plant batch(es). | `/plantbatches/v1/moveplantbatches` |
| `split_batch(data, license_number='', return_obs=False)` | Split a given batch. | `/plantbatches/v1/split` |
| `split_batches(data, license_number='', return_obs=False)` | Split multiple batches. | `/plantbatches/v1/split` |

*Plants*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_plant(data, license_number='', return_obs=False)` | Create a plant. | `/plants/v1/` |
| `create_plants(data, license_number='', return_obs=False)` | Use a plant to create an immature plant batch. | `/plants/v1/` |
| `create_plant_packages(data, license_number='')` | Create plant packages. | `/plants/v1/create/plantbatch/packages` |
| `get_plants(uid='', label='', action='', license_number='', start='', end='')` | Get plant(s). Actions: `vegetative`, `flowering`, `onhold`, `inactive`, `additives`, `additives/types`, `growthphases`, `waste/methods`, `waste/reasons`. | `/plants/v1/` |
| `manage_plants(data, action, license_number='', return_obs=False)` | Manage plant(s) by applying a given action. Actions: `moveplants`, `changegrowthphases`, `destroyplants`, `additives`, `additives/bylocation`, `create/plantings`, `create/plantbatch/packages`, `manicureplants`, `harvestplants`. | `/plants/v1/` |
| `move_plants(data, license_number='', return_obs=False)` | Move multiple plants. | `/plants/v1/moveplants` |

*Sales*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_receipts(uid='', action='active', license_number='', start='', end='', sales_start='', sales_end='')` | Get sale(s). Actions: `active`, `inactive`. | `/sales/v1/receipts/` |
| `get_transactions(license_number='', start='', end='')` | Get transaction(s). | `/sales/v1/transactions/` |
| `get_customer_types(license_number='')` | Get all customer types. | `/sales/v1/customertypes` |
| `create_receipt(data, license_number='', return_obs=False)` | Create a receipt. | `/sales/v1/receipts` |
| `create_receipts(data, license_number='', return_obs=False)` | Create receipt(s). | `/sales/v1/receipts` |
| `update_receipts(data, license_number='', return_obs=False)` | Update receipt(s). | `/sales/v1/receipts` |
| `delete_receipt(uid, license_number='')` | Delete receipt. | `/sales/v1/receipts` |
| `create_transactions(data, date, license_number='', return_obs=False)` | Create transaction(s). | `/sales/v1/transactions` |
| `update_transactions(data, date, license_number='', return_obs=False)` | Update transaction(s). | `/sales/v1/transactions` |

*Strains*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_strains(uid='', action='active', license_number='')` | Get strains. Actions: `active`. | `/strains/v1/` |
| `create_strain(data, license_number='', return_obs=False)` | Create a strain. | `/strains/v1/create` |
| `create_strains(data, license_number='', return_obs=False)` | Create strain(s). | `/strains/v1/create` |
| `update_strain(data, license_number='', return_obs=False)` | Update strain. | `/strains/v1/update` |
| `update_strains(data, license_number='', return_obs=False)` | Update strain(s). | `/strains/v1/update` |
| `delete_strain(uid, license_number='')` | Delete strain. | `/strains/v1/` |

*Transfers*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_transfers(uid='', transfer_type='incoming', license_number='', start='', end='')` | Get transfers. | `/transfers/v1/` |
| `get_transfer_packages(uid, license_number='', action='packages')` | Get shipments. Actions: `packages`, `packages/wholesale`, `requiredlabtestbatches`. | `/transfers/v1/` |
| `get_transfer_types(license_number='')` | Get all transfer types. | `/transfers/v1/types` |
| `get_package_statuses(license_number='')` | Get all package status choices. | `/transfers/v1/delivery/packages/states` |
| `get_transporters(uid)` | Get the data for a transporter. | `/transfers/v1/` |
| `get_transporter_details(uid)` | Get the details of the transporter driver and vehicle. | `/transfers/v1/` |
| `create_transfer(data, license_number='', return_obs=False)` | Create a transfer. | `/transfers/v1/external/incoming` |
| `create_transfers(data, license_number='', return_obs=False)` | Create transfer(s). | `/transfers/v1/external/incoming` |
| `update_transfer(data, license_number='', return_obs=False)` | Update a given transfer. | `/transfers/v1/external/incoming` |
| `update_transfers(data, license_number='', return_obs=False)` | Update transfer(s). | `/transfers/v1/external/incoming` |
| `delete_transfer(uid, license_number='')` | Delete transfer. | `/transfers/v1/external/incoming` |

*Transfer Templates*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_transfer_templates(uid='', action='', license_number='', start='', end='')` | Get transfer template(s). Actions: `deliveries`, `packages`. | `/transfers/v1/templates/` |
| `create_transfer_templates(data, license_number='', return_obs=False)` | Create transfer_template(s). | `/transfers/v1/templates/` |
| `update_transfer_templates(data, license_number='', return_obs=False)` | Update transfer template(s). | `/transfers/v1/templates/` |
| `delete_transfer_template(uid, license_number='')` | Delete transfer template. | `/transfers/v1/templates/` |

*Waste*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_waste_methods(license_number='')` | Get all waste methods for a given license. | `/plants/v1/waste/methods` |
| `get_waste_reasons(license_number='')` | Get all waste reasons for plants for a given license. | `/plants/v1/waste/reasons` |
| `get_waste_types(license_number='')` | Get all waste types for harvests for a given license. | `/harvests/v1/waste/types` |

*Misc*

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_units_of_measure(license_number='')` | Get all units of measurement. | `/unitsofmeasure/v1/active` |
| `import_tags(file_path, row_start=0, row_end=None, number=10)` | Import plant and package tags. | N/A |
| `format_params(**kwargs)` | Format Metrc request parameters. | N/A |

Note the following [rate limits](https://www.metrc.com/wp-content/uploads/2021/10/4-Metrc-Rate-Limiting-1.pdf):
- 50 GET calls per second per facility.
- 150 GET calls per second per vendor API key.
- 10 concurrent GET calls per facility.
- 30 concurrent GET calls per integrator.

## Metrc Models

The `cannlytics.metrc.models` contains common Metrc models. Certain models have methods for self-management. Using the methods of the models in tandem with the `Metrc` client allows for powerful management of your Metrc data.

- `Category` - A class representing an item category.
    ```py
    # When you request a category, you receive the following object.
    {
        "Name": "Buds",
        "ProductCategoryType": "Buds",
        "QuantityType": "WeightBased",
        "RequiresStrain": True,
        "RequiresItemBrand": False,
        "RequiresAdministrationMethod": False,
        "RequiresUnitCbdPercent": False,
        "RequiresUnitCbdContent": False,
        "RequiresUnitCbdContentDose": False,
        "RequiresUnitThcPercent": False,
        "RequiresUnitThcContent": False,
        "RequiresUnitThcContentDose": False,
        "RequiresUnitVolume": False,
        "RequiresUnitWeight": False,
        "RequiresServingSize": False,
        "RequiresSupplyDurationDays": False,
        "RequiresNumberOfDoses": False,
        "RequiresPublicIngredients": False,
        "RequiresDescription": False,
        "RequiresProductPhotos": 0,
        "RequiresLabelPhotos": 0,
        "RequiresPackagingPhotos": 0,
        "CanContainSeeds": True,
        "CanBeRemediated": True,
        "CanBeDestroyed": False
    }
    ```
- `Delivery` - A class that represents a cannabis home delivery. Sales are reported to record the transfer of cannabis products to a consumer, patient or caregiver.
    ```py
    # When you create a receipt, you pass the following object.
    {
        "SalesDateTime": "2016-10-04T16:44:53.000",
        "SalesCustomerType": "Consumer",
        "PatientLicenseNumber": None,
        "CaregiverLicenseNumber": None,
        "IdentificationMethod": None,
        "Transactions": [
            {
                "PackageLabel": "ABCDEF012345670000010331",
                "Quantity": 1.0,
                "UnitOfMeasure": "Ounces",
                "TotalAmount": 9.99
            }
        ]
    }

    # When you request receipts, you receive the following object.
    {
        "Id": 1,
        "ReceiptNumber": None,
        "SalesDateTime": "2016-01-01T17:35:45.000",
        "SalesCustomerType": "Consumer",
        "PatientLicenseNumber": None,
        "CaregiverLicenseNumber": None,
        "IdentificationMethod": None,
        "TotalPackages": 0,
        "TotalPrice": 0.0,
        "Transactions": [],
        "IsFinal": False,
        "ArchivedDate": None,
        "RecordedDateTime": "0001-01-01T00:00:00+00:00",
        "RecordedByUserName": None,
        "LastModified": "0001-01-01T00:00:00+00:00"
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a receipt record in Metrc. |
    | `update(**kwargs)` | Update the receipt given parameters as keyword arguments. |
    | `delete()` | Delete the receipt. |
- `Employee` - An organization's employee or team member.
    ```py
    {
        "FullName": "Keegan Skeate",
        "License": None
    }
    ```
- `Facility` - A Facility represents a building licensed for the growing, processing, and/or selling of product. Facilities are created and have their permissions determined by a state.
    ```py
    {
        "HireDate": "0001-01-01",
        "IsOwner": False,
        "IsManager": True,
        "Occupations": [],
        "Name": "Cultivation LLC",
        "Alias": "Cultivation on Road St",
        "DisplayName": "Cultivation on Road St",
        "CredentialedDate": "1969-08-15",
        "SupportActivationDate": None,
        "SupportExpirationDate": None,
        "SupportLastPaidDate": None,
        "FacilityType": None,
        "License": {
            "Number": "403-X0001",
            "StartDate": "2013-06-28",
            "EndDate": "2015-12-28",
            "LicenseType": "Medical Cultivation"
        }
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `get_locations(uid='', action='')` | Get locations at the facility. Actions: `active`, `types`. |
    | `create_location(name, location_type='default')` | Create a location at the facility. |
    | `create_locations(names, types=[])` | Create locations at the facility. |
    | `update_locations(ids, names, types=[])` | Update locations at the facility. |
    | `delete_location(uid)` | Delete a location at the facility. |
- `Item` - Items are used to track a licensee's inventory at a given facility. The Metrc documentation states, "*Items belong to a single facility. Each item has a unique item name, category, and strain. Item Names are used for identification, so an item name should not simply be a category name. Item names are specific to the item in that package or production batch. Categories are pre-defined. The item name identifies what is in the package and categories are used for grouping similar items for reporting purposes. An item will retain its name unless it is re-packaged.*"
    ```py
    {
        "Id": 1,
        "Name": "Buds",
        "ProductCategoryName": "Buds",
        "ProductCategoryType": "Buds",
        "QuantityType": "WeightBased",
        "DefaultLabTestingState": "NotSubmitted",
        "UnitOfMeasureName": "Ounces",
        "ApprovalStatus": "Approved",
        "ApprovalStatusDateTime": "0001-01-01T00:00:00+00:00",
        "StrainId": 1,
        "StrainName": "Spring Hill Kush",
        "AdministrationMethod": None,
        "UnitCbdPercent": None,
        "UnitCbdContent": None,
        "UnitCbdContentUnitOfMeasureName": None,
        "UnitCbdContentDose": None,
        "UnitCbdContentDoseUnitOfMeasureName": None,
        "UnitThcPercent": None,
        "UnitThcContent": None,
        "UnitThcContentUnitOfMeasureName": None,
        "UnitThcContentDose": None,
        "UnitThcContentDoseUnitOfMeasureName": None,
        "UnitVolume": None,
        "UnitVolumeUnitOfMeasureName": None,
        "UnitWeight": None,
        "UnitWeightUnitOfMeasureName": None,
        "ServingSize": None,
        "SupplyDurationDays": None,
        "NumberOfDoses": None,
        "UnitQuantity": None,
        "UnitQuantityUnitOfMeasureName": None,
        "PublicIngredients": None,
        "Description": None,
        "IsUsed": False
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create()` | Create an item record in Metrc. |
    | `update(**kwargs)` | Update the item given parameters as keyword arguments. |
    | `delete()` | Delete the item. |
- `Location` - A class that represents a cannabis-production location.
    ```py
    {
        "Id": 1,
        "Name": "Harvest Location",
        "LocationTypeId": 1,
        "LocationTypeName": "Default",
        "ForPlantBatches": True,
        "ForPlants": True,
        "ForHarvests": True,
        "ForPackages": True
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `update(**kwargs)` | Update the location. |
    | `delete()` | Delete the location. |
- `Harvest` - A class that represents a cannabis harvest.
    | Method | Description |
    |--------|-------------|
    | `create_package(name, tag, weight, location=None, note='', uom=None)` | Create a package from a harvest. |
    | `create_packages(name, tag, weights, location=None, note='', uom=None)` | Create packages from a harvest. |
    | `create_testing_packages(data)` | Create testing packages from a harvest. |
    | `remove_waste(weight, waste_type='Waste', uom='Grams')` | Remove waste from the harvest. |
    | `finish()` | Finish a harvest. |
    | `unfinish()` | Un-finish a harvest. |
    | `move(destination, harvest_name=None)` | Move a harvest. |
- `Package` - A class that represents a cannabis package.
    | Method | Description |
    |--------|-------------|
    | `create_package(name, tag='', label='', labels=[], weight=0, weights=[], location=None, note='', patient_license=None, uom=None, uoms=[], production_batch=False, donation=False, remediation=False, same_item=False)` | Create a package from a harvest. |
    | `change_item(item_name)` | Change the item of the package. |
    | `finish()` | Finish a package. |
    | `unfinish()` | Un-finish a package. |
    | `adjust(weight, note='', reason='Mandatory State Destruction', uom='Grams')` | Adjust the package. |
    | `remediate(method, steps)` | Remediate the package. |
    | `update_note(note)` | Update the package's note. |
    | `change_location(location)` | Change the package's location. |
    | `update_items(name='', names=[])` | Update the package's item. |
    | `delete()` | Delete the package. |
- `Patient` - A class that represents a cannabis patient.
    ```py
    {
        'PatientId': 1,
        'LicenseNumber': '000001',
        'RegistrationDate': '2015-01-08',
        'LicenseEffectiveStartDate': '2014-07-12',
        'LicenseEffectiveEndDate': '2015-07-07',
        'RecommendedPlants': 6,
        'RecommendedSmokableQuantity': 2.0,
        'HasSalesLimitExemption': False,
        'OtherFacilitiesCount': 1
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a patient record in Metrc. |
    | `update(**kwargs)` | Update the patient given parameters as keyword arguments. |
    | `create()` | Delete the patient. |
- `Plant` - A class that represents a cannabis plant.
    | Method | Description |
    |--------|-------------|
    | `create_planting(name, count, location=None, batch_type='Clone')` | Create an immature plant batch from the plant. |
    | `create_plant_package(name, tag, count=1, batch_type='Clone', trade_sample=False, donation=False, location=None, note='', patient_license=None)` | Create a package of immature plants from the plant. |
    | `flower(tag, location_name=None)` | Change the growth phase of the plant to flowering. |
    | `move(location_name)` | Move the plant to a new location. |
    | `destroy(weight, method='Compost', material='Soil', note='n/a', reason='Contamination', uom='grams')` | Destroy the plant. |
    | `manicure(weight, harvest_name=None, location_name=None, patient_license=None, uom='Grams')` | Manicure the plant. |
    | `harvest(harvest_name, weight, location_name=None, patient_license=None, uom='Grams')` | Harvest the plant. |
- `PlantBatch` - A class that represents a cannabis plant batch.
    ```py
    # When you create a plant batch, you pass the following object.
    {
        "Name": "B. Kush 5-30",
        "Type": "Clone",
        "Count": 25,
        "Strain": "Spring Hill Kush",
        "Location": None,
        "PatientLicenseNumber": "X00001",
        "ActualDate": "2015-12-15"
    }

    # When you request plant batches, you receive the following object.
    {
        "Id": 5,
        "Name": "Demo Plant Batch 1",
        "Type": "Seed",
        "LocationId": None,
        "LocationName": None,
        "LocationTypeName": None,
        "StrainId": 1,
        "StrainName": "Spring Hill Kush",
        "PatientLicenseNumber": None,
        "UntrackedCount": 80,
        "TrackedCount": 10,
        "PackagedCount": 0,
        "HarvestedCount": 0,
        "DestroyedCount": 40,
        "SourcePackageId": None,
        "SourcePackageLabel": None,
        "SourcePlantId": None,
        "SourcePlantLabel": None,
        "SourcePlantBatchId": None,
        "SourcePlantBatchName": None,
        "PlantedDate": "2014-10-10",
        "LastModified": "0001-01-01T00:00:00+00:00"
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create(license_number='')` | Create a plant batch record in Metrc. |
    | `create_package(item_name, tag, count, location='', note='', trade_sample=False, donation=False)` | Create a package from the plant batch. |
    | `create_package_from_mother(tag, item, count, location=None, note='', trade_sample=False, donation=False)` | Create a package from the plant batch mother plant. |
    | `change_growth_phase(tag, count=1, growth_phase='Vegetative', location=None, patient_license=None)` | Change the growth phase of the batch. |
    | `destroy_plants(count, reason)` | Destroy a number of plants for a given reason. |
    | `split(name, count, location=None)` | Split the batch. |
- `LabResult` - A class that represents a cannabis lab result.
    | Method | Description |
    |--------|-------------|
    | `create(data)` | Post lab result data. |
    | `post(data)` | Post lab result data. Equivalent alternative of `create`. |
    | `upload_coa(data)` | Upload lab result CoA. |
    | `release(data)` | Release lab results. |
- `Receipt` - A class that represents a cannabis sale receipt. Sales are reported to record the transfer of cannabis products to a consumer, patient or caregiver.
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a receipt record in Metrc. |
    | `update(**kwargs)` | Update the receipt given parameters as keyword arguments. |
    | `delete()` | Delete the receipt. |
    ```py
    # When you request receipts, you receive the following object.
    {
        "SalesDateTime": "2016-10-04T16:44:53.000",
        "SalesCustomerType": "Consumer",
        "PatientLicenseNumber": None,
        "CaregiverLicenseNumber": None,
        "IdentificationMethod": None,
        "Transactions": [
            {
                "PackageLabel": "ABCDEF012345670000010331",
                "Quantity": 1.0,
                "UnitOfMeasure": "Ounces",
                "TotalAmount": 9.99
            }
        ]
    }

    # When you create a receipt, you pass the following object.
    {
        "Id": 1,
        "ReceiptNumber": None,
        "SalesDateTime": "2016-01-01T17:35:45.000",
        "SalesCustomerType": "Consumer",
        "PatientLicenseNumber": None,
        "CaregiverLicenseNumber": None,
        "IdentificationMethod": None,
        "TotalPackages": 0,
        "TotalPrice": 0.0,
        "Transactions": [],
        "IsFinal": False,
        "ArchivedDate": None,
        "RecordedDateTime": "0001-01-01T00:00:00+00:00",
        "RecordedByUserName": None,
        "LastModified": "0001-01-01T00:00:00+00:00"
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a receipt record in Metrc. |
    | `update(**kwargs)` | Update the receipt given parameters as keyword arguments. |
    | `delete()` | Delete the receipt. |
- `Strain` - A class that represents a cannabis strain.
    ```py
    {
        "Id": 1,
        "Name": "Old-time Moonshine",
        "TestingStatus": "InHouse",
        "ThcLevel": 0.1865,
        "CbdLevel": 0.1075,
        "IndicaPercentage": 25.0,
        "SativaPercentage": 75.0
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a strain record in Metrc. |
    | `update(**kwargs)` | Update the strain given parameters as keyword arguments. |
    | `delete()` | Delete the strain. |
- `Transfer` - A class that represents a cannabis transfer.
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a transfer record in Metrc. |
    | `update(**kwargs)` | Update the transfer given parameters as keyword arguments. |
    | `delete()` | Delete the transfer. |
- `TransferTemplate` -A class that represents a cannabis transfer template. The template can be copied to create other templates. Transfer templates can be used for transfers to the same destination licensee utilizing the same: planned route, transporter(s), driver(s), vehicle(s), and packages.
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a transfer template record in Metrc. |
    | `update(**kwargs)` | Update the transfer template given parameters as keyword arguments. |
    | `delete()` | Delete the transfer template. |
- `Transaction` - A class that represents a cannabis sale transaction.
    ```py
    # When you create a transaction, you pass the following object.
    {
        "PackageId": 71,
        "PackageLabel": "ABCDEF012345670000010331",
        "ProductName": "Shake",
        "ProductCategoryName": None,
        "ItemStrainName": None,
        "ItemUnitCbdPercent": None,
        "ItemUnitCbdContent": None,
        "ItemUnitCbdContentUnitOfMeasureName": None,
        "ItemUnitCbdContentDose": None,
        "ItemUnitCbdContentDoseUnitOfMeasureName": None,
        "ItemUnitThcPercent": None,
        "ItemUnitThcContent": None,
        "ItemUnitThcContentUnitOfMeasureName": None,
        "ItemUnitThcContentDose": None,
        "ItemUnitThcContentDoseUnitOfMeasureName": None,
        "ItemUnitVolume": None,
        "ItemUnitVolumeUnitOfMeasureName": None,
        "ItemUnitWeight": None,
        "ItemUnitWeightUnitOfMeasureName": None,
        "ItemServingSize": None,
        "ItemSupplyDurationDays": None,
        "ItemUnitQuantity": None,
        "ItemUnitQuantityUnitOfMeasureName": None,
        "QuantitySold": 1.0,
        "UnitOfMeasureName": "Ounces",
        "UnitOfMeasureAbbreviation": "oz",
        "TotalPrice": 9.99,
        "SalesDeliveryState": None,
        "ArchivedDate": None,
        "RecordedDateTime": "0001-01-01T00:00:00+00:00",
        "RecordedByUserName": None,
        "LastModified": "0001-01-01T00:00:00+00:00"
    }

    # When you get a transaction, you receive an object as follows.
    {
        "SalesDate": "2015-01-08",
        "TotalTransactions": 40,
        "TotalPackages": 40,
        "TotalPrice": 399.6
    }

    # When you update a transaction, you pass the following object.
    {
        "PackageLabel": "ABCDEF012345670000010331",
        "Quantity": 1.0,
        "UnitOfMeasure": "Ounces",
        "TotalAmount": 9.99
    }
    ```
    | Method | Description |
    |--------|-------------|
    | `create()` | Create a transaction record in Metrc. |
    | `update(**kwargs)` | Update the transaction given parameters as keyword arguments. |
- `Waste` - A class that represents cannabis waste.


## Metrc Constants

| Constant | Description |
|----------|-------------|
| `DEFAULT_HISTORY = 5` | The number of minutes in the past to check the Metrc API when creating and updating objects and returning observations. |
| `additive_types` | Types of additives that may be used during cultivation: `Fertilizer`, `Pesticide`, `Other`.  |
| `adjustment_reasons` | Objects representing reasons for adjusting inventory, e.g. `{'Name': 'Drying', ...}`. |
| `analyses` | State mandated quality control analysis objects, e.g. `{'Name': 'THC', ...}`. |
| `batch_types` | Types of inventory batches, e.g. `Clone`. |
| `categories` | A list of known categories, e.g. `Flower & Buds`. |
| `customer_types` | A list of customer types: `Consumer`, `Patient`, `Caregiver`, and `ExternalPatient`. |
| `growth_phases` | The growth phase of a given plant: `Young`, `Vegetative`, `Flowering`. |
| `item_types` | A list of item objects, e.g. `{'Name': 'Buds', ...}`. |
| `location_types` | A list of location type objects, e.g. `{'Name': 'Default', ...}`. |
| `package_types` | A list of package types, e.g. `{'Name': 'Product', ...}`. |
| `parameters` | A map of keys to Metrc API parameters. |
| `test_statuses` | A list of quality control analysis statuses, e.g. `TestPassed`. |
| `transfer_statuses` | A list of transfer statuses, e.g. `Shipped`. |
| `transfer_types` | A list of transfer type objects, e.g. `{'Name': 'Lab Sample Transfer', ...}`. |
| `units` | A list of unit objects, e.g. `{'Name': 'WeightBased, ...}`. |
| `waste_methods` | A list of waste method objects, e.g. `{'Name': 'Grinder'}`. |
| `waste_reasons` | A list of wast reason objects, e.g. `{'Name': 'Disease/Infestation', ...}`. |
| `waste_types` | A state-by-state map to lists of waste types, e.g. `{'ca': ['Plant Material'], ...}`. |

<!-- ## Metrc URLs
Available Metrc endpoints are found in `cannlytics.metrc.urls`. -->

## References

| State | Documentation |
|-------|---------------|
| [Alaska](https://www.metrc.com/partner/alaska/) | <https://api-ak.metrc.com/Documentation> |
| [California](https://www.metrc.com/partner/california/) | <https://api-ca.metrc.com/Documentation> |
| [Colorado](https://www.metrc.com/partner/colorado/) | <https://api-co.metrc.com/Documentation> |
| [Louisiana](https://www.metrc.com/partner/louisiana/) | <https://api-la.metrc.com/Documentation> |
| [Maine](https://www.metrc.com/partner/maine/) | <https://api-me.metrc.com/Documentation> |
| [Maryland](https://www.metrc.com/partner/maryland/) | <https://api-md.metrc.com/Documentation> |
| [Massachusetts](https://www.metrc.com/partner/massachusetts/) | <https://api-ma.metrc.com/Documentation> |
| [Michigan](https://www.metrc.com/partner/michigan/) | <https://api-mi.metrc.com/Documentation> |
| [Minnesota](https://www.metrc.com/partner/minnesota/) | <https://api-mn.metrc.com/Documentation> |
| [Mississippi](https://www.metrc.com/partner/mississippi/) | <https://api-ms.metrc.com/Documentation> |
| [Missouri](https://www.metrc.com/partner/missouri/) | <https://api-mo.metrc.com/Documentation> |
| [Montana](https://www.metrc.com/partner/montana/) | <https://api-mt.metrc.com/Documentation> |
| [Nevada](https://www.metrc.com/partner/nevada/) | <https://api-nv.metrc.com/Documentation> |
| [Ohio](https://www.metrc.com/partner/ohio/) | <https://api-oh.metrc.com/Documentation> |
| [Oklahoma](https://www.metrc.com/partner/oklahoma/) | <https://api-ok.metrc.com/Documentation> |
| [Oregon](https://www.metrc.com/partner/oregon/) | <https://api-or.metrc.com/Documentation> |
| [South Dakota](https://www.metrc.com/partner/south-dakota/) | <https://api-sd.metrc.com/Documentation> |
| [West Virginia](https://www.metrc.com/partner/west-virginia/) | <https://api-wv.metrc.com/Documentation> |
