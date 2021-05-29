# -*- coding: utf-8 -*-
"""
cannlytics.traceability.metrc.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains common Metrc models.
"""

# External imports
from datetime import datetime

# Internal imports
from cannlytics.firebase import get_document, update_document

# Local imports
from .utils import (
    clean_dictionary,
    clean_nested_dictionary,
    camel_to_snake,
    snake_to_camel,
    update_context,
    remove_dict_fields,
    remove_dict_nulls,
    get_timestamp,
)


class Model(object):
    """Base class for all Metrc models."""

    def __init__(
        self,
        client,
        context,
        license_number='',
        function=camel_to_snake
    ):
        """Initialize the model, setting keys as properties."""
        self.client = client
        self._license = license_number
        properties = clean_nested_dictionary(context, function)
        for key in properties:
            self.__dict__[key] = properties[key]

    def __getattr__(self, key):
        return self.__dict__[key]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    @classmethod
    def from_fb(cls, client, ref):
        """Initialize a class from Firebase data.
        Args:
            client (Client): A Metrc client instance.
            ref (str): The reference to the document in Firestore.
        """
        data = get_document(ref)
        obj = cls(client, data)
        return obj

    @property
    def uid(self):
        """The model's unique ID."""
        return self.__dict__.get('id')

    def to_dict(self):
        """Returns the model's properties as a dictionary."""
        data = vars(self).copy()
        [data.pop(x, None) for x in ['_license', 'client']]
        return data

    def to_fb(self, ref='', col=''):
        """Upload the model's properties as a dictionary to Firestore.
        Args:
            ref (str): The Firestore document reference.
            col (str): A Firestore collection, with the UID as document ID.
        """
        data = vars(self).copy()
        [data.pop(x, None) for x in ['_license', 'client']]
        if col:
            update_document(f'{col}/{self.uid}', data)
        else:
            update_document(ref, data)

    # TODO: Add create_from_json to all models.


class Employee(Model):
    """An organization's employee or team member.
    E.g.
        {
            "FullName": "Keegan Skeate",
            "License": None
        }
    """
    pass


class Facility(Model):
    """A Facility represents a building licensed for the growing,
    processing, and/or selling of product. Facilities are created
    and have their permissions determined by a state.

    E.g.

    ```js
    {
        "HireDate": "0001-01-01",
        "IsOwner": false,
        "IsManager": true,
        "Occupations": [],
        "Name": "Cultivation LLC",
        "Alias": "Cultivation on Road St",
        "DisplayName": "Cultivation on Road St",
        "CredentialedDate": "1969-08-15",
        "SupportActivationDate": null,
        "SupportExpirationDate": null,
        "SupportLastPaidDate": null,
        "FacilityType": null,
        "License": {
            "Number": "403-X0001",
            "StartDate": "2013-06-28",
            "EndDate": "2015-12-28",
            "LicenseType": "Medical Cultivation"
        }
    }
    ```
    """

    @property
    def license_number(self):
        """The facilities license number."""
        return self.license['number']

    def get_locations(self, uid='', action=''):
        """Get locations at the facility.
        Args:
            uid (str): The UID of a location, takes precedent over action.
            action (str): A specific filter to apply, with options: `active`, `types`.
        """
        response = self.client.get_locations(uid=uid, action=action, license_number=self.license_number)
        return response

    def create_locations(self, names, types=[]):
        """Create locations at the facility.
        Args:
            names (list): A list of location names.
            types (list): A list of location types:
                `default`, `planting`, or `packing`.
        """
        data = []
        for i in range(len(names)):
            try:
                location_type = types[i]
            except IndexError:
                location_type = 'Default Location Type'
            data.append({
                'Name': names[i],
                'LocationTypeName': location_type
            })
        response = self.client.create_locations(
            data,
            license_number=self.license_number
        )
        return response

    def update_locations(self, ids, names, types=[]):
        """Update locations at the facility.
        Args:
            uids (list): A list of location IDs.
            names (list): A list of location names.
            types (list): A list of location types:
                `default`, `planting`, or `packing`.
        """
        data = []
        for i in range(len(ids)):
            try:
                location_type = types[i]
            except IndexError:
                location_type = 'Default Location Type'
            data.append({
                'Id': ids[i],
                'Name': names[i],
                'LocationTypeName': location_type
            })
        response = self.client.update_locations(
            data,
            license_number=self.license_number
        )
        return response

    def delete_location(self, uid):
        """Delete a location at the facility.
        Args:
            uid (str): The UID of a location to delete.
        """
        response = self.client.delete_location(
            uid,
            license_number=self.license_number
        )
        return response

    # TODO:
    # Get / Create / Update / Delete strains from facility
    # Get / Create / Update / Delete items from facility

    # TODO: Create transfers from the facility


