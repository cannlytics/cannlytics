"""
Data Set Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Data set data model.
"""
# Standard imports.
from dataclasses import dataclass

# Internal imports.
from .base import Model


@dataclass
class DataSet(Model):
    """An abstract representation of a data set."""
    _collection = 'organizations/%s/datasets'