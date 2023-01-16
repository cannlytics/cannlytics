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

*Contents*
- [Metrc](#metrc)
- [Facilities and Employees](#facilities-and-employees)
- [Category](#category)
- [Deliveries](#deliveries)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
- [](#)
<!--
Harvests
Items
Lab Results
Locations
Packages
Patients
Plant Batches
Plants
Sales
Strains
Transfers
Transfer Templates
Types
-->


## Example

```py
from cannlytics import metrc

# Initialize a Metrc API client.
track = Metrc(
    'your-vendor-api-key',
    'your-user-api-key',
    primary_license='123',
    state='ok',
    logs=True,
    test=False,
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

## Metrc

The tables below contain all of the methods of the `Metrc` class found in `cannlytics.metrc.client`. The following arguments are treated similarly in each method:

- You can specify `license_number` to perform operations for a specific licensee.

- Methods that create or update data accept an optional argument `return_obs` for you to specify if you wish for the created or updated data to be returned. This requires subsequent requests to the Metrc API, because the default behavior is for create or update methods to return `None`.

- Methods to get data usually accept a `uid` argument for you to specify a specific Metrc tag or label.

- For queryable objects, you can pass ISO-formatted times to `start` and `end` arguments to get data for a specific day.

- You can specify `action` where applicable to perform the functionality of various model types.

Note that Metrc has the following [rate limits](https://www.metrc.com/wp-content/uploads/2021/10/4-Metrc-Rate-Limiting-1.pdf):
- 50 GET calls per second per facility.
- 150 GET calls per second per vendor API key.
- 10 concurrent GET calls per facility.
- 30 concurrent GET calls per integrator.

The `cannlytics.metrc.models` submodule contains common Metrc models. Certain models have methods for self-management. Using the methods of the models in tandem with the `Metrc` client allows for powerful management of your Metrc data.

## Facilities and Employees

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_employees(license_number='')` | Get all employees. | `/employees/v1/`|
| `get_facilities()` | Get all facilities. | `/employees/v1/`|
| `get_facility(license_number='')` | Get a given facility by its license number. | `/employees/v1/`|

## Deliveries

The `Delivery` class represents a cannabis home delivery. Sales are reported to record the transfer of cannabis products to a consumer, patient or caregiver. The class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a receipt record in Metrc. |
| `update(**kwargs)` | Update the receipt given parameters as keyword arguments. |
| `delete()` | Delete the receipt. |

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

The `Metrc` class has the following methods for managing deliveries.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_deliveries(data, license_number='', return_obs=False)` | Create home deliver(ies). | `/sales/v1/deliveries` |
| `get_deliveries(uid='', action='active', license_number='', start='', end='', sales_start='', sales_end='')` | Get sale(s). Actions: `active`, `inactive`. | `/sales/v1/deliveries` |
| `get_return_reasons(license_number='')` | Get the possible return reasons for home delivery items. | `/sales/v1/deliveries/delivery/returnreasons` |
| `complete_deliveries(data, license_number='')` | Complete home delivery(ies). | `/sales/v1/deliveries` |
| `delete_delivery(uid, license_number='')` | Delete a home delivery. | `/sales/v1/deliveries` |
| `update_deliveries(data, license_number='')` | Update home delivery(ies). | `/sales/v1/deliveries` |

## Harvests

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_harvests(uid='', action='active', license_number='', start='', end='')` | Get harvests. Actions: `active`, `onhold`, `inactive`, `waste/types`. | `/harvests/v1/` |
| `finish_harvests(data, license_number='')` | Finish harvests. | `/harvests/v1/finish` |
| `unfinish_harvests(data, license_number='')` | Unfinish harvests. | `/harvests/v1/unfinish` |
| `remove_waste(data, license_number='')` | Remove's waste from a harvest. | `/harvests/v1/removewaste` |
| `move_harvests(data, license_number='')` | Move a harvests. | `/harvests/v1/move` |
| `create_harvest_packages(data, license_number='', return_obs=False)` | Create packages from a harvest. | `/harvests/v1/create/packages` |
| `create_harvest_testing_packages(data, license_number='', return_obs=False)` | Create packages from a harvest for testing. | `/harvests/v1/create/packages/testing` |

## Items

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

## Lab Results

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_lab_results(uid='', license_number='')` | Get lab results. | `/labtests/v1/results` |
| `get_test_types(license_number='')` | Get required quality assurance analyses. | `/labtests/v1/types` |
| `get_test_statuses(license_number='')` | Get pre-defined lab statuses. | `/labtests/v1/states` |
| `post_lab_results(data, license_number='', return_obs=False)` | Post lab result(s). | `/labtests/v1/record` |
| `upload_coas(data, license_number='')` | Upload lab result CoA(s). | `/labtests/v1/labtestdocument` |
| `release_lab_results(data, license_number='')` | Release lab result(s). | `/labtests/v1/results/release` |

## Locations

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_location_types(license_number='')` | Get all location types for a given license. | `/locations/v1/types` |
| `get_location(uid='', license_number='')` | Get a location. | `/locations/v1/` |
| `get_locations(uid='', action='active', license_number='')` | Get locations. Action: `active`, `types`. | `/locations/v1/` |
| `create_location(name, location_type='default', license_number='', return_obs=False)` | Create location. | `/locations/v1/create` |
| `create_locations(names, types=[], license_number='', return_obs=False)` | Create location(s). | `/locations/v1/create` |
| `update_locations(data, license_number='', return_obs=False)` | Update location(s). | `/locations/v1/update` |
| `delete_location(uid, license_number='')` | Delete location. | `/locations/v1/` |

## Packages

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
| `change_package_locations(data, license_number='', return_obs=False)` | Update package item location(s). | `/packages/v1/change/locations` |
| `manage_packages(data, action='adjust', license_number='', return_obs=False)` | Adjust package(s). Actions: `adjust`, `finish`, `unfinish`, `remediate`. | `/packages/v1/` |
| `update_package_notes(data, license_number='', return_obs=False)` | Update package note(s). | `/packages/v1/change/note` |

## Patients

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_patients(uid='', action='active', license_number='')` | Get licensee member patients. Action: `active`. | `/patients/v1/` |
| `create_patients(data, license_number='', return_obs=False)` | Create patient(s). | `/patients/v1/` |
| `update_patients(data, license_number='', return_obs=False)` | Update strain(s). | `/patients/v1/` |
| `delete_patient(uid, license_number='')` | Delete patient. | `/patients/v1/` |

## Plant Batches

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

## Plants

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_plant(data, license_number='', return_obs=False)` | Create a plant. | `/plants/v1/` |
| `create_plants(data, license_number='', return_obs=False)` | Use a plant to create an immature plant batch. | `/plants/v1/` |
| `create_plant_packages(data, license_number='')` | Create plant packages. | `/plants/v1/create/plantbatch/packages` |
| `get_plants(uid='', label='', action='', license_number='', start='', end='')` | Get plant(s). Actions: `vegetative`, `flowering`, `onhold`, `inactive`, `additives`, `additives/types`, `growthphases`, `waste/methods`, `waste/reasons`. | `/plants/v1/` |
| `manage_plants(data, action, license_number='', return_obs=False)` | Manage plant(s) by applying a given action. Actions: `moveplants`, `changegrowthphases`, `destroyplants`, `additives`, `additives/bylocation`, `create/plantings`, `create/plantbatch/packages`, `manicureplants`, `harvestplants`. | `/plants/v1/` |
| `move_plants(data, license_number='', return_obs=False)` | Move multiple plants. | `/plants/v1/moveplants` |

## Sales

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

## Strains

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_strains(uid='', action='active', license_number='')` | Get strains. Actions: `active`. | `/strains/v1/` |
| `create_strain(data, license_number='', return_obs=False)` | Create a strain. | `/strains/v1/create` |
| `create_strains(data, license_number='', return_obs=False)` | Create strain(s). | `/strains/v1/create` |
| `update_strain(data, license_number='', return_obs=False)` | Update strain. | `/strains/v1/update` |
| `update_strains(data, license_number='', return_obs=False)` | Update strain(s). | `/strains/v1/update` |
| `delete_strain(uid, license_number='')` | Delete strain. | `/strains/v1/` |

## Transfers

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

## Transfer Templates

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_transfer_templates(uid='', action='', license_number='', start='', end='')` | Get transfer template(s). Actions: `deliveries`, `packages`. | `/transfers/v1/templates/` |
| `create_transfer_templates(data, license_number='', return_obs=False)` | Create transfer_template(s). | `/transfers/v1/templates/` |
| `update_transfer_templates(data, license_number='', return_obs=False)` | Update transfer template(s). | `/transfers/v1/templates/` |
| `delete_transfer_template(uid, license_number='')` | Delete transfer template. | `/transfers/v1/templates/` |

## Types

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_waste_methods(license_number='')` | Get all waste methods for a given license. | `/plants/v1/waste/methods` |
| `get_waste_reasons(license_number='')` | Get all waste reasons for plants for a given license. | `/plants/v1/waste/reasons` |
| `get_waste_types(license_number='')` | Get all waste types for harvests for a given license. | `/harvests/v1/waste/types` |
| `get_units_of_measure(license_number='')` | Get all units of measurement. | `/unitsofmeasure/v1/active` |

## Miscellaneous methods

| Method | Description | Endpoint |
|--------|-------------|----------|
| `import_tags(file_path, row_start=0, row_end=None, number=10)` | Import plant and package tags. | N/A |

## Constants

The following constants are found in `cannlytics.metrc.constants`. Available Metrc endpoints are found in `cannlytics.metrc.urls`.

| Constant | Description |
|----------|-------------|
| `DEFAULT_HISTORY` | The number of minutes (5 by default) in the past to check the Metrc API when creating and updating objects and returning observations. |
| `parameters` | A map of keys to Metrc API parameters. |

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
