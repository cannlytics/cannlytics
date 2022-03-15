"""
Organization Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Organization data model.
"""
# Standard imports.
from dataclasses import dataclass, field
from typing import List

# Internal imports.
from .base import Model


@dataclass
class Organization(Model):
    """The place where work happens."""
    _collection = 'organizations/%s'
    name: str = ''
    dba: str = ''
    credentialed_date: str = ''
    license_number: str = ''
    license_numbers: List = field(default_factory=list)
    license_type: str = ''
    team: List = field(default_factory=list)
