"""
Measurement Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Measurement data model.
"""
# Standard imports.
from dataclasses import dataclass, field
from typing import List

# Internal imports.
from .base import Model


@dataclass
class Measurement(Model):
    """A measurement is an amount measured by an analyst or scientific instrument.
    A calculation is applied to the measurement to get the final result."""
    _collection = 'organizations/%s/measurements'
