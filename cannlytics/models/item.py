"""
Inventory Item Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Inventory item data model.
"""
# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# Internal imports.
from .base import Model


@dataclass
class Item(Model):
    """Any physical inventory item that an organization may have at
    their facility(ies), such as cannabis flower, supplies, or
    instruments. Inventory can be assigned to a specific area to make
    locating the inventory item easier."""
    _collection = 'organizations/%s/inventory'
    admin_method: str = ''
    approved: str = ''
    approved_at: datetime = None
    area_id: str = ''
    area_name: str = ''
    category_name: str = ''
    category_type: str = ''
    description: str = ''
    dose: float = 0.0
    dose_number: int = 0
    dose_units: str = ''
    item_type: str = ''
    moved_at: datetime = None
    name: str = ''
    quantity: float = 0.0
    quantity_type: str = ''
    serving_size: float = 0.0
    supply_duration_days: int = 0
    status: str = ''
    strain_id: str = ''
    strain_name: str = ''
    units: str = ''
    volume: float = 0.0
    volume_units: str = ''
    weight: float = 0.0
    weight_units: str = ''
