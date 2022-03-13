"""
Workflow Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Workflow data model.
"""
# Standard imports.
from dataclasses import dataclass

# Internal imports.
from .base import Model

@dataclass
class Workflow(Model):
    """An abstract series of actions performed on a set trigger."""
    _collection = 'organizations/%s/workflows'
