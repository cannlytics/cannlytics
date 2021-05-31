# -*- coding: utf-8 -*-
"""
cannlytics.traceability.leaf.client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the Client class responsible for
communicating with the Leaf Data Systems API.
"""

from json import dumps
from datetime import datetime
from requests import Session

from .exceptions import APIError
from .urls import *
from .utils import format_time_filter, get_time_string
from .models import (
    Area,
    Batch,
    Disposal,
    Inventory,
    InventoryAdjustment,
    InventoryType,
    LabResult,
    Licensee,
    Plant,
    Sale,
    Strain,
    Transfer,
    User,
)


class Client(object):
    """An instance of this class communicates with
    the Leaf Data Systems API.

        api_key (str): A Leaf Data Systems API key.
            Created in the Leaf Data Systems user interface.

        mme_code (str): The Leaf Data Systems ID for the licensee to
            connect. Retrieved from the Leaf Data Systems user interface
            or the `/mmes` endpoint.

        Usage: track = leaf.Client(api_key='xyz', mme_code='abc')
    """

    def __init__(self, api_key, mme_code):
        self.base = LEAF_API_BASE_URL
        self.test_api = LEAF_API_BASE_URL_TEST
        self.session = Session()
        self.session.headers.update({
            'x-mjf-key': api_key,
            'x-mjf-mme-code': mme_code,
            'Content-Type': 'application/json'
        })

    def request(
        self,
        method,
        endpoint,
        params=None,
        data=None,
    ):
        """Make a request to the Leaf API."""
        # FIXME: Restart session if ConnectionError
        response = getattr(self.session, method)(
            endpoint,
            json=data,
            params=params,
        )
        if response.status_code == 200:
            body = response.json()
            try:
                return body['data']
            except (KeyError, TypeError):
                return body
        else:
            raise APIError(response)

    #------------------------------------------------------------------
    # Areas
    #------------------------------------------------------------------

    def get_areas(self):
        """Get all areas."""
        url = LEAF_AREAS_URL
        response = self.request('get', url)
        return [Area(self, x) for x in response]


    def create_areas(self, data):
        """Create area(s).
        Args:
            data (list): A list of area(s) to create.
        """
        url = LEAF_AREAS_URL
        response = self.request('post', url, data={'area': data})
        return [Area(self, x) for x in response]


    def update_area(self, data):
        """Update area.
        Args:
            data (dict): Updated area data.
        """
        url = LEAF_AREAS_UPDATE_URL
        response = self.request('post', url, data={'area': data})
        return Area(self, response)


    def delete_area(self, global_id):
        """Delete an area.
        Args:
            global_id (str): The `area_global_id` of the area to delete.
        """
        url = LEAF_AREAS_DELETE_URL % global_id
        return self.request('delete', url)


    #------------------------------------------------------------------
    # Batches
    #------------------------------------------------------------------

    def get_batches(
        self,
        external_id='',
        global_id='',
        harvested_start='',
        harvested_end='',
        planted_start='',
        planted_end='',
        status='',
        batch_type=''
    ):
        """Get all batches, with optional exclusive filters.
        If filtering by time, then both the start and end are required.
        Args:
            external_id (str): A free-form external ID.
            global_id (str): A batch `global_id`.
            harvested_start (str): An ISO date string, e.g. 2020-04-20.
            harvested_end (str): An ISO date string, e.g. 2021-04-20.
            planted_start (str): An ISO date string, e.g. 2020-04-20.
            planted_end (str): An ISO date string, e.g. 2021-04-20.
            status (str): Batch status, does not work when
                batch_type="intermediate/ end product".
            batch_type (str): Type of 'propagation material', 'plant',
                'harvest', or 'intermediate/ end product'
        """
        url = LEAF_BATCHES_URL
        # TODO: Re-write with params
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif harvested_start and harvested_end:
            url += format_time_filter(
                harvested_start,
                harvested_end,
                field='harvested_at'
            )
        elif planted_start and planted_end:
            url += format_time_filter(
                planted_start,
                planted_end,
                field='harvested_at'
            )
        elif status:
            url += f'?f_status={status}'
        elif batch_type:
            url += f'?f_type={batch_type}'
        response = self.request('get', url)
        return [Batch(self, x) for x in response]


    def create_batches(self, data):
        """Create batch(es).
        Args:
            data (list): A list of batch data.
        """
        url = LEAF_BATCHES_URL
        response = self.request('post', url, data={'batch': data})
        return [Batch(self, x) for x in response]


    def update_batch(self, data):
        """Update a batch.
        Args:
            data (dict): Updated batch data.
        """
        url = LEAF_BATCHES_UPDATE_URL
        response = self.request('post', url, data={'batch': data})
        return Batch(self, response)


    def delete_batch(self, global_id):
        """Delete a batch.
        Args:
            global_id (str): The `global_id` of the batch to delete.
        """
        url = LEAF_BATCHES_DELETE_URL % global_id
        return self.request('delete', url)


    def cure_batch(
        self,
        area_id,
        destination_id,
        batch_id,
        flower_dry_weight=0,
        flower_waste=0,
        other_dry_weight=0,
        other_waste=0,
    ):
        """Enter dry weight data into a harvest batch record.
        This action should be used in lieu of updating a batch
        record to enter dry weights. This function may be used
        multiple times to record updates to dry weights of a batch
        until the final weights have been recorded. Through this
        process, waste can be reported that corresponds to 'flower'
        or 'other material' related to the harvest batch.
        Args:
            area_id (str): Required area ID of the plants.
            destination_id (str): Required destination area ID for the harvest.
            batch_id (str): The global batch ID of the harvest batch.
            flower_dry_weight (int):
            flower_waste (int):
            other_dry_weight (int):
            other_waste (int):
        """
        url = LEAF_BATCHES_CURE_URL
        data = {
            "global_batch_id": batch_id,
            "flower_dry_weight": flower_dry_weight,
            "other_dry_weight": other_dry_weight,
            "flower_waste": flower_waste,
            "other_waste": other_waste,
            "global_flower_area_id": area_id,
            "global_other_area_id": destination_id
        }
        response = self.request('post', url, data=data)
        return Batch(self, response)


    def finish_batch(
        self,
        batch_id,
        lots,
    ):
        """Create inventory lots of 'flower' and 'other_material'
        from a harvest batch.
        Args:
            batch_id (str): The batch to finish.
            lots (list): A list of dictionaries with inventory type, area ID,
                and quantity for that type and area. For example:
                [{
                    "global_inventory_type_id": "WAG010101.TY94",
                    "global_area_id": "WAG010101.AR9A",
                    "qty": "101"
                }]
        """
        url = LEAF_BATCHES_FINISH_URL
        data = {
            "global_batch_id": batch_id,
            "new_lot_types": lots
        }
        response = self.request('post', url, data=data)
        return [Batch(self, x) for x in response]


    #------------------------------------------------------------------
    # Disposals
    #------------------------------------------------------------------

    def get_disposals(
        self,
        disposal_start='',
        disposal_end='',
        external_id='',
        global_batch_id='',
        global_id='',
        global_plant_id='',
    ):
        """Get all disposals, with optional exclusive filters.
        If filtering by time, then both the start and end are required.
        Args:
            disposal_start (str): An ISO date string, e.g. 2020-04-20.
            disposal_end (str): An ISO date string, e.g. 2021-04-20.
            external_id (str): A free-form external ID.
            global_id (str): The `global_id` of a disposal.
            global_batch_id (str): The `global_id` of a disposed batch.
            global_plant_id (str): The `global_id` of a disposed plant.
        """
        url = LEAF_DISPOSAL_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif global_batch_id:
            url += f'?f_batch_id={global_batch_id}'
        elif global_plant_id:
            url += f'?f_plant_id={global_plant_id}'
        elif disposal_start and disposal_end:
            url += format_time_filter(
                disposal_start,
                disposal_end,
                field='date'
            )
        response = self.request('get', url)
        return [Disposal(self, x) for x in response]


    def create_disposals(self, data):
        """Create disposal(s).
        Args:
            data (list): A list of disposal data to create.
        """
        url = LEAF_DISPOSAL_URL
        response = self.request('post', url, data={'disposal': data})
        return [Disposal(self, x) for x in response]


    def update_disposal(self, data):
        """Update a disposal.
        Args:
            data (dict): Updated disposal data.
        """
        url = LEAF_DISPOSAL_UPDATE_URL
        response = self.request('post', url, data={'disposal': data})
        return [Disposal(self, x) for x in response]


    def delete_disposal(self, global_id):
        """Delete a disposal.
        Args:
            global_id (str): The `global_id` of the disposal to delete.
        """
        url = LEAF_DISPOSAL_DELETE_URL % global_id
        return self.request('delete', url)


    def dispose_disposal(self, data):
        """Dispose of a destruction record previously created.
        Args:
            data (dict): A dictionary of global_id and disposed_at.
        """
        url = LEAF_DISPOSAL_DISPOSE_URL
        response = self.request('post', url, data=data)
        return Disposal(self, response)


    #------------------------------------------------------------------
    # Plants
    #------------------------------------------------------------------

    def get_plants(
        self,
        external_id='',
        global_id='',
        global_batch_id='',
        origin='',
    ):
        """Get plants, with optional exclusive filters.
        Args:
            external_id (str): A free-form external ID.
            global_id (str): The `global_id` of a disposal.
            global_batch_id (str): The `global_id` of a disposed batch.
            origin (str): The propagation source type.
        """
        url = LEAF_PLANTS_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif global_batch_id:
            url += f'?f_batch_id={global_batch_id}'
        elif origin:
            url += f'?f_origin={origin}'
        response = self.request('get', url)
        return [Plant(self, x) for x in response]


    def get_plants_by_area(self):
        """Get plant count by area."""
        url = LEAF_PLANTS_AREAS_URL
        response = self.request('get', url)
        return [Area(self, x) for x in response]


    def create_plants(self, data):
        """Create plant(s).
        Args:
            data (list): A list of plant data to create.
        """
        url = LEAF_PLANTS_URL
        response = self.request('post', url, data={'plant': data})
        return [Plant(self, x) for x in response]


    def update_plant(self, data):
        """Update a plant.
        Args:
            data (dict): Updated plant data.
        """
        url = LEAF_PLANTS_UPDATE_URL
        response = self.request('post', url, data={'plant': data})
        return Plant(self, response)


    def delete_plant(self, global_id):
        """Delete a plant.
        Args:
            global_id (str): The `global_id` of the plant to delete.
        """
        url = LEAF_PLANTS_DELETE_URL % global_id
        return self.request('delete', url)


    def harvest_plants(
        self,
        area_id,
        destination_id,
        plant_ids,
        batch_id='',
        external_id='',
        harvested_at='',
        flower_wet_weight=0,
        other_wet_weight=0,
        uom='gm'
    ):
        """Harvest living plants and record the harvest batch wet weight.
        The harvest batch created becomes the child batch of the plant
        batch(es) harvested into it.
        Args:
            area_id (str): Required area ID of the plants.
            destination_id (str): Required destination area ID for the harvest.
            plant_ids (list): A list of `global_id`s of plants to harvest.
            batch_id (str): Leave blank to create a new harvest batch, or
                designate global batch ID of harvest batch to add to.
            external_id (str):
            harvested_at (str):
            flower_wet_weight (int):
            other_wet_weight (int):
            uom (str):
        """
        url = LEAF_PLANTS_HARVEST_URL
        qty_harvest = flower_wet_weight + other_wet_weight
        # Optional: If no area ID, lookup area?
        if not harvested_at:
            harvested_at = get_time_string()
        # date = harvested_at.split('-')
        # yyyy, mm, dd = date[0], date[1], date[2]
        # harvest_date = f"{mm}/{dd}/{yyyy}"
        data = {
            "external_id": external_id,
            "harvested_at": harvested_at,
            "qty_harvest": qty_harvest,
            "flower_wet_weight": flower_wet_weight,
            "other_wet_weight": other_wet_weight,
            "uom": uom,
            # "global_flower_area_id": area_id,
            # "global_other_area_id": area_id,
            'global_area_id': area_id,
            "global_harvest_batch_id": '',
            "global_plant_ids": []
        }
        for plant_id in plant_ids:
            data['global_plant_ids'].append({'global_plant_id': plant_id})
        response = self.request('post', url, data=data)
        return Plant(self, response)


    def move_plants_to_inventory(self, data):
        """Package immature or mature plants of the same strain
        into an inventory lot.
        Args:
            data (dict): Updated plant data.
        """
        url = LEAF_PLANTS_MOVE_URL
        response = self.request('post', url, data=data)
        return Inventory(self, response)


    #------------------------------------------------------------------
    # Strains
    #------------------------------------------------------------------

    def get_strains(self):
        """Get all strains."""
        url = LEAF_STRAINS_URL
        response = self.request('get', url)
        return [Strain(self, x) for x in response]


    def create_strains(self, data):
        """Create strain(s).
        Args:
            data (list): A list of strain(s) to create.
        """
        url = LEAF_STRAINS_URL
        response = self.request('post', url, data={'strain': data})
        return [Strain(self, x) for x in response]


    def update_strain(self, data):
        """Update strain.
        Args:
            data (dict): Updated strain data.
        """
        url = LEAF_STRAINS_UPDATE_URL
        response = self.request('post', url, data={'strain': data})
        return Strain(self, response)


    def delete_strain(self, global_id):
        """Delete a strain.
        Args:
            global_id (str): The `global_id` of the strain to delete.
        """
        url = LEAF_STRAINS_DELETE_URL % global_id
        return self.request('delete', url)


    #------------------------------------------------------------------
    # Inventory types
    #------------------------------------------------------------------

    def get_inventory_types(
        self,
        external_id='',
        global_id='',
        inventory_type='',
    ):
        """Get all disposals, with optional exclusive filters.
        If filtering by time, then both the start and end are required.
        Args:
            external_id (str): A free-form external ID.
            global_id (str): The `global_id` of a disposal.
            type (str): The primary category of the inventory type.
                Values include immature_plant, mature_plant,
                harvest_materials, intermediate_product,
                end_product, waste
        """
        url = LEAF_INVENTORY_TYPES_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif inventory_type:
            url += f'?f_type={inventory_type}'
        response = self.request('get', url)
        return [InventoryType(self, x) for x in response]


    def create_inventory_types(self, data):
        """Create inventory type(s).
        Args:
            data (list): A list of inventory types to create.
        """
        url = LEAF_INVENTORY_TYPES_URL
        response = self.request('post', url, data={'inventory_type': data})
        return [InventoryType(self, x) for x in response]


    def update_inventory_type(self, data):
        """Update an inventory type.
        Args:
            data (dict): Updated inventory type data.
        """
        url = LEAF_INVENTORY_TYPES_UPDATE_URL
        response = self.request('post', url, data={'inventory_type': data})
        return InventoryType(self, response)


    def delete_inventory_type(self, global_id):
        """Delete an inventory type.
        Args:
            global_id (str): The `global_id` of the inventory type to delete.
        """
        url = LEAF_INVENTORY_TYPES_DELETE_URL % global_id
        return self.request('delete', url)


    #------------------------------------------------------------------
    # Inventory
    #------------------------------------------------------------------

    def get_inventory(
        self,
        created_at_start='',
        created_at_end='',
        external_id='',
        global_id='',
        batch_id='',
        inventory_type='',
    ):
        """Get inventory, with optional exclusive filters.
        If filtering by time, then both the start and end are required.
        Args:
            created_at_start (str): An ISO date string, e.g. 2020-04-20.
            created_at_end (str): An ISO date string, e.g. 2021-04-20.
            external_id (str): A free-form external ID.
            global_id (str): The `global_id` of an inventory adjustment.
            batch_id (str): The `global_id` of a batch.
            inventory_type (str): An inventory type.
        """
        url = LEAF_INVENTORY_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif batch_id:
            url += f'?f_batch_id={batch_id}'
        elif inventory_type:
            url += f'?f_type={inventory_type}'
        elif created_at_start and created_at_end:
            url += format_time_filter(
                created_at_start,
                created_at_end,
                field='date'
            )
        response = self.request('get', url)
        return [Inventory(self, x) for x in response]


    def create_inventory(self, data):
        """Create inventory item(s).
        Args:
            data (list): A list of inventory item(s) to create.
        """
        url = LEAF_INVENTORY_URL
        response = self.request('post', url, data={'inventory': data})
        return [Inventory(self, x) for x in response]


    def update_inventory(self, data):
        """Update an inventory item.
        Args:
            data (dict): Updated inventory item data.
        """
        url = LEAF_INVENTORY_UPDATE_URL
        response = self.request('post', url, data={'inventory': data})
        return Inventory(self, response)


    def delete_inventory(self, global_id):
        """Delete an inventory item.
        Args:
            global_id (str): The `global_id` of an inventory item.
        """
        url = LEAF_INVENTORY_DELETE_URL % global_id
        return self.request('delete', url)


    def split_inventory(
        self,
        inventory_id,
        area_id,
        qty,
        external_id='',
    ):
        """Split inventory items into children lots that have the same
        attributes as the parent lot. Inventory should NOT be
        split prior to transferring samples to a lab, since the
        lab sample must be derived from the parent lot at time of
        transfer in order for the lab results to properly associate with it.

        Args:
            inventory_id (str): The `global_id` of the inventory item to split.
            area_id (str): The `global_id` of the area where the child inventory
                will be located.
            qty (str): The quantity of inventory being split into the
                new lot from the parent lot, relative to the
                unit of measure ('uom') of the associated
                inventory type.
            external_id (str): A free-form external ID.
        """
        url = LEAF_INVENTORY_SPLIT_URL
        data = {
            "global_inventory_id": inventory_id,
            "global_area_id": area_id,
            "external_id": external_id,
            "qty": qty,
            'net_weight': '',
            'cost': '',
        }
        response = self.request('post', url, data=data)
        return Inventory(self, response)


    def convert_inventory(
        self,
        area_id,
        inventory_type_id,
        items,
        qty,
        external_id='',
        medically_compliant=False,
        retest=True,
        strain_id='',
        uom='gm',
        start_date='',
        end_date='',
        waste=0,
    ):
        """Inventory conversions are performed for extraction,
        infusion, pre-packaging, and combining functions and
        convert inventory lots of one inventory type into another.

        Args:
            area_id (str): The `global_id` of the area where the conversion
                will be located.
            inventory_type_id (str): The `global_id` of the inventory type
                for the conversion.
            items (list): A list of inventory items to convert. Each
                inventory item should be a dictionary with `qty`
                and `global_id` fields.
            qty (str): The quantity of inventory being split into the
                new lot from the parent lot, relative to the
                unit of measure ('uom') of the associated
                inventory type.
            external_id (str): An optional free-form external ID.
            medically_compliant (bool): If the conversion is medically compliant.
            strain_id (str): The `global_id` of a strain if the conversion
                is strain-specific.
            uom (str): The unit of measure, 'gm' or 'ea'.
            retest (bool): If the conversion needs to be tested again.
            start_date (str): The ISO date conversion began.
            end_date (str): The ISO date conversion ended.
            waste (int): The total weight (gm) of waste produced from the
                conversion process.
        """
        url = LEAF_INVENTORY_CONVERT_URL
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = datetime.now()
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        else:
            end_date = datetime.now()
        started_at = start_date.strftime('%m/%d/%Y')
        finished_at = end_date.strftime('%m/%d/%Y')
        data = {
            "conversion": [
                {
                    "external_id": external_id,
                    "global_inventory_type_id": inventory_type_id,
                    "global_area_id": area_id,
                    "global_strain_id": strain_id,
                    "uom": uom,
                    "qty": qty,
                    "qty_waste_total": waste,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "product_not_altered": '1' if not retest else '0',
                    "medically_compliant": '1' if medically_compliant else '0',
                    "inventories": []
                }
            ]
        }
        for item in items:
            data['inventories'].append({
                'qty': item['qty'],
                'global_from_inventory_id': item['global_id'],
            })
        response = self.request('post', url, data=data)
        return [Inventory(self, x) for x in response]


    def inventory_to_plants(
        self,
        inventory_id,
        batch_id='',
        qty=1,
    ):
        """Unpackage plants from inventory lots. This may occur
        when 'Immature Plant' inventory records are being converted
        into growing plants, or when transferred plants that have been moved
        to inventory already need to be moved back to plant records.
            inventory_id (str): The `global_id` of the inventory item.
            batch_id (str): An optional `global_id` for a batch. If
                empty, then a new batch will be created.
            qty (int): The number of plants to create.
        """
        url = LEAF_INVENTORY_MOVE_URL
        data = {
            'global_inventory_id': inventory_id,
            'global_batch_id': batch_id,
            'qty': qty,
        }
        response = self.request('post', url, data=data)
        return [Plant(self, x) for x in response]


    #------------------------------------------------------------------
    # Inventory adjustments
    #------------------------------------------------------------------

    def get_inventory_adjustments(
        self,
        created_at_start='',
        created_at_end='',
        external_id='',
        global_id='',
        inventory_id='',
        qty='',
    ):
        """Get inventory adjustments, with optional exclusive filters.
        If filtering by time, then both the start and end are required.
        Filtering by quantity will return all quantities greater than
        the minimum quantity designated
        Args:
            created_at_start (str): An ISO date string, e.g. 2020-04-20.
            created_at_end (str): An ISO date string, e.g. 2021-04-20.
            external_id (str): A free-form external ID.
            global_id (str): The `global_id` of an inventory adjustment.
            inventory_id (str): The `global_id` of an inventory item.
            qty (int): A quantity of adjustments made.
        """
        url = LEAF_INVENTORY_ADJUSTMENTS_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif inventory_id:
            url += f'?f_inventory_id={inventory_id}'
        elif qty:
            url += f'?f_adjusted_qty={qty}'
        elif created_at_start and created_at_end:
            url += format_time_filter(
                created_at_start,
                created_at_end,
                field='date'
            )
        response = self.request('get', url)
        return [InventoryAdjustment(self, x) for x in response]


    def create_inventory_adjustments(self, data):
        """Create disposal(s).
        Args:
            data (list): A list of disposal data to create.
        """
        url = LEAF_INVENTORY_ADJUSTMENTS_URL
        response = self.request('post', url, data={'inventory_adjustment': data})
        return [InventoryAdjustment(self, x) for x in response]


    #------------------------------------------------------------------
    # Inventory transfers
    #------------------------------------------------------------------

    def get_transfers(
        self,
        external_id='',
        batch_id='',
        global_id='',
        status='',
        sender='',
        receiver='',
        date='',
    ):
        """Get inventory transfers.
        Args:
            external_id (str): A free-form external ID.
            batch_id (str): The `global_id` of a batch.
            global_id (str): The `global_id` for an inventory transfer.
            status (str): The status of the transfer. May be of type
                'open', 'in-transit', 'received', or 'ready-for-pickup'.
            sender (str): The `mme_code` of the sending licensee.
            receiver (str): The `mme_code` of the receiving licensee.
            date (str): The ISO date of estimated departure.
        """
        url = LEAF_INVENTORY_TRANSFERS_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif status:
            url += f'?f_status={status}'
        elif sender:
            url += f'?f_mme_code={sender}'
        elif receiver:
            url += f'?f_to_mme_code={receiver}'
        elif batch_id:
            url += f'?f_batch={batch_id}'
        elif date:
            date = datetime.fromisoformat(date)
            departed_date = date.strftime('%m/%d/%Y')
            url += f'?f_date1={departed_date}'
        response = self.request('get', url)
        return [Transfer(self, x) for x in response]


    def create_transfers(self, data):
        """Create inventory transfer(s).
        Args:
            data (list): A list of inventory transfer(s) to create.
        """
        url = LEAF_INVENTORY_TRANSFERS_URL
        response = self.request('post', url, data={'inventory_transfer': data})
        return [Transfer(self, x) for x in response]


    def create_transfer(self, data):
        """Create a single inventory transfer.
        Args:
            data (dict): Inventory transfer to create.
        """
        return self.create_transfers([data])


    def update_transfer(self, data):
        """Update inventory transfer.
        Args:
            data (dict): Updated inventory transfer data.
        """
        url = LEAF_INVENTORY_TRANSFERS_UPDATE_URL
        response = self.request('post', url, data={'inventory_transfer': data})
        return Transfer(self, response)


    def transit_transfer(self, global_id):
        """
        Changes the 'status' of an 'open' inventory transfer
        to 'in_transit'.
        Args:
            global_id (str): The `global_id` of an inventory transfer.
        """
        url = LEAF_INVENTORY_TRANSFERS_TRANSIT_URL
        data = {'global_id': global_id}
        response = self.request('post', url, data=data)
        return Transfer(self, response)


    def receive_transfer(
        self,
        global_id,
        area_id='',
        area_ids=[],
        strain_id='',
        strain_ids=[],
    ):
        """
        Receive inventory associated with an inventory transfer that
        has been sent by another licensee.
        Args:
            global_id (str): The `global_id` of an inventory transfer.
            area_id (str): The `global_id` of an area if all items are
                to be received in one designated area.
            area_ids (list): An optional list that takes precedent over area_id
                to designate each received transfer to a specific area.
            strain_id (str): An optional `global_id` of a strain if all items are
                to be received as a specific strain.
            area_ids (list): An optional list that takes precedent over area_id
                to designate each received transfer to a specific area.
        """
        url = LEAF_INVENTORY_TRANSFERS_RECEIVE_URL
        data = {'global_id': global_id, 'inventory_transfer_items': []}
        item_request = self.get_transfers(global_id=global_id)
        items = item_request[0].inventory_transfer_items
        # Optional: Make area_ids and strain_ids flexibility more elegant.
        count = 0
        for item in items:
            print(item)
            if area_ids:
                area_id = area_ids[count]
            if strain_ids:
                strain_id = strain_ids[count]
            data['inventory_transfer_items'].append({
                'global_id': item['global_id'],
                'received_qty': item['qty'],
                'global_received_area_id': area_id,
                'global_received_strain_id': strain_id,
                'global_received_inventory_id': item['global_inventory_id'],
            })
            count += 1
        response = self.request('post', url, data=data)
        return Transfer(self, response)


    def void_transfer(self, global_id):
        """
        Causes an inventory transfer record to be voided.
        Args:
            global_id (str): The `global_id` of an inventory transfer.
        """
        url = LEAF_INVENTORY_TRANSFERS_VOID_URL
        response = self.request('post', url, data={'global_id': global_id})
        return Transfer(self, response)


    #------------------------------------------------------------------
    # Lab results
    #------------------------------------------------------------------

    def get_lab_results(
        self,
        external_id='',
        global_batch_id='',
        global_id='',
        status='',
        testing_status='',
        inventory_type='',
    ):
        """Get lab_results."""
        url = LEAF_LAB_RESULTS_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif status:
            url += f'?f_status={status}'
        elif testing_status:
            url += f'?f_testing_status={testing_status}'
        elif inventory_type:
            url += f'?f_type={inventory_type}'
        elif global_batch_id:
            url += f'?f_batch={global_batch_id}'
        response = self.request('get', url)
        return [LabResult(self, x) for x in response]


    def create_lab_results(self, data):
        """Create lab result(s).
        Args:
            data (list): A list of lab result(s) to create.
        """
        url = LEAF_LAB_RESULTS_URL
        response = self.request('post', url, data={'lab_result': data})
        return [LabResult(self, x) for x in response]


    def update_lab_result(self, data):
        """Update lab result.
        Args:
            data (dict): Updated lab result data.
        """
        url = LEAF_LAB_RESULTS_UPDATE_URL
        response = self.request('post', url, data={'lab_result': data})
        return LabResult(self, response)


    def delete_lab_result(self, global_id):
        """Delete a lab result.
        Args:
            global_id (str): The `global_id` of the lab result to delete.
        """
        url = LEAF_LAB_RESULTS_DELETE_URL % global_id
        return self.request('delete', url)


    #------------------------------------------------------------------
    # Sales
    #------------------------------------------------------------------

    def get_sales(
        self,
        external_id='',
        global_area_id='',
        global_id='',
        sale_type='',
        sold_at_start='',
        sold_at_end='',
        status='',
    ):
        """Get all sales, with optional exclusive filters.
        If filtering by time, then both the start and end are required.
        Args:
            external_id (str): A free-form external ID.
            global_area_id (str): The `global_id` of an area of a sale.
            global_id (str): The `global_id` of a sale.
            sale_type (str): The type of sale.
                Values include ... TODO:
            sold_at_start (str): An ISO date string, e.g. 2020-04-20.
            sold_at_end (str): An ISO date string, e.g. 2021-04-20.
            status (str): The status of sales.
        """
        url = LEAF_SALES_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif global_area_id:
            url += f'?f_area_id={global_area_id}'
        elif sale_type:
            url += f'?f_sale_type={sale_type}'
        elif status:
            url += f'?f_status={status}'
        elif sold_at_start and sold_at_end:
            url += format_time_filter(
                sold_at_start,
                sold_at_end,
                field='date'
            )
        response = self.request('get', url)
        return [Sale(self, x) for x in response]


    def create_sales(self, data):
        """Create sale(s).
        Args:
            data (list): A list of a sale(s) data to create.
        """
        url = LEAF_SALES_URL
        response = self.request('post', url, data={'sale': data})
        return [Sale(self, x) for x in response]


    def update_sale(self, data):
        """Update sales.
        Args:
            data (dict): Updated sale data.
        """
        url = LEAF_SALES_UPDATE_URL
        response = self.request('post', url, data={'sale': data})
        return Sale(self, response)


    def delete_sale(self, global_id):
        """Delete a sale.
        Args:
            global_id (str): The `global_id` of the sale to delete.
        """
        url = LEAF_SALES_DELETE_URL % global_id
        return self.request('delete', url)


    #------------------------------------------------------------------
    # Licensees and users
    #------------------------------------------------------------------

    def get_licensees(
        self,
        mme_code='',
        mme_name='',
        mme_cert='',
        updated_at_start='',
        updated_at_end='',
    ):
        """Get licensees,  with optional exclusive filters.
        Args:
            mme_code (str): A licensee's `mme_code`.
            mme_name (str): A licensee's name.
            mme_cert (str): A licensee's certification number.
            updated_at_start (str): An ISO date to restrict the latest updated.
            updated_at_end (str): An ISO date to restrict the earliest updated.
        """
        url = LEAF_LICENSEES_URL
        if mme_code:
            url += f'?f_mme_code={mme_code}'
        elif mme_name:
            url += f'?f_mme_name={mme_name}'
        elif mme_cert:
            url += f'?f_mme_cert={mme_cert}'
        elif updated_at_start:
            date = updated_at_start.split('-')
            yyyy, mm, dd = date[0], date[1], date[2]
            url += f'?f_updated_at1={mm}/{dd}/{yyyy}'
        elif updated_at_end:
            date = updated_at_end.split('-')
            yyyy, mm, dd = date[0], date[1], date[2]
            url += f'?f_updated_at2={mm}/{dd}/{yyyy}'
        response = self.request('get', url)
        return [Licensee(self, x) for x in response]


    def get_licensee(self, global_id, mme_code=''):
        """Get licensee,  with optional exclusive filters.
        Args:
            global_id (str): The `global_id` of the licensee to get.
            mme_code (str): The `mme_code` of the licensee to get.
        """
        url = LEAF_LICENSEE_URL % global_id
        if mme_code:
            url += f'?f_mme_code={mme_code}'
        response = self.request('get', url)
        return Licensee(self, response)


    def get_users(
        self,
        global_id='',
        mme_name='',
        mme_code='',
        user_name='',
        user_email='',
        external_id='',
        updated_at_start='',
        updated_at_end='',
    ):
        """Get all users.
        Args:
            global_id (str): The `global_id` of a user.
            mme_name (str): The name of users' licensee.
            mme_code (str): The `mme_code` of users' licensee.
            user_name (str): The name of a user.
            user_email (str): The email of a user.
            external_id (str): A free-form external ID.
            updated_at_start (str): An ISO date to restrict to the latest updated users.
            updated_at_end (str): An ISO date to restrict to the earliest updated users.
        """
        url = LEAF_USERS_URL
        if global_id:
            url += f'?f_global_id={global_id}'
        elif mme_name:
            url += f'?f_mme_name={mme_name}'
        elif mme_code:
            url += f'?f_mme_code={mme_code}'
        elif user_name:
            url += f'?f_user_name={user_name}'
        elif user_email:
            url += f'?f_user_email={user_email}'
        elif external_id:
            url += f'?f_external_id={external_id}'
        elif updated_at_start:
            date = updated_at_start.split('-')
            yyyy, mm, dd = date[0], date[1], date[2]
            url += f'?f_updated_at1={mm}/{dd}/{yyyy}'
        elif updated_at_end:
            date = updated_at_end.split('-')
            yyyy, mm, dd = date[0], date[1], date[2]
            url += f'?f_updated_at2={mm}/{dd}/{yyyy}'
        response = self.request('get', url)
        return [User(self, x) for x in response]

