"""
Contact Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Contact data model.
"""
# Standard imports.
from dataclasses import dataclass, field
from typing import List

# Internal imports.
from .base import Model


@dataclass
class Contact(Model):
    """Contacts in the case of non-laboratory users, are
    other organizations that you work with. Your contacts exist as
    organizations in the decentralized community, a network of
    federated servers that communicate with each other."""
    _collection = 'organizations/%s/contacts'
    additional_fields: List = field(default_factory=list)
    name: str = ''
    email: str = ''
    phone_number: str = ''
    phone_number_formatted: str = ''
    address_formatted: str = ''
    street: str = ''
    city: str = ''
    county: str = ''
    state: str = ''
    zip_code: str = ''
    latitude: float = 0.0
    longitude: float = 0.0
    people: List = field(default_factory=list)