class Location(Model):
    """A class that represents a cannabis-production location.
    E.g.
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
    """

    def __init__(self, client, properties, license_number=''):
        super().__init__(client, properties, license_number)
        self._parameters = {
            'name': 'Name',
            'location_type': 'LocationTypeName',
            'batches': 'ForPlantBatches',
            'plants': 'ForPlants',
            'harvests': 'ForHarvests',
            'packages': 'ForPackages'
        }

    def update(self, **kwargs):
        """Update location."""
        data = self.to_dict()
        update = clean_dictionary(data, snake_to_camel)
        for param in kwargs:
            key = self._parameters.get(param, param)
            update[key] = kwargs[param]
        self.client.update_locations([update])

    def delete(self):
        """Delete location."""
        self.client.delete_location(self.id)


class Strain(Model):
    """A class that represents a cannabis strain.
    E.g.
        {
            "Id": 1,
            "Name": "Old-time Moonshine",
            "TestingStatus": "InHouse",
            "ThcLevel": 0.1865,
            "CbdLevel": 0.1075,
            "IndicaPercentage": 25.0,
            "SativaPercentage": 75.0
        }
    """

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create()
        return obj

    def create(self):
        """Create a strain record in Metrc."""
        context = self.to_dict()
        data = clean_dictionary(context, snake_to_camel)
        self.client.create_strains([data])

    def update(self, **kwargs):
        """Update the strain given parameters as keyword arguments."""
        context = self.to_dict()
        data = update_context(context, **kwargs)
        self.client.update_strains([data], license_number=self._license)

    def delete(self):
        """Delete the strain."""
        self.client.delete_strain(self.id, license_number=self._license)


class Item(Model):
    """Items are used to track a licensee's inventory at a given facility.
    Items belong to a single facility
    Each item has a unique item name, category, and strain.
    Item Names are used for identification, so an item name
    should not simply be a category name. Item names are
    specific to the item in that package or production batch.
    Categories are pre-defined. The item name
    identifies what is in the package and categories
    are used for grouping similar items for reporting purposes.    
    An item will retain its name unless it is re-packaged.
    E.g.
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
            "AdministrationMethod": null,
            "UnitCbdPercent": null,
            "UnitCbdContent": null,
            "UnitCbdContentUnitOfMeasureName": null,
            "UnitCbdContentDose": null,
            "UnitCbdContentDoseUnitOfMeasureName": null,
            "UnitThcPercent": null,
            "UnitThcContent": null,
            "UnitThcContentUnitOfMeasureName": null,
            "UnitThcContentDose": null,
            "UnitThcContentDoseUnitOfMeasureName": null,
            "UnitVolume": null,
            "UnitVolumeUnitOfMeasureName": null,
            "UnitWeight": null,
            "UnitWeightUnitOfMeasureName": null,
            "ServingSize": null,
            "SupplyDurationDays": null,
            "NumberOfDoses": null,
            "UnitQuantity": null,
            "UnitQuantityUnitOfMeasureName": null,
            "PublicIngredients": null,
            "Description": null,
            "IsUsed": false
        }
    """

    RETURNED_VALUES = {
        'ProductCategoryName': 'item_category',
        'StrainName': 'strain',
        'UnitOfMeasureName': 'unit_of_measure',
        'QuantityType': 'quantity_type',
        'DefaultLabTestingState': 'default_lab_testing_state',
        'ApprovalStatus': 'approval_status',
        'ApprovalStatusDateTime': 'approval_status_date_time',
        'StrainId': 'strain_id',
        'AdministrationMethod': 'administration_method',
        'UnitQuantity': 'unit_quantity',
        'UnitQuantityUnitOfMeasureName': 'unit_quantity_unit_of_measure_name',
    }

    def __init__(self, client, properties, license_number=''):
        super().__init__(client, properties, license_number)
        for k, v in self.RETURNED_VALUES.items():
            try:
                self.__dict__[v] = properties[k]
            except KeyError:
                pass

    @classmethod
    def create_from_json(cls, client, license_number, json):
        new_obj = cls(client, json, license_number)
        new_obj.create(license_number)
        return new_obj

    def create(self, license_number):
        """Create an item record in Metrc."""
        context = self.to_dict()
        data = clean_dictionary(context, snake_to_camel)
        self.client.create_items([data], license_number)

    def update(self, **kwargs):
        """Update the item given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = update_context(context, **kwargs)
        data = remove_dict_fields(data, self.RETURNED_VALUES.keys())
        data = remove_dict_nulls(data)
        self.client.update_items([data], self._license)

    def delete(self):
        """Delete the item."""
        self.client.delete_item(self.id, self._license)


class Plant(Model):
    """A class that represents a cannabis plant.
    
    Plants are tagged at the immature lot growth phase and at the mature / flowering growth
    phase.
    A UID number is assigned to an immature plant lot of
    up to 100 seeds or immature plants. Required corresponding UID
    number labels will need to be produced by the licensee
    . Once the immature lot has been
    established in Metrc, the death of an immature plant(s) must be recorded in Metrc by
    recording the associated waste amount and reducing the total number of the immature
    plants in the lot for each immature plant that was destroyed.

    Plant tags are assigned to individual plants when they are moved to a designated
    canopy area, or when the plant begins flowering.

    A plant can be destroyed anytime during the growth phases.
    Any waste produced by the plant should be recorded prior to the destruction.
    2. Any waste created during the immature growth phase must be recorded as waste
    using the Plant Waste function and destroyed.
    3. When immature plants begin to flower, select the Change Growth Phase button
    to record the change and associate the new Plant Tag ID to the plant(s).
    4. In Metrc, anytime something is trimmed from a flowering plant during growing
    with the intent to sell it, process it, or perform a partial harvest, a Manicure batch
    must be created.
    """

    # TODO: `create/plantings`,
    # TODO: `create/plantbatch/packages`,

    def flower(self, tag, location_name=None):
        """Change the growth phase of the plant to flowering.
        Args:
            tag (str): A tag to assign to the flowering plant.
            location_name (str): An optional new location for the plant.
        """
        if location_name is None:
            location_name = self.location_name
        data = {
            'Label': self.label,
            'NewTag': tag,
            'GrowthPhase': 'Flowering',
            'NewLocation': location_name,
            'GrowthDate': get_timestamp()
        }
        self.client.manage_plants(
            [data],
            action='changegrowthphases',
            license_number=self._license
        )

    def move(self, location_name):
        """Move the plant to a new location.
        Args:
            location_name (str): The destination's name.
        """
        data = {
            'Id': self.id,
            'Location': location_name,
            'ActualDate': get_timestamp()
        }
        self.client.manage_plants(
            [data],
            action='moveplants',
            license_number=self._license
        )

    def destroy(
        self,
        weight,
        method='Compost',
        material='Soil',
        note='n/a',
        reason='Contamination',
        uom='grams',
        ):
        """Destroy the plant.
        Args:
            weight (float): Required weight of the waste.
            material (str): The waste material, e.g soil.
            method (str): The mechanism of destruction:
                `Grinder` or `Compost`.
            reason (str): The reason for destruction:
                `Contamination` or `Male Plants`.
        """
        data = {
            'Id': self.id,
            'WasteMethodName': method,
            'WasteMaterialMixed': material,
            'WasteWeight': weight,
            'WasteUnitOfMeasureName': uom,
            'WasteReasonName': reason,
            'ReasonNote': note,
            'ActualDate': get_timestamp()
        }
        self.client.manage_plants(
            [data],
            action='destroyplants',
            license_number=self._license
        )

    def manicure(
        self,
        weight,
        harvest_name=None,
        location_name=None,
        patient_license=None,
        uom='Grams',
    ):
        """Manicure the plant.
        Args:
            weight (float): Required harvest weight.
            harvest_name (str): Optional harvest name.
            location_name (str): The drying location's name.
            patient_license (str): A patient's license number.
            uom (str): The unit of measure
        """
        if location_name is None:
            location_name = self.location_name
        data = {
            'Plant': self.label,
            'Weight': weight,
            'UnitOfWeight': uom,
            'DryingLocation': location_name,
            'HarvestName': harvest_name,
            'PatientLicenseNumber': patient_license,
            'ActualDate': get_timestamp()
        }
        self.client.manage_plants(
            [data],
            action='manicureplants',
            license_number=self._license
        )

    def harvest(
        self,
        harvest_name,
        weight,
        location_name=None,
        patient_license=None,
        uom='Grams',
    ):
        """Harvest the plant.
        Args:
            harvest_name (str): Required harvest name.
            weight (float): Required harvest weight.
            location_name (str): The harvest location's name.
            patient_license (str): A patient's license number.
            uom (str): The unit of measure.
        """
        if location_name is None:
            location_name = self.location_name
        data = {
            'Plant': self.label,
            'Weight': weight,
            'UnitOfWeight': uom,
            'DryingLocation': location_name,
            'HarvestName': harvest_name,
            'PatientLicenseNumber': patient_license,
            'ActualDate': get_timestamp()
        }
        self.client.manage_plants(
            [data],
            action='harvestplants',
            license_number=self._license
        )


class Harvest(Model):
    """A class that represents a cannabis harvest.
    
    A harvest batch is created and given a
    unique Harvest Name when plants
    or plant material are harvested.

    A. Harvest Name – Harvests must be strain specific. The Harvest Name must be
    unique. It is a best practice for the harvest name to include the Strain Name
    and Harvest Date, but it is not required by the State.

    B. Weight – The plant is weighed individually in its entirety after being cut from
    root ball (stem, stalk, bud/flower, leaves, trim leaves, etc.).
    
    C. Waste – This can be recorded using multiple entries but must be reported
    within three days of destruction.
    
    D. Package – Package and tag the product from the Harvest Batch (Fresh
    Cannabis Plant, Flower, Leaf or Kief). These packages must be strain
    specific.
    
    E. Transfer – Licensee must create transfer manifest to move product to a
    Processor, Distributor, or Manufacturer.
    
    F. Finish – When the Harvest Batch (HB) has been fully packaged, there should
    be remaining wet weight to account for moisture loss. Selecting Finish
    Harvest will attribute any remaining weight to moisture loss.
    
    6. A Harvest Batch package of Flower, Leaf, Kief or Fresh Cannabis Plant can only
    be created from the Harvested Tab using a single strain from plants harvested at
    the same time.
    """
    
    def create_packages(self, data):
        """Create packages from a harvest.
        Args:
            data (list): The package data.
        """
        self.client.create_harvest_packages(data, license_number=self._license)

    # FIXME: create testing package
    def create_testing_packages(self, data):
        """Create testing packages from a harvest.
        Args:
            data (list): The package data.
        """
        self.client.create_harvest_packages(data, license_number=self._license)

    def remove_waste(self, weight, waste_type='Waste', uom='Grams'):
        """Remove waste from the harvest.
        Args:
            weight (float): Required harvest weight.
            waste_type (str): The type of waste.
            uom (str): The unit of measure.
        """
        data = {
            'Id': self.uid,
            'WasteType': waste_type,
            'UnitOfWeight': uom,
            'WasteWeight': weight,
            'ActualDate': get_timestamp()
        }
        self.client.remove_waste([data], license_number=self._license)
    
    def finish(self):
        """Finish a harvest."""
        data = {'Id': self.uid, 'ActualDate': get_timestamp()}
        self.client.finish_harvests([data], license_number=self._license)
    

    def unfinish(self):
        """Unfinish a harvest."""
        self.client.unfinish_harvests([{'Id': self.uid}], license_number=self._license)

    def move(self, destination, harvest_name=None):
        """Move a harvest.
        Args:
            destination (str): THe name of the destination location.
            harvest_name (str): An optional harvest name.
        """
        data = {
            "Id": self.uid,
            "HarvestName": harvest_name,
            "DryingLocation": destination,
            "ActualDate": get_timestamp()
        }
        self.client.move_harvest([data], license_number=self._license)


class Package(Model):
    """A class that represents a cannabis package.
    
    Immature plants and seeds can be packaged by a nursery and
    transported by a distributor to a cultivator,
    distributor or retailer for sale.

    2. When a manufacturer is creating a concentrate that will then be used in multiple
    infused production batches, the concentrate must be created as a new package.
    The infused production batches will then be created from the concentrate
    package.

    A. The new package of concentrate is a production batch and will then be
    partially used in an infused product or sold to a customer.

    B. This makes it more easily recorded as connected to the finished infused
    product package.

    3. Packages made at a manufacturer facility that creates concentrates must be
    created by pulling from other packages.

    4. A package must exist in order for it to be selected for transfer.
    Transfers are realtime inventory dependent.

    5. There must be a contents section for each new package created from an existing
    package.

    6. When adjusting a package, use the appropriate adjustment reason.

    7. In order for a distributor to send a sample for testing,
    a test sample package must be created. A new test sample must
    have a new RFID package tag and be pulled
    from an existing package.

    8. Package tags may only be used once and may not be reused.
    """

    # @classmethod
    # def create_from_json(cls, client, license_number, json):
    #     new_obj = cls(client, json, license_number)
    #     new_obj.create_package(new_obj.to_dict(), license_number)
    #     return new_obj

    def create_package(self, data):
        """Create a package record in Metrc."""
        data = clean_nested_dictionary(data, snake_to_camel)
        self.client.create_packages([data], self._license)

    def change_item(self, item_name):
        """Change the item of the package."""
        data = {'Label': self.label, 'Item': item_name}
        self.client.change_package_items([data], self._license)

    def finish(self):
        """Finish a package."""
        data = {'Label': self.label, 'ActualDate': get_timestamp()}
        self.client.manage_packages([data], action='finish', license_number=self._license)

    def unfinish(self):
        """Unfinish a package."""
        self.client.manage_packages([{'Label': self.label}], action='unfinish', license_number=self._license)

    def adjust(
        self,
        weight,
        note='',
        reason='Mandatory State Destruction',
        uom='Grams'
    ):
        """Adjust the package.
        Args:
            weight (float): Required adjustment weight.
            note (str): Required note for certain reasons.
            reason (str): The reason for adjustment.
            uom (str): The unit of measure.
        """
        data = {
            'Label': self.label,
            'Quantity': weight,
            'UnitOfMeasure': uom,
            'AdjustmentReason': reason,
            'AdjustmentDate': get_timestamp(),
            'ReasonNote': note
        }
        self.client.manage_packages([data], action='adjust', license_number=self._license)


    # TODO:  remediate, update_note, change_location
    # update_items, update, delete


class Patient(Model):
    """A class that represents a cannabis patient.
    e.g
    {
        'PatientId': 1,
        'LicenseNumber': '000001',
        'RegistrationDate': '2015-01-08',
        'LicenseEffectiveStartDate': '2014-07-12',
        'LicenseEffectiveEndDate': '2015-07-07',
        'RecommendedPlants': 6,
        'RecommendedSmokableQuantity': 2.0,
        'HasSalesLimitExemption': false,
        'OtherFacilitiesCount': 1
    }
    """

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create()
        return obj

    def create(self):
        """Create a patient record in Metrc."""
        context = self.to_dict()
        context['actual_date'] = get_timestamp()
        data = clean_nested_dictionary(context, snake_to_camel)
        self.client.create_patients([data], license_number=self._license)

    def update(self, **kwargs):
        """Update the patient given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = update_context(context, **kwargs)
        data = remove_dict_nulls(data)
        self.client.update_patients([data], self._license)

    def delete(self):
        """Delete the patient."""
        self.client.delete_patient(self.id, self._license)


class PlantBatch(Model):
    """A class that represents a cannabis plant batch.
    E.g.
        {
            "Id": 5,
            "Name": "Demo Plant Batch 1",
            "Type": "Seed",
            "LocationId": null,
            "LocationName": null,
            "LocationTypeName": null,
            "StrainId": 1,
            "StrainName": "Spring Hill Kush",
            "PatientLicenseNumber": null,
            "UntrackedCount": 80,
            "TrackedCount": 10,
            "PackagedCount": 0,
            "HarvestedCount": 0,
            "DestroyedCount": 40,
            "SourcePackageId": null,
            "SourcePackageLabel": null,
            "SourcePlantId": null,
            "SourcePlantLabel": null,
            "SourcePlantBatchId": null,
            "SourcePlantBatchName": null,
            "PlantedDate": "2014-10-10",
            "LastModified": "0001-01-01T00:00:00+00:00"
        }
        {
            "Name": "B. Kush 5-30",
            "Type": "Clone",
            "Count": 25,
            "Strain": "Spring Hill Kush",
            "Location": null,
            "PatientLicenseNumber": "X00001",
            "ActualDate": "2015-12-15"
        }
    """

    RETURNED_VALUES = {
        'TrackedCount': 'count',
        'StrainName': 'strain',
        'LocationName': 'location',
        'QuantityType': 'quantity_type',
        'DefaultLabTestingState': 'default_lab_testing_state',
        'ApprovalStatus': 'approval_status',
        'ApprovalStatusDateTime': 'approval_status_date_time',
        'StrainId': 'strain_id',
        'AdministrationMethod': 'administration_method',
        'UnitQuantity': 'unit_quantity',
        'UnitQuantityUnitOfMeasureName': 'unit_quantity_unit_of_measure_name',
    }

    def __init__(self, client, properties, license_number=''):
        super().__init__(client, properties, license_number)
        for k, v in self.RETURNED_VALUES.items():
            try:
                self.__dict__[v] = properties[k]
            except KeyError:
                pass

    @classmethod
    def create_from_json(cls, client, license_number, json):
        new_obj = cls(client, json, license_number)
        new_obj.create(license_number)
        return new_obj

    def create(self, license_number):
        """Create a plant batch record in Metrc."""
        context = self.to_dict()
        data = clean_dictionary(context, snake_to_camel)
        self.client.manage_batches([data], 'createplantings', license_number)

    def create_package(self, data):
        """Create a package from the plant batch."""
        data = clean_dictionary(data, snake_to_camel)
        self.client.manage_batches([data], 'createpackages', self._license) # , from_mother=True

    def create_package_from_plants(self, data):
        """Create a package from the plant batch."""
        data = clean_dictionary(data, snake_to_camel)
        self.client.manage_batches([data], '/create/packages/frommotherplant', self._license)

    def change_growth_phase(self, data):
        """Change the growth phase of the batch."""
        data = clean_dictionary(data, snake_to_camel)
        self.client.manage_batches([data], 'changegrowthphase', self._license)

    def destroy_plants(self, count, reason):
        """Destroy a number of plants for a given reason.
        Args:
            count (int): The number of plants to destroy.
            reason (str): The reason for the destruction.
        """
        date = datetime.now().strftime('%Y-%m-%d')
        data = {
            'PlantBatch': self.name,
            'Count': count,
            'ReasonNote': reason,
            'ActualDate': date
        }
        self.client.manage_batches([data], 'destroy', self._license)


