# Cannlytics Metrc Module

<div align="center" style="text-align:center; margin-top:1rem; margin-bottom: 1rem;">
  <img width="150px" alt="" src="https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_metrc_logo.png?alt=media&token=8087c714-c03f-47f1-9196-7353cc887ead">
</div>

[Metrc](https://metrc.com) is the predominant tracking and traceability system mandated for use by cannabis licensees in the majority of states that permit cannabis markets. Cannabis licensees and verified software integrators use Metrc to compliantly track cannabis at each point of the supply chain. You can use the `cannlytics.metrc` module to securely interface with the Metrc API and perform all operations needed for compliance. Simply plug in your vendor and user API keys, specify your state of operations, and you're off to the races.

*Contents*

- [Metrc](#metrc)
- [Facilities and Employees](#facilities-and-employees)
- [Locations](#locations)
- [Strains](#strains)
- [Categories](#Categories)
- [Plants](#plants)
- [Plant Batches](#plant-batches)
- [Harvests](#Harvests)
- [Packages](#packages)
- [Items](#items)
- [Transfers](#transfers)
- [Transfer Templates](#transfer-templates)
- [Lab Results](#lab-results)
- [Patients](#patients)
- [Sales](#sales)
- [Deliveries](#deliveries)
- [Types](#types)
- [Examples](#examples)
- [References](#references)

## Metrc

The `Metrc` class found in `cannlytics.metrc.client` is initialized with a Metrc vendor API Key, a Metrc user API key, an optional `primary_license`, the `state` abbreviation, e.g. `'ok'` for Oklahoma, whether or not to print to a log file, `logs`, and whether or not to perform the requests in the sandbox, `test`.

```py
from cannlytics.metrc import Metrc

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

The following arguments are treated similarly in each method of the `Metrc` class:

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

The `Facility` class represents a building licensed for the growing, processing, and/or selling of product. Facilities are created and have their permissions determined by a state.

```py
from cannlytics.metrc.models import Facility

# Example facility.
facility = Facility.from_dict({
  'hire_date': '2022-04-20',
  'is_owner': False,
  'is_manager': True,
  'occupations': [],
  'name': 'Cultivation LLC',
  'alias': 'Cultivation on Road St',
  'display_name': 'Cultivation on Road St',
  'credentialed_date': '1969-08-15',
  'support_activation_date': None,
  'support_expiration_date': None,
  'support_last_paid_date': None,
  'facility_type': None,
  'license': {
    'number': '403-X0001',
    'start_date': '2013-06-28',
    'end_date': '2015-12-28',
    'license_type': 'Medical Cultivation'
  }
})
```

The `Facility` class has the following methods.

| Method | Description |
|--------|-------------|
| `get_locations(uid='', action='')` | Get locations at the facility. Actions: `active`, `types`. |
| `create_location(name, location_type='default')` | Create a location at the facility. |
| `create_locations(names, types=[])` | Create locations at the facility. |
| `update_locations(ids, names, types=[])` | Update locations at the facility. |
| `delete_location(uid)` | Delete a location at the facility. |

The `Employee` class represents an organization's employee or team member.

```py
from cannlytics.metrc.models import Employee

# Example employee.
employee = Employee.from_dict({
    'full_name': 'Bud S. Moker',
    'license': None
})
```

The `Employee` class has the following methods.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_employees(license_number='')` | Get all employees. | `/employees/v1/`|
| `get_facilities()` | Get all facilities. | `/employees/v1/`|
| `get_facility(license_number='')` | Get a given facility by its license number. | `/employees/v1/`|

## Locations

The `Location` class represents a cannabis-production location.

```py
from cannlytics.metrc.models import Location

# When you request a location, you receive the following object.
location = Location.from_dict({
  'id': 1,
  'name': 'Harvest Location',
  'location_type_id': 1,
  'location_type_name': 'Default',
  'for_plant_batches': True,
  'for_plants': True,
  'for_harvests': True,
  'for_packages': True
})
```

The `Location` class has the following methods.

| Method | Description |
|--------|-------------|
| `update(**kwargs)` | Update the location. |
| `delete()` | Delete the location. |

The `Metrc` class has the following methods for managing locations.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_location_types(license_number='')` | Get all location types for a given license. | `/locations/v1/types` |
| `get_location(uid='', license_number='')` | Get a location. | `/locations/v1/` |
| `get_locations(uid='', action='active', license_number='')` | Get locations. Action: `active`, `types`. | `/locations/v1/` |
| `create_location(name, location_type='default', license_number='', return_obs=False)` | Create location. | `/locations/v1/create` |
| `create_locations(names, types=[], license_number='', return_obs=False)` | Create location(s). | `/locations/v1/create` |
| `update_locations(data, license_number='', return_obs=False)` | Update location(s). | `/locations/v1/update` |
| `delete_location(uid, license_number='')` | Delete location. | `/locations/v1/` |

## Strains

The `Strain` class represents a cannabis strain.

```py
from cannlytics.metrc.models import Strain

# When you request a strain, you receive the following object.
strain = Strain.from_dict({
  'id': 1,
  'name': 'Old-time Moonshine',
  'testing_status': 'InHouse',
  'thc_level': 0.1865,
  'cbd_level': 0.1075,
  'indica_percentage': 25.0,
  'sativa_percentage': 75.0
})
```

The `Strain` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a strain record in Metrc. |
| `update(**kwargs)` | Update the strain given parameters as keyword arguments. |
| `delete()` | Delete the strain. |

The `Metrc` class has the following methods for managing strains.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_strains(uid='', action='active', license_number='')` | Get strains. Actions: `active`. | `/strains/v1/` |
| `create_strain(data, license_number='', return_obs=False)` | Create a strain. | `/strains/v1/create` |
| `create_strains(data, license_number='', return_obs=False)` | Create strain(s). | `/strains/v1/create` |
| `update_strain(data, license_number='', return_obs=False)` | Update strain. | `/strains/v1/update` |
| `update_strains(data, license_number='', return_obs=False)` | Update strain(s). | `/strains/v1/update` |
| `delete_strain(uid, license_number='')` | Delete strain. | `/strains/v1/` |

## Categories

The `Category` class represents an item category. Categories are pre-defined by Metrc by state. Categories are used for grouping similar items for reporting purposes.

```py
from cannlytics.metrc.models import Category

# When you request a category, you receive the following object.
category = Category.from_dict({
  'name': 'Buds',
  'product_category_type': 'Buds',
  'quantity_type': 'WeightBased',
  'requires_strain': True,
  'requires_item_brand': False,
  'requires_administration_method': False,
  'requires_unit_cbd_percent': False,
  'requires_unit_cbd_content': False,
  'requires_unit_cbd_content_dose': False,
  'requires_unit_thc_percent': False,
  'requires_unit_thc_content': False,
  'requires_unit_thc_content_dose': False,
  'requires_unit_volume': False,
  'requires_unit_weight': False,
  'requires_serving_size': False,
  'requires_supply_duration_days': False,
  'requires_number_of_doses': False,
  'requires_public_ingredients': False,
  'requires_description': False,
  'requires_product_photos': 0,
  'requires_label_photos': 0,
  'requires_packaging_photos': 0,
  'can_contain_seeds': True,
  'can_be_remediated': True,
  'can_be_destroyed': False
})
```

## Plants

The `Plant` class represents a cannabis plant.

```py
from cannlytics.metrc.models import Plant

# When you request a plant, you receive the following object.
plant = Plant.from_dict({
  'id': 24,
  'label': 'ABCDEF012345670000000024',
  'state': 'Tracked',
  'growth_phase': 'Vegetative',
  'plant_batch_id': 1,
  'plant_batch_name': 'Demo Plant Batch',
  'plant_batch_type_id': 1,
  'plant_batch_type_name': 'Seed',
  'strain_id': 1,
  'strain_name': 'Spring Hill Kush',
  'location_id': 2,
  'location_name': 'Plants Location',
  'location_type_name': None,
  'patient_license_number': None,
  'harvest_id': None,
  'harvested_unit_of_weight_name': None,
  'harvested_unit_of_weight_abbreviation': None,
  'harvested_wet_weight': None,
  'harvest_count': 0,
  'is_on_hold': False,
  'is_on_trip': False,
  'planted_date': '2014-10-10',
  'vegetative_date': '2014-10-20',
  'flowering_date': None,
  'harvested_date': None,
  'destroyed_date': None,
  'destroyed_note': None,
  'destroyed_by_user_name': None,
  'last_modified': '0001-01-01T00:00:00+00:00'
})
```

The `Plant` class has the following methods.

| Method | Description |
|--------|-------------|
| `create_planting(name, count, location=None, batch_type='Clone')` | Create an immature plant batch from the plant. |
| `create_plant_package(name, tag, count=1, batch_type='Clone', trade_sample=False, donation=False, location=None, note='', patient_license=None)` | Create a package of immature plants from the plant. |
| `flower(tag, location_name=None)` | Change the growth phase of the plant to flowering. |
| `move(location_name)` | Move the plant to a new location. |
| `destroy(weight, method='Compost', material='Soil', note='n/a', reason='Contamination', uom='grams')` | Destroy the plant. |
| `manicure(weight, harvest_name=None, location_name=None, patient_license=None, uom='Grams')` | Manicure the plant. |
| `harvest(harvest_name, weight, location_name=None, patient_license=None, uom='Grams')` | Harvest the plant. |

The `Metrc` class has the following methods for managing plants.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_plant(data, license_number='', return_obs=False)` | Create a plant. | `/plants/v1/` |
| `create_plants(data, license_number='', return_obs=False)` | Use a plant to create an immature plant batch. | `/plants/v1/` |
| `create_plant_packages(data, license_number='')` | Create plant packages. | `/plants/v1/create/plantbatch/packages` |
| `get_plants(uid='', label='', action='', license_number='', start='', end='')` | Get plant(s). Actions: `vegetative`, `flowering`, `onhold`, `inactive`, `additives`, `additives/types`, `growthphases`, `waste/methods`, `waste/reasons`. | `/plants/v1/` |
| `manage_plants(data, action, license_number='', return_obs=False)` | Manage plant(s) by applying a given action. Actions: `moveplants`, `changegrowthphases`, `destroyplants`, `additives`, `additives/bylocation`, `create/plantings`, `create/plantbatch/packages`, `manicureplants`, `harvestplants`. | `/plants/v1/` |
| `move_plants(data, license_number='', return_obs=False)` | Move multiple plants. | `/plants/v1/moveplants` |

## Plant Batches

The `PlantBatch` class represents a cannabis plant batch.

```py
from cannlytics.metrc.models import PlantBatch

# When you request plant batches, you receive the following object.
batch = PlantBatch.from_dict({
  'id': 5,
  'name': 'Demo Plant Batch 1',
  'type': 'Seed',
  'location_id': None,
  'location_name': None,
  'location_type_name': None,
  'strain_id': 1,
  'strain_name': 'Spring Hill Kush',
  'patient_license_number': None,
  'untracked_count': 80,
  'tracked_count': 10,
  'packaged_count': 0,
  'harvested_count': 0,
  'destroyed_count': 40,
  'source_package_id': None,
  'source_package_label': None,
  'source_plant_id': None,
  'source_plant_label': None,
  'source_plant_batch_id': None,
  'source_plant_batch_name': None,
  'planted_date': '2014-10-10',
  'last_modified': '0001-01-01T00:00:00+00:00'
})

# When you create a plant batch, you pass the following object.
batch = PlantBatch.from_dict({
  'name': 'B. Kush 5-30',
  'type': 'Clone',
  'count': 25,
  'strain': 'Spring Hill Kush',
  'location': None,
  'patient_license_number': 'X00001',
  'actual_date': '2015-12-15'
})
```

The `PlantBatch` class has the following methods.

| Method | Description |
|--------|-------------|
| `create(license_number='')` | Create a plant batch record in Metrc. |
| `create_package(item_name, tag, count, location='', note='', trade_sample=False, donation=False)` | Create a package from the plant batch. |
| `create_package_from_mother(tag, item, count, location=None, note='', trade_sample=False, donation=False)` | Create a package from the plant batch mother plant. |
| `change_growth_phase(tag, count=1, growth_phase='Vegetative', location=None, patient_license=None)` | Change the growth phase of the batch. |
| `destroy_plants(count, reason)` | Destroy a number of plants for a given reason. |
| `split(name, count, location=None)` | Split the batch. |

The `Metrc` class has the following methods for managing plant batches.

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

## Harvests

The `Harvest` class represents a cannabis harvest.

```py
from cannlytics.metrc.models import Harvest

# When you request a harvest, you receive the following object.
harvest = Harvest.from_dict({
  'id': 1,
  'name': '2022-04-20-Harvest Location-M',
  'harvest_type': 'Product',
  'source_strain_count': 0,
  'source_strain_names': None,
  'strains': [],
  'drying_location_id': 1,
  'drying_location_name': 'Harvest Location',
  'drying_location_type_name': None,
  'patient_license_number': None,
  'current_weight': 0.0,
  'total_waste_weight': 0.0,
  'plant_count': 70,
  'total_wet_weight': 40.0,
  'total_restored_weight': 0.0,
  'package_count': 5,
  'total_packaged_weight': 0.0,
  'unit_of_weight_name': 'Ounces',
  'lab_testing_state': None,
  'lab_testing_state_date': None,
  'is_on_hold': False,
  'harvest_start_date': '2022-04-20',
  'finished_date': None,
  'archived_date': None,
  'is_on_trip': False,
  'last_modified': '2022-04-20T00:00:00+00:00'
})
```

The `Harvest` class has the following methods.

| Method | Description |
|--------|-------------|
| `create_package(name, tag, weight, location=None, note='', uom=None)` | Create a package from a harvest. |
| `create_packages(name, tag, weights, location=None, note='', uom=None)` | Create packages from a harvest. |
| `create_testing_packages(data)` | Create testing packages from a harvest. |
| `remove_waste(weight, waste_type='Waste', uom='Grams')` | Remove waste from the harvest. |
| `finish()` | Finish a harvest. |
| `unfinish()` | Un-finish a harvest. |
| `move(destination, harvest_name=None)` | Move a harvest. |

The `Metrc` class has the following methods for managing harvests.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_harvests(uid='', action='active', license_number='', start='', end='')` | Get harvests. Actions: `active`, `onhold`, `inactive`, `waste/types`. | `/harvests/v1/` |
| `finish_harvests(data, license_number='')` | Finish harvests. | `/harvests/v1/finish` |
| `unfinish_harvests(data, license_number='')` | Unfinish harvests. | `/harvests/v1/unfinish` |
| `remove_waste(data, license_number='')` | Remove's waste from a harvest. | `/harvests/v1/removewaste` |
| `move_harvests(data, license_number='')` | Move a harvests. | `/harvests/v1/move` |
| `create_harvest_packages(data, license_number='', return_obs=False)` | Create packages from a harvest. | `/harvests/v1/create/packages` |
| `create_harvest_testing_packages(data, license_number='', return_obs=False)` | Create packages from a harvest for testing. | `/harvests/v1/create/packages/testing` |

## Packages

The `Package` class represents a cannabis package.

```py
from cannlytics.metrc.models import Package

# When you request a package, you receive the following object.
package = Package.from_dict({
  'id': 2,
  'label': 'ABCDEF012345670000010042',
  'package_type': 'Product',
  'source_harvest_count': 0,
  'source_package_count': 0,
  'source_processing_job_count': 0,
  'source_harvest_names': None,
  'location_id': None,
  'location_name': None,
  'location_type_name': None,
  'quantity': 1.0,
  'unit_of_measure_name': 'Ounces',
  'unit_of_measure_abbreviation': 'oz',
  'patient_license_number': None,
  'item_from_facility_license_number': None,
  'item_from_facility_name': None,
  'note': None,
  'packaged_date': '2014-11-29',
  'initial_lab_testing_state': 'NotSubmitted',
  'lab_testing_state': 'NotSubmitted',
  'lab_testing_state_date': '2014-11-29',
  'is_production_batch': False,
  'production_batch_number': None,
  'source_production_batch_numbers': None,
  'is_trade_sample': False,
  'is_trade_sample_persistent': False,
  'source_package_is_trade_sample': False,
  'is_donation': False,
  'is_donation_persistent': False,
  'source_package_is_donation': False,
  'is_testing_sample': False,
  'is_process_validation_testing_sample': False,
  'product_requires_remediation': False,
  'contains_remediated_product': False,
  'remediation_date': None,
  'received_date_time': None,
  'received_from_manifest_number': None,
  'received_from_facility_license_number': None,
  'received_from_facility_name': None,
  'is_on_hold': False,
  'archived_date': None,
  'finished_date': None,
  'is_on_trip': False,
  'package_for_product_destruction': None,
  'last_modified': '2023-01-18T01:10:10.3436996+00:00',
  'item': {
    'id': 1,
    'name': 'Buds',
    'product_category_name': 'Buds',
    'product_category_type': 0,
    'quantity_type': 0,
    'default_lab_testing_state': 0,
    'unit_of_measure_name': None,
    'approval_status': 0,
    'approval_status_date_time': '0001-01-01T00:00:00+00:00',
    'strain_id': None,
    'strain_name': None,
    'administration_method': None,
    'unit_cbd_percent': None,
    'unit_cbd_content': None,
    'unit_cbd_content_unit_of_measure_name': None,
    'unit_cbd_content_dose': None,
    'unit_cbd_content_dose_unit_of_measure_name': None,
    'unit_thc_percent': None,
    'unit_thc_content': None,
    'unit_thc_content_unit_of_measure_name': None,
    'unit_thc_content_dose': None,
    'unit_thc_content_dose_unit_of_measure_name': None,
    'unit_volume': None,
    'unit_volume_unit_of_measure_name': None,
    'unit_weight': None,
    'unit_weight_unit_of_measure_name': None,
    'serving_size': None,
    'supply_duration_days': None,
    'number_of_doses': None,
    'unit_quantity': None,
    'unit_quantity_unit_of_measure_name': None,
    'public_ingredients': None,
    'description': None,
    'product_images': [],
    'label_images': [],
    'packaging_images': [],
    'is_used': False
  }
})

# When you create a package, you pass the following object.
package = Package.from_dict({
  'tag': 'ABCDEF012345670000020201',
  'location': None,
  'item': 'Buds',
  'quantity': 16.0,
  'unit_of_measure': 'Ounces',
  'patient_license_number': 'X00001',
  'note': 'This is a note.',
  'is_production_batch': False,
  'production_batch_number': None,
  'is_donation': False,
  'is_trade_sample': False,
  'product_requires_remediation': False,
  'use_same_item': False,
  'actual_date': '2015-12-15',
  'required_lab_test_batches': None,
  'ingredients': [
    {
      'package': 'ABCDEF012345670000010041',
      'quantity': 8.0,
      'unit_of_measure': 'Ounces'
    },
  ]
})
```

The `Package` class has the following methods.

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

The `Metrc` class has the following methods for managing packages.

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

## Items

The `Item` class is used to track a licensee's inventory at a given facility. Items belong to a single facility. Each item has a unique item name, category, and strain. Item names are used for identification, so an item name should not simply be a category name. Item names are specific to the item in that package or production batch. The item name identifies what is in the package. An item will retain its name unless it is re-packaged.*'

```py
from cannlytics.metrc.models import Item

# When you request an item, you receive the following object.
item = Item.from_dict({
  'id': 1,
  'name': 'Buds',
  'product_category_name': 'Buds',
  'product_category_type': 'Buds',
  'quantity_type': 'WeightBased',
  'default_lab_testing_state': 'NotSubmitted',
  'unit_of_measure_name': 'Ounces',
  'approval_status': 'Approved',
  'approval_status_date_time': '0001-01-01T00:00:00+00:00',
  'strain_id': 1,
  'strain_name': 'Spring Hill Kush',
  'administration_method': None,
  'unit_cbd_percent': None,
  'unit_cbd_content': None,
  'unit_cbd_content_unit_of_measure_name': None,
  'unit_cbd_content_dose': None,
  'unit_cbd_content_dose_unit_of_measure_name': None,
  'unit_thc_percent': None,
  'unit_thc_content': None,
  'unit_thc_content_unit_of_measure_name': None,
  'unit_thc_content_dose': None,
  'unit_thc_content_dose_unit_of_measure_name': None,
  'unit_volume': None,
  'unit_volume_unit_of_measure_name': None,
  'unit_weight': None,
  'unit_weight_unit_of_measure_name': None,
  'serving_size': None,
  'supply_duration_days': None,
  'number_of_doses': None,
  'unit_quantity': None,
  'unit_quantity_unit_of_measure_name': None,
  'public_ingredients': None,
  'description': None,
  'is_used': False
})
```

The `Item` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create an item record in Metrc. |
| `update(**kwargs)` | Update the item given parameters as keyword arguments. |
| `delete()` | Delete the item. |

The `Metrc` class has the following methods for managing items.

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

## Transfers

The `Transfer` class represents a cannabis transfer.

```py
from cannlytics.metrc.models import Transfer

# When you request a transfer, you receive the following object.
transfer = Transfer.from_dict({
  'id': 1,
  'manifest_number': '0000000001',
  'shipment_license_type': 0,
  'shipper_facility_license_number': '123-ABC',
  'shipper_facility_name': 'Lofty Med-Cultivation B',
  'name': None,
  'transporter_facility_license_number': '123-BCD',
  'transporter_facility_name': 'Lofty Med-Dispensary',
  'driver_name': 'X',
  'driver_occupational_license_number': '',
  'driver_vehicle_license_number': '',
  'vehicle_make': 'X',
  'vehicle_model': 'X',
  'vehicle_license_plate_number': 'X',
  'delivery_count': 0,
  'received_delivery_count': 0,
  'package_count': 7,
  'received_package_count': 0,
  'contains_plant_package': False,
  'contains_product_package': False,
  'contains_trade_sample': False,
  'contains_donation': False,
  'contains_testing_sample': False,
  'contains_product_requires_remediation': False,
  'contains_remediated_product_package': False,
  'created_date_time': '2016-10-10T08:20:45-05:00',
  'created_by_user_name': None,
  'last_modified': '0001-01-01T00:00:00+00:00',
  'delivery_id': 1,
  'recipient_facility_license_number': '123-ABC',
  'recipient_facility_name': 'Lofty Med-Cultivation A',
  'shipment_type_name': 'Transfer',
  'shipment_transaction_type': 'Standard',
  'estimated_departure_date_time': '2016-10-11T14:48:30.000',
  'actual_departure_date_time': None,
  'estimated_arrival_date_time': '2016-10-11T16:50:00.000',
  'actual_arrival_date_time': None,
  'delivery_package_count': 7,
  'delivery_received_package_count': 0,
  'received_date_time': '2016-10-11T16:42:19-05:00',
  'estimated_return_departure_date_time': None,
  'actual_return_departure_date_time': None,
  'estimated_return_arrival_date_time': None,
  'actual_return_arrival_date_time': None
})

# When you create transfers, you pass the following object.
transfer = Transfer.from_dict({
  'shipper_license_number': '123-ABC',
  'shipper_name': 'Lofty Med-Cultivation B',
  'shipper_main_phone_number': '123-456-7890',
  'shipper_address1': '123 Real Street',
  'shipper_address2': None,
  'shipper_address_city': 'Somewhere',
  'shipper_address_state': 'CO',
  'shipper_address_postal_code': None,
  'transporter_facility_license_number': None,
  'driver_occupational_license_number': None,
  'driver_name': None,
  'driver_license_number': None,
  'phone_number_for_questions': None,
  'vehicle_make': None,
  'vehicle_model': None,
  'vehicle_license_plate_number': None,
  'destinations': [
    {
      'recipient_license_number': '123-XYZ',
      'transfer_type_name': 'Transfer',
      'planned_route': 'I will drive down the road to the place.',
      'estimated_departure_date_time': '2018-03-06T09:15:00.000',
      'estimated_arrival_date_time': '2018-03-06T12:24:00.000',
      'gross_weight': None,
      'gross_unit_of_weight_id': None,
      'transporters': [
        {
          'transporter_facility_license_number': '123-ABC',
          'driver_occupational_license_number': '50',
          'driver_name': 'X',
          'driver_license_number': '5',
          'phone_number_for_questions': '18005555555',
          'vehicle_make': 'X',
          'vehicle_model': 'X',
          'vehicle_license_plate_number': 'X',
          'is_layover': False,
          'estimated_departure_date_time': '2018-03-06T12:00:00.000',
          'estimated_arrival_date_time': '2018-03-06T21:00:00.000',
          'transporter_details': None
        }
      ],
      'packages': [
        {
          'item_name': 'Buds',
          'quantity': 10.0,
          'unit_of_measure_name': 'Ounces',
          'packaged_date': '2018-02-04T00:00:00Z',
          'gross_weight': None,
          'gross_unit_of_weight_name': None,
          'wholesale_price': None
        },
      ]
    }
  ]
})
```

The `Transfer` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a transfer record in Metrc. |
| `update(**kwargs)` | Update the transfer given parameters as keyword arguments. |
| `delete()` | Delete the transfer. |

The `Metrc` class has the following methods for managing transfers.

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

The `TransferTemplate` class represents a cannabis transfer template. The template can be copied to create other templates. Transfer templates can be used for transfers to the same destination licensee utilizing the same: planned route, transporter(s), driver(s), vehicle(s), and packages.

```py
from cannlytics.metrc.models import TransferTemplate

# When you request a transfer template, you receive the following object.
template = TransferTemplate.from_dict({
  'id': 1,
  'manifest_number': None,
  'shipment_license_type': 0,
  'shipper_facility_license_number': '123-ABC',
  'shipper_facility_name': 'Lofty Med-Cultivation B',
  'name': 'Template 1',
  'transporter_facility_license_number': '123-BCD',
  'transporter_facility_name': 'Lofty Med-Dispensary',
  'driver_name': 'X',
  'driver_occupational_license_number': '',
  'driver_vehicle_license_number': '',
  'vehicle_make': 'X',
  'vehicle_model': 'X',
  'vehicle_license_plate_number': 'X',
  'delivery_count': 1,
  'received_delivery_count': 0,
  'package_count': 7,
  'received_package_count': 0,
  'contains_plant_package': False,
  'contains_product_package': False,
  'contains_trade_sample': False,
  'contains_donation': False,
  'contains_testing_sample': False,
  'contains_product_requires_remediation': False,
  'contains_remediated_product_package': False,
  'created_date_time': '2016-10-10T08:20:45-05:00',
  'created_by_user_name': None,
  'last_modified': '0001-01-01T00:00:00+00:00',
  'delivery_id': 0,
  'recipient_facility_license_number': None,
  'recipient_facility_name': None,
  'shipment_type_name': None,
  'shipment_transaction_type': None,
  'estimated_departure_date_time': '0001-01-01T00:00:00.000',
  'actual_departure_date_time': None,
  'estimated_arrival_date_time': '0001-01-01T00:00:00.000',
  'actual_arrival_date_time': None,
  'delivery_package_count': 0,
  'delivery_received_package_count': 0,
  'received_date_time': None,
  'estimated_return_departure_date_time': None,
  'actual_return_departure_date_time': None,
  'estimated_return_arrival_date_time': None,
  'actual_return_arrival_date_time': None
})

# When you create transfer templates, you pass the following object.
template = TransferTemplate.from_dict({
  'name': 'Template 1',
  'transporter_facility_license_number': None,
  'driver_occupational_license_number': None,
  'driver_name': None,
  'driver_license_number': None,
  'phone_number_for_questions': None,
  'vehicle_make': None,
  'vehicle_model': None,
  'vehicle_license_plate_number': None,
  'destinations': [
    {
      'recipient_license_number': '123-XYZ',
      'transfer_type_name': 'Transfer',
      'planned_route': 'I will drive down the road to the place.',
      'estimated_departure_date_time': '2018-03-06T09:15:00.000',
      'estimated_arrival_date_time': '2018-03-06T12:24:00.000'
      'transporters': [
        {
          'transporter_facility_license_number': '123-ABC',
          'driver_occupational_license_number': '50',
          'driver_name': 'X',
          'driver_license_number': '5',
          'phone_number_for_questions': '18005555555',
          'vehicle_make': 'X',
          'vehicle_model': 'X',
          'vehicle_license_plate_number': 'X',
          'is_layover': False,
          'estimated_departure_date_time': '2018-03-06T12:00:00.000',
          'estimated_arrival_date_time': '2018-03-06T21:00:00.000',
          'transporter_details': None
        }
      ],
      'packages': [
        {
          'package_label': 'ABCDEF012345670000010026',
          'wholesale_price': None
        },
      ]
    }
  ]
})
```

The `TransferTemplate` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a transfer template record in Metrc. |
| `update(**kwargs)` | Update the transfer template given parameters as keyword arguments. |
| `delete()` | Delete the transfer template. |

The `Metrc` class has the following methods for managing transfer templates.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_transfer_templates(uid='', action='', license_number='', start='', end='')` | Get transfer template(s). Actions: `deliveries`, `packages`. | `/transfers/v1/templates/` |
| `create_transfer_templates(data, license_number='', return_obs=False)` | Create transfer_template(s). | `/transfers/v1/templates/` |
| `update_transfer_templates(data, license_number='', return_obs=False)` | Update transfer template(s). | `/transfers/v1/templates/` |
| `delete_transfer_template(uid, license_number='')` | Delete transfer template. | `/transfers/v1/templates/` |

## Lab Results

The `LabResult` class that represents a cannabis lab result for a single analyte, e.g. `Microbiologicals`.

```py
from cannlytics.metrc.models import LabResult

# When you request a lab result, you receive the following object.
lab_result = LabResult.from_dict({
  'package_id': 2,
  'lab_test_result_id': 1,
  'lab_facility_license_number': '405R-X0001',
  'lab_facility_name': 'CO PERCEPTIVE TESTING LABS, LLC',
  'source_package_label': 'ABCDEF012345670000010042',
  'product_name': 'Buds',
  'product_category_name': 'Buds',
  'test_performed_date': '2014-11-29',
  'overall_passed': True,
  'revoked_date': None,
  'result_released': True,
  'result_release_date_time': '2014-11-29T00:00:00+00:00',
  'test_type_name': 'Microbiologicals',
  'test_passed': True,
  'test_result_level': 0.1,
  'test_comment': 'This is a comment.',
  'test_informational_only': False,
  'lab_test_detail_revoked_date': None
})
```

The `LabResult` class has the following methods.

| Method | Description |
|--------|-------------|
| `create(data)` | Post lab result data. |
| `post(data)` | Post lab result data. Equivalent alternative of `create`. |
| `upload_coa(data)` | Upload lab result CoA. |
| `release(data)` | Release lab results. |

The `Metrc` class has the following methods for managing lab results.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_lab_results(uid='', license_number='')` | Get lab results. | `/labtests/v1/results` |
| `get_test_types(license_number='')` | Get required quality assurance analyses. | `/labtests/v1/types` |
| `get_test_statuses(license_number='')` | Get pre-defined lab statuses. | `/labtests/v1/states` |
| `post_lab_results(data, license_number='', return_obs=False)` | Post lab result(s). | `/labtests/v1/record` |
| `upload_coas(data, license_number='')` | Upload lab result CoA(s). | `/labtests/v1/labtestdocument` |
| `release_lab_results(data, license_number='')` | Release lab result(s). | `/labtests/v1/results/release` |

## Patients

The `Patient` class represents a cannabis patient.

```py
from cannlytics.metrc.models import Patient

# When you request a patient, you receive the following object.
patient = Patient.from_dict({
  'patient_id': 1,
  'license_number': '000001',
  'registration_date': '2015-01-08',
  'license_effective_start_date': '2014-07-12',
  'license_effective_end_date': '2015-07-07',
  'recommended_plants': 6,
  'recommended_smokable_quantity': 2.0,
  'has_sales_limit_exemption': False,
  'other_facilities_count': 1
})
```

The `Patient` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a patient record in Metrc. |
| `update(**kwargs)` | Update the patient given parameters as keyword arguments. |
| `create()` | Delete the patient. |

The `Metrc` class has the following methods for managing patients.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_patients(uid='', action='active', license_number='')` | Get licensee member patients. Action: `active`. | `/patients/v1/` |
| `create_patients(data, license_number='', return_obs=False)` | Create patient(s). | `/patients/v1/` |
| `update_patients(data, license_number='', return_obs=False)` | Update strain(s). | `/patients/v1/` |
| `delete_patient(uid, license_number='')` | Delete patient. | `/patients/v1/` |

## Sales

The `Receipt` class represents a cannabis sale receipt. Sales are reported to record the transfer of cannabis products to a consumer, patient or caregiver.

```py
from cannlytics.metrc.models import Receipt

# When you request receipts, you receive the following object.
receipt = Receipt.from_dict({
  'sales_date_time': '2016-10-04T16:44:53.000',
  'sales_customer_type': 'Consumer',
  'patient_license_number': None,
  'caregiver_license_number': None,
  'identification_method': None,
  'transactions': [
    {
      'package_label': 'ABCDEF012345670000010331',
      'quantity': 1.0,
      'unit_of_measure': 'Ounces',
      'total_amount': 9.99
    }
  ]
})

# When you create a receipt, you pass the following object.
receipt = Receipt.from_dict({
  'id': 1,
  'receipt_number': None,
  'sales_date_time': '2016-01-01T17:35:45.000',
  'sales_customer_type': 'Consumer',
  'patient_license_number': None,
  'caregiver_license_number': None,
  'identification_method': None,
  'total_packages': 0,
  'total_price': 0.0,
  'transactions': [],
  'is_final': False,
  'archived_date': None,
  'recorded_date_time': '0001-01-01T00:00:00+00:00',
  'recorded_by_user_name': None,
  'last_modified': '0001-01-01T00:00:00+00:00'
})
```

The `Receipt` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a receipt record in Metrc. |
| `update(**kwargs)` | Update the receipt given parameters as keyword arguments. |
| `delete()` | Delete the receipt. |

The `Transaction` class that represents a cannabis sale transaction.

```py
from cannlytics.metrc.models import Transaction

# When you create a transaction, you pass the following object.
transaction = Transaction.from_dict({
  'package_id': 71,
  'package_label': 'ABCDEF012345670000010331',
  'product_name': 'Shake',
  'product_category_name': None,
  'item_strain_name': None,
  'item_unit_cbd_percent': None,
  'item_unit_cbd_content': None,
  'item_unit_cbd_content_unit_of_measure_name': None,
  'item_unit_cbd_content_dose': None,
  'item_unit_cbd_content_dose_unit_of_measure_name': None,
  'item_unit_thc_percent': None,
  'item_unit_thc_content': None,
  'item_unit_thc_content_unit_of_measure_name': None,
  'item_unit_thc_content_dose': None,
  'item_unit_thc_content_dose_unit_of_measure_name': None,
  'item_unit_volume': None,
  'item_unit_volume_unit_of_measure_name': None,
  'item_unit_weight': None,
  'item_unit_weight_unit_of_measure_name': None,
  'item_serving_size': None,
  'item_supply_duration_days': None,
  'item_unit_quantity': None,
  'item_unit_quantity_unit_of_measure_name': None,
  'quantity_sold': 1.0,
  'unit_of_measure_name': 'Ounces',
  'unit_of_measure_abbreviation': 'oz',
  'total_price': 9.99,
  'sales_delivery_state': None,
  'archived_date': None,
  'recorded_date_time': '0001-01-01T00:00:00+00:00',
  'recorded_by_user_name': None,
  'last_modified': '0001-01-01T00:00:00+00:00'
})

# When you get a transaction, you receive an object as follows.
transaction = Transaction.from_dict({
  'sales_date': '2015-01-08',
  'total_transactions': 40,
  'total_packages': 40,
  'total_price': 399.6
})

# When you update a transaction, you pass the following object.
transaction = Transaction.from_dict({
  'package_label': 'ABCDEF012345670000010331',
  'quantity': 1.0,
  'unit_of_measure': 'Ounces',
  'total_amount': 9.99
})
```

The `Transaction` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a transaction record in Metrc. |
| `update(**kwargs)` | Update the transaction given parameters as keyword arguments. |

The `Metrc` class has the following methods for managing sales.

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

## Deliveries

The `Delivery` class represents a cannabis home delivery. Sales are reported to record the transfer of cannabis products to a consumer, patient or caregiver.

```py
from cannlytics.metrc.models import Delivery

# When you create a delivery, you pass the following object.
new_delivery = Delivery.from_dict({
  'sales_date_time': '2016-10-04T16:44:53.000',
  'sales_customer_type': 'Consumer',
  'patient_license_number': None,
  'caregiver_license_number': None,
  'identification_method': None,
  'transactions': [
    {
      'package_label': 'ABCDEF012345670000010331',
      'quantity': 1.0,
      'unit_of_measure': 'Ounces',
      'total_amount': 9.99
    }
  ]
})

# When you request deliveries, you receive the following object.
delivery = Delivery.from_dict({
  'id': 1,
  'receipt_number': None,
  'sales_date_time': '2016-01-01T17:35:45.000',
  'sales_customer_type': 'Consumer',
  'patient_license_number': None,
  'caregiver_license_number': None,
  'identification_method': None,
  'total_packages': 0,
  'total_price': 0.0,
  'transactions': [],
  'is_final': False,
  'archived_date': None,
  'recorded_date_time': '0001-01-01T00:00:00+00:00',
  'recorded_by_user_name': None,
  'last_modified': '0001-01-01T00:00:00+00:00',
})
```

The `Delivery` class has the following methods.

| Method | Description |
|--------|-------------|
| `create()` | Create a receipt record in Metrc. |
| `update(**kwargs)` | Update the receipt given parameters as keyword arguments. |
| `delete()` | Delete the receipt. |

The `Metrc` class has the following methods for managing deliveries.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `create_deliveries(data, license_number='', return_obs=False)` | Create home deliver(ies). | `/sales/v1/deliveries` |
| `get_deliveries(uid='', action='active', license_number='', start='', end='', sales_start='', sales_end='')` | Get sale(s). Actions: `active`, `inactive`. | `/sales/v1/deliveries` |
| `get_return_reasons(license_number='')` | Get the possible return reasons for home delivery items. | `/sales/v1/deliveries/delivery/returnreasons` |
| `complete_deliveries(data, license_number='')` | Complete home delivery(ies). | `/sales/v1/deliveries` |
| `delete_delivery(uid, license_number='')` | Delete a home delivery. | `/sales/v1/deliveries` |
| `update_deliveries(data, license_number='')` | Update home delivery(ies). | `/sales/v1/deliveries` |

## Types

The `Metrc` class has the following methods for retrieving types.

| Method | Description | Endpoint |
|--------|-------------|----------|
| `get_additive_types` | Types of additives that may be used during cultivation: `Fertilizer`, `Pesticide`, `Other`.  |
| `get_adjustment_reasons` | Objects representing reasons for adjusting inventory, e.g. `{'Name': 'Drying', ...}`. |
| `get_analyses` | State mandated quality control analysis objects, e.g. `{'Name': 'THC', ...}`. |
| `get_batch_types` | Types of inventory batches, e.g. `Clone`. |
| `get_categories` | A list of known categories, e.g. `Flower & Buds`. |
| `get_customer_types` | A list of customer types: `Consumer`, `Patient`, `Caregiver`, and `ExternalPatient`. |
| `get_growth_phases` | The growth phase of a given plant: `Young`, `Vegetative`, `Flowering`. |
| `get_item_types` | A list of item objects, e.g. `{'Name': 'Buds', ...}`. |
| `get_location_types` | A list of location type objects, e.g. `{'Name': 'Default', ...}`. |
| `get_package_types` | A list of package types, e.g. `{'Name': 'Product', ...}`. |
| `get_test_statuses` | A list of quality control analysis statuses, e.g. `TestPassed`. |
| `get_transfer_statuses` | A list of transfer statuses, e.g. `Shipped`. |
| `get_transfer_types` | A list of transfer type objects, e.g. `{'Name': 'Lab Sample Transfer', ...}`. |
| `get_waste_methods(license_number='')` | Get all waste methods for a given license, e.g. `{'Name': 'Grinder'}`. | `/plants/v1/waste/methods` |
| `get_waste_reasons(license_number='')` | Get all waste reasons for plants for a given license, e.g. `{'Name': 'Disease/Infestation', ...}`. | `/plants/v1/waste/reasons` |
| `get_waste_types(license_number='')` | Get all waste types for harvests for a given license. | `/harvests/v1/waste/types` |
| `get_units_of_measure(license_number='')` | Get all units of measurement, e.g. `{'Name': 'WeightBased, ...}`. | `/unitsofmeasure/v1/active` |

## Examples

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
sales = track.get_receipts(action='active', start='2022-04-20')

# Update the sales receipt.
sale = track.get_receipts(uid='420')
sale.total_price = 25
sale.update()
```

For a complete demonstration, see the Metrc test.

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
| [New Jersey](https://www.metrc.com/partner/new-jersey/) | <https://api-nj.metrc.com/Documentation> |
| [Ohio](https://www.metrc.com/partner/ohio/) | <https://api-oh.metrc.com/Documentation> |
| [Oklahoma](https://www.metrc.com/partner/oklahoma/) | <https://api-ok.metrc.com/Documentation> |
| [Oregon](https://www.metrc.com/partner/oregon/) | <https://api-or.metrc.com/Documentation> |
| [South Dakota](https://www.metrc.com/partner/south-dakota/) | <https://api-sd.metrc.com/Documentation> |
| [West Virginia](https://www.metrc.com/partner/west-virginia/) | <https://api-wv.metrc.com/Documentation> |
