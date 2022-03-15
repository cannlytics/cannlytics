"""
Cannabis License Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Cannabis license data model.
"""
# Standard imports.
from dataclasses import dataclass

# Internal imports.
from .base import Model


@dataclass
class CannabisLicense(Model):
    """A state-issued cannabis license."""
    _collection = 'organizations/%s/licenses'
    active_date: str = ''
    expiration_date: str = ''
    license_number: str = ''
    license_type: str = ''
