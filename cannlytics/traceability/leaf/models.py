# -*- coding: utf-8 -*-
"""
cannlytics.traceability.leaf.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains common Leaf Data Systems models.
"""

from cannlytics.firebase import get_document, update_document

from .utils import get_time_string


class LeafModel(object):
    """Base class for all Leaf models."""

    def __init__(self, client, context):
        """Initialize the model, setting keys as properties."""
        self.client = client
        for key in context:
            self.__dict__[key] = context[key]
    
    def __getattr__(self, key):
        """Get properties through dot notation."""
        return self.__dict__[key]
    
    def __setattr__(self, key, value):
        """Set properties through dot notation."""
        self.__dict__[key] = value
    
    @classmethod
    def from_fb(cls, client, ref):
        """Initialize a class from Firebase data.
        Args:
            client (Client): A client instance.
            ref (str): The reference to the document in Firestore.
        """
        data = get_document(ref)
        return cls(client, data)
    
    def to_fb(self, ref='', col=''):
        """Upload the model's properties as a dictionary to Firestore.
        Args:
            ref (str): The Firestore document reference.
            col (str): A Firestore collection, with the UID as document ID.
        """
        data = vars(self).copy()
        [data.pop(x, None) for x in ['client']]
        if col:
            update_document(f'{col}/{self.global_id}', data)
        else:
            update_document(ref, data)
    
    def to_dict(self):
        """Returns the model's properties as a dictionary."""
        data = vars(self).copy()
        [data.pop(x, None) for x in ['client']]
        return data


class Area(LeafModel):
    """A class that represents physical locations at licensed facilities
    where plants and inventory will be located.
    """

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(obj.name, json.get('type'), json.get('external_id'))
        return obj

    def create(self, name, type='non-quarantine', external_id=''):
        """Create an area record."""
        data = {'name': name, 'type': type, 'external_id': external_id}
        area = self.client.create_areas([data])[0]
        self.global_id = area['global_id']

    def update(self, **kwargs):
        """Update the area given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_area(data)

    def delete(self):
        """Delete the area."""
        self.client.delete_area(self.global_id)


class Batch(LeafModel):
    """A class that represents a batch of propagation material, plants,
    harvests, or intermediate / end products.
    """

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(**json)
        return obj

    def create(
        self,
        global_area_id='',
        global_strain_id='',
        num_plants=0,
        origin='seed',
        type='propagation material',
    ):
        """Create a batch record."""
        data = {
            'global_area_id': global_area_id,
            'global_strain_id': global_strain_id,
            'num_plants': num_plants,
            'origin': origin,
            'type': type,
        }
        entry = self.client.create_batches([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])

    def update(self, **kwargs):
        """Update the batch given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_batch(data)

    def delete(self):
        """Delete the batch."""
        self.client.delete_batch(self.global_id)


class Disposal(LeafModel):
    """A class that represents a cannabis disposal."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(**json)
        return obj

    def create(
        self,
        qty='',
        external_id='',
        global_area_id='',
        global_batch_id='',
        global_plant_id='',
        global_inventory_id='',
        reason='mandated',
        source='batch',
        uom='gm'
    ):
        """Create a disposal record."""
        data = {
            'external_id': external_id,
            'reason': reason,
            # 'disposal_at': get_time_string(),
            'qty': qty,
            'uom': uom,
            'source': source,
            'global_batch_id': global_batch_id,
            'global_area_id': global_area_id,
            'global_plant_id': global_plant_id,
            'global_inventory_id': global_inventory_id
        }
        entry = self.client.create_disposals([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])

    def update(self, **kwargs):
        """Update the disposal given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_disposal(data)

    def delete(self):
        """Delete the disposal."""
        self.client.delete_disposal(self.global_id)

    def dispose(self):
        """Dispose of the disposal."""
        data = {'global_id': self.global_id, 'disposed_at': get_time_string()}
        self.client.dispose_disposal(data)


class Inventory(LeafModel):
    """A class that represents an inventory item."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(json)
        return obj

    def create(self, data): # Optional: Pass parameters
        """Create an inventory record."""
        entry = self.client.create_inventory([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])
    
    def update(self, **kwargs):
        """Update the inventory given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_inventory_type(data)

    def delete(self):
        """Delete the inventory."""
        self.client.delete_inventory_type(self.global_id)
    
    def split(self, qty, area_id, external_id=''):
        """Split the inventory."""
        entry = self.client.split_inventory(
            inventory_id=self.global_id,
            area_id=area_id,
            qty=qty,
            external_id=external_id
        )
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])
    
    def convert(
        self,
        area_id,
        inventory_type_id,
        qty,
        items=[],
        external_id='',
        medically_compliant=False,
        retest=True,
        strain_id='',
        uom='gm',
        start_date='',
        end_date='',
        waste=0,
    ):
        """Convert the inventory into new inventory."""
        inventories = [{
            'global_from_inventory_id': self.global_id,
            'qty': qty
        }]
        for item in items:
            inventories.append({
                'qty': item['qty'],
                'global_from_inventory_id': item['global_id'],
            })
            qty += item['qty']
        if not start_date:
            start_date = get_time_string()
        if not end_date:
            end_date = get_time_string()
        entry = self.client.convert_inventory(
            area_id,
            inventory_type_id,
            inventories,
            qty,
            external_id=external_id,
            medically_compliant=medically_compliant,
            retest=retest,
            strain_id=strain_id,
            uom=uom,
            start_date=start_date,
            end_date=end_date,
            waste=waste,
        )
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])
    
    def to_plants(self, data):
        """Unpackage the inventory into plants."""
        plants = self.client.inventory_to_plants(
            self.global_id,
            batch_id='',
            qty=1,
        )
        return plants


