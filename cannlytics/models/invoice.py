"""
Invoice Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Invoice data model.
"""
# Standard imports.
from dataclasses import dataclass, field
from typing import List

# Internal imports.
from .base import Model


@dataclass
class Invoice(Model):
    """Invoices are incoming or outgoing bills that you want to manage
    in the Cannlytics platform."""
    _collection = 'organizations/%s/invoices'
    analyses: List = field(default_factory=list)