class LabResult(Model):
    """A class that represents a cannabis lab result.

    The Lab Results tab displays the details of each individual lab test performed on
    the package. A Document Download button is available on each row on the Lab
    Results tab to view the associated certificate of analysis (COA), which the
    laboratory staff uploads when test results are recorded. The test results and
    COA are available on the source package and any related packages only after
    the laboratory staff releases the results
    """

    @classmethod
    def create_from_json(cls, client, license_number, json):
        new_obj = cls(client, json, license_number)
        new_obj.post(license_number)
        return new_obj

    def post(self, data={}):
        """Post lab result data."""
        context = self.to_dict()
        result = clean_dictionary(data, snake_to_camel)
        self.client.post_lab_results([{**context, **result}], self._license)

    def upload_coa(self, data={}):
        """Upload lab result CoA."""
        context = self.to_dict()
        result = clean_dictionary(data, snake_to_camel)
        self.client.upload_coas([{**context, **result}], self._license)

    def release(self, data={}):
        """Release lab results."""
        context = self.to_dict()
        result = clean_dictionary(data, snake_to_camel)
        self.client.release_lab_results([{**context, **result}], self._license)


class Transfer(Model):
    """A class that represents a cannabis transfer.
    Transfers are a key component of the chain of custody process.
    
    A transfer must be created anytime a package moves from one licensee to
    another, even if the two facilities are located on the same property.

    Packages can only be transported from one licensee to another by a licensed
    Distributor. A Testing Laboratory is allowed to transport test samples for official
    state testing. Distributors and Testing Laboratories are required to record the
    actual departure time from the origin facility and the actual arrival time at the
    destination facility in Metrc real-time.

    A package must be received in its entirety (the system DOES NOT allow
    receiving a partial package).

    A transfer can be rejected by individual package, or in whole by rejecting all
    packages.

    A rejected package requires the originating Licensee to receive the package
    back into inventory.

    A package must exist in order to be selected for transfer. Transfers are done in
    real time and are inventory dependent.

    When receiving a package, any adjustments to the weight, volume, or count may
    be reported to the State.

    If there are any questions about a transfer, reject it.

    A transfer can be modified , or voided, up until the time that the
    Distributor or Testing Laboratory marks that it has departed the facility. Once the
    transfer process has begun, the transfer may not be modified except by the Distributor
    or Testing Laboratory to edit estimated departure and arrival times, or driver and vehicle
    information (see Edit Transporter Info below).

    When modifying transfers, each of the transfer fields may be modified at the same level
    of detail as when the transfer was created. Edits may be completed for a variety of
    reasons including: error correction, changes in destination, changes in product, etc.

    Voiding a transfer can only be completed by the originating business. Voiding a transfer
    permanently eliminates it and moves the product back into the originator’s inventory.
    Once a transfer has been voided, it cannot be reinstated and all associated packages
    will be returned to the transfer originator’s inventory

    Receiving a transfer is the final point of exchange in the chain of custody.
    """

    RETURNED_VALUES = {}

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create()
        return obj

    def create(self):
        """Create a transfer record in Metrc."""
        context = self.to_dict()
        data = clean_nested_dictionary(context, snake_to_camel)
        self.client.create_transfers([data], license_number=self._license)

    def update(self, **kwargs):
        """Update the transfer given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = update_context(context, **kwargs)
        data = remove_dict_fields(data, self.RETURNED_VALUES.keys())
        data = remove_dict_nulls(data)
        self.client.update_transfers([data], self._license)

    def delete(self):
        """Delete the transfer."""
        self.client.delete_transfer(self.id, self._license)



class TransferTemplate(Model):
    """A class that represents a cannabis transfer template.
    Transfer templates can be used for transfers to the same
    destination licensee utilizing the same:

        - Planned Route
        - Transporter(s)
        - Driver(s)
        - Vehicle(s)
        - Package

    The template can be copied to create other templates.
    """

    RETURNED_VALUES = {}

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create()
        return obj

    def create(self):
        """Create a transfer template record in Metrc."""
        context = self.to_dict()
        data = clean_nested_dictionary(context, snake_to_camel)
        self.client.create_transfer_templates([data], license_number=self._license)

    def update(self, **kwargs):
        """Update the transfer template given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = update_context(context, **kwargs)
        data = remove_dict_fields(data, self.RETURNED_VALUES.keys())
        data = remove_dict_nulls(data)
        self.client.update_transfer_templates([data], self._license)

    def delete(self):
        """Delete the transfer template."""
        self.client.delete_transfer_template(self.id, self._license)