class InventoryAdjustment(LeafModel):
    """A class that represents an inventory adjustment."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(**json)
        return obj

    def create(self, data): # Optional: Pass parameters
        """Create an inventory adjustment record."""
        entry = self.client.create_inventory_adjustments([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])


class InventoryType(LeafModel):
    """A class that represents an inventory type."""
    
    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(**json)
        return obj

    def create(
        self,
        weight=0,
        external_id='',
        name='',
        type='end_product',
        intermediate_type='usable_marijuana',
        uom='ea'
    ):
        """Create an inventory type record."""
        data = {
            'external_id': external_id,
            'name': name,
            'type': type,
            'intermediate_type': intermediate_type,
            'weight_per_unit_in_grams': weight,
            'uom': uom
        }
        entry = self.client.create_inventory_types([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])
    
    def update(self, **kwargs):
        """Update the inventory type given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_inventory_type(data)

    def delete(self):
        """Delete the inventory type."""
        self.client.delete_inventory_type(self.global_id)


class Transfer(LeafModel):
    """A class that represents an inventory transfer"""
    
    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(json)
        return obj

    def create(self, data): # Optional: Pass parameters
        """Create an inventory transfer record."""
        entry = self.client.create_transfers([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])
    
    def update(self, **kwargs):
        """Update the inventory transfer given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_transfer(data)
    
    def receive(self, area_id):
        """Receive the inventory transfer."""
        entry = self.client.receive_transfer(
            self.global_id,
            area_id=area_id,
        )
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])
    
    def transit(self):
        """Flag the inventory transfer as in-transit."""
        self.client.transit_transfer(self.global_id)
    
    def void(self):
        """Void the inventory transfer."""
        self.client.void_transfer(self.global_id)
        
    

class LabResult(LeafModel):
    """A class that represents a cannabis lab result."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(**json)
        return obj

    def create(self, data):
        """Create a lab result record."""
        data['tested_at'] = get_time_string()
        entry = self.client.create_lab_results([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])

    def update(self, **kwargs):
        """Update the lab result given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_lab_result(data)

    def delete(self):
        """Delete the lab result."""
        self.client.delete_lab_result(self.global_id)


class Licensee(LeafModel):
    """A class representing a cannabis licensee."""
    pass


class Plant(LeafModel):
    """A class that represents a cannabis plant."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(**json)
        return obj

    def create(self, batch_id='', created_at='', origin='seed', stage='growing'):
        """Create a plant record."""
        if not created_at:
            created_at = get_time_string()
        data = {
            'global_batch_id': batch_id,
            'origin': origin,
            'plant_created_at': created_at,
            'stage': stage,
        }
        entry = self.client.create_plants([data])[0]
        entry_data = entry.to_dict()
        for key in entry_data:
            self.__setattr__(key, entry_data[key])

    def update(self, **kwargs):
        """Update the plant given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_plant(data)

    def delete_plant(self):
        """Delete the plant"""
        self.client.delete_plant(self.global_id)

    def harvest(self, data):
        self.client.harvest_plants(
            data['area_id'],
            data['destination_id'],
            [self.global_id],
            batch_id=data.get('batch_id'),
            external_id=data.get('external_id'),
            harvested_at=get_time_string(),
            flower_wet_weight=data.get('flower_wet_weight'),
            other_wet_weight=data.get('other_wet_weight'),
            uom='gm'
        )
    
    def move_to_inventory(self, area_id, type_id='', plant_ids=[]):
        """Package the plant into an inventory lot.
        Args:
            area_id (str): The area to locate the new package.
            type_id (str): The inventory type ID. If blank,
                then create a new inventory type.
            plant_ids (list): Optional list of other plants to include.
        """
        data = {
            'global_plant_ids': [self.global_id],
            'global_inventory_type_id': type_id,
            'global_area_id': area_id
        }
        self.client.move_plants_to_inventory(data)


class Sale(LeafModel):
    """A class that represents a cannabis sale."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(obj.name)
        return obj

    def create(self, name):
        """Create a sales record."""
        data = {'name': name}
        json = self.client.create_sales([data])[0]
        self.__dict__ = {**self.__dict__, **json}

    def update(self, **kwargs):
        """Update the sale given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_sale(data)

    def delete(self):
        """Delete the sale."""
        self.client.delete_sale(self.global_id)


class Strain(LeafModel):
    """A class that represents a cannabis strain."""

    @classmethod
    def create_from_json(cls, client, json):
        obj = cls(client, json)
        obj.create(obj.name)
        return obj

    def create(self, name):
        """Create a strain record."""
        data = {'name': name}
        json = self.client.create_strains([data])[0]
        self.__dict__ = {**self.__dict__, **json}

    def update(self, **kwargs):
        """Update the strain given parameters as keyword arguments."""
        context = self.to_dict().copy()
        data = {**context, **kwargs}
        self.client.update_strain(data)

    def delete(self):
        """Delete the strain."""
        self.client.delete_strain(self.global_id)


class User(LeafModel):
    """A class representing a user at a cannabis licensee."""
    pass

