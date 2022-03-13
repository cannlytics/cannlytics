"""
Template Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Template data model.
"""
# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# Internal imports.
from .base import Model


@dataclass
class Template(Model):
    """Templates for generating documents, such as invoices and
    certificates."""
    _collection = 'organizations/%s/transfers'
    status: str = ''
    storage_ref: str = ''
    version: str = ''