class Transaction(Model):
    """A class that represents a cannabis sale transaction.
    Get:
    {
        "SalesDate": "2015-01-08",
        "TotalTransactions": 40,
        "TotalPackages": 40,
        "TotalPrice": 399.6
    }
    {
        "PackageId": 71,
        "PackageLabel": "ABCDEF012345670000010331",
        "ProductName": "Shake",
        "ProductCategoryName": null,
        "ItemStrainName": null,
        "ItemUnitCbdPercent": null,
        "ItemUnitCbdContent": null,
        "ItemUnitCbdContentUnitOfMeasureName": null,
        "ItemUnitCbdContentDose": null,
        "ItemUnitCbdContentDoseUnitOfMeasureName": null,
        "ItemUnitThcPercent": null,
        "ItemUnitThcContent": null,
        "ItemUnitThcContentUnitOfMeasureName": null,
        "ItemUnitThcContentDose": null,
        "ItemUnitThcContentDoseUnitOfMeasureName": null,
        "ItemUnitVolume": null,
        "ItemUnitVolumeUnitOfMeasureName": null,
        "ItemUnitWeight": null,
        "ItemUnitWeightUnitOfMeasureName": null,
        "ItemServingSize": null,
        "ItemSupplyDurationDays": null,
        "ItemUnitQuantity": null,
        "ItemUnitQuantityUnitOfMeasureName": null,
        "QuantitySold": 1.0,
        "UnitOfMeasureName": "Ounces",
        "UnitOfMeasureAbbreviation": "oz",
        "TotalPrice": 9.99,
        "SalesDeliveryState": null,
        "ArchivedDate": null,
        "RecordedDateTime": "0001-01-01T00:00:00+00:00",
        "RecordedByUserName": null,
        "LastModified": "0001-01-01T00:00:00+00:00"
    }
    Post:
    {
        "PackageLabel": "ABCDEF012345670000010331",
        "Quantity": 1.0,
        "UnitOfMeasure": "Ounces",
        "TotalAmount": 9.99
    }
    """

    RETURNED_VALUES = {}

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create()
        return obj

    def create(self):
        """Create a transaction record in Metrc."""
        context = self.to_dict()
        data = clean_nested_dictionary(context, snake_to_camel)
        self.client.create_transactions([data], license_number=self._license)

    def update(self, **kwargs):
        """Update the transaction given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = update_context(context, **kwargs)
        data = remove_dict_fields(data, self.RETURNED_VALUES.keys())
        data = remove_dict_nulls(data)
        self.client.update_transactions([data], self._license)



class Receipt(Model):
    """A class that represents a cannabis sale receipt.
    Sales are reported to record the transfer of cannabis
    products to a consumer, patient or caregiver.

    Retrived:

    {
        "Id": 1,
        "ReceiptNumber": null,
        "SalesDateTime": "2016-01-01T17:35:45.000",
        "SalesCustomerType": "Consumer",
        "PatientLicenseNumber": null,
        "CaregiverLicenseNumber": null,
        "IdentificationMethod": null,
        "TotalPackages": 0,
        "TotalPrice": 0.0,
        "Transactions": [],
        "IsFinal": false,
        "ArchivedDate": null,
        "RecordedDateTime": "0001-01-01T00:00:00+00:00",
        "RecordedByUserName": null,
        "LastModified": "0001-01-01T00:00:00+00:00"
    }

    Post:

    {
        "SalesDateTime": "2016-10-04T16:44:53.000",
        "SalesCustomerType": "Consumer",
        "PatientLicenseNumber": null,
        "CaregiverLicenseNumber": null,
        "IdentificationMethod": null,
        "Transactions": [
            {
                "PackageLabel": "ABCDEF012345670000010331",
                "Quantity": 1.0,
                "UnitOfMeasure": "Ounces",
                "TotalAmount": 9.99
            }
        ]
    }

    """

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create()
        return obj

    def create(self):
        """Create a receipt record in Metrc."""
        context = self.to_dict()
        data = clean_nested_dictionary(context, snake_to_camel)
        self.client.create_receipts([data], license_number=self._license)

    def update(self, **kwargs):
        """Update the receipt given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = update_context(context, **kwargs)
        data = remove_dict_nulls(data)
        self.client.update_receipts([data], self._license)

    def delete(self):
        """Delete the receipt."""
        self.client.delete_receipt(self.id, self._license)





#------------------------
# Unused | Needed?
#------------------------

# class Driver(Model):
#     """A class that represents a cannabis transfer driver."""
#     pass


# class Vehicle(Model):
#     """A class that represents a cannabis transfer driver."""
#     pass


# class Waste(Model):
#     """A class that represents a cannabis waste.
    
#     A harvest batch is created and given a
#     unique Harvest Name when plants
#     or plant material are harvested.

#     Plant waste must be recorded within three business days of destruction. In Metrc
#     plant waste can be recorded by Immature Plant Lot, Flowering Plant or by
#     Location.
#     2. Waste can also be recorded by Harvest Batch. See Metrc User Guide for details.
#     3. When recording Flowering Plant waste, the waste from multiple plants can be
#     recorded as a single waste event but the flowering plants contributing to the
#     waste must be individually identified.
#     4. If a plant is no longer viable, the waste must be recorded prior to recording its
#     destruction.
#     5. The reason for the waste must be identified using the Waste Reasons defined by
#     the State of California as listed in Exhibit 38 below. Use of some Waste
#     Reasons may be limited to certain license types, as determined by the State.

#     """

#     pass

