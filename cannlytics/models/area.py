"""
Area Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Area data model.
"""
# Standard imports.
from dataclasses import dataclass
from typing import Optional

# Internal imports.
from .base import Model


@dataclass
class Area(Model):
    """An abstract area that your organization uses in your workflow.
    Areas represent distinct places at your facility(ies).
    Areas are abstract units where you can store inventory,
    plants, samples, instruments, or whatever you please."""
    _collection = 'organizations/%s/areas'
    active: bool = True
    area_type: str = 'General'
    area_type_id: str = ''
    external_id: str = ''
    name: str = ''
    quarantine: bool = False
    for_batches: Optional[bool] = False
    for_plants: Optional[bool] = False
    for_harvests: Optional[bool] = False
    for_packages: Optional[bool] = False
