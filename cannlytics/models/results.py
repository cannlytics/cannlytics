"""
Results Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Results data model.
"""
# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# Internal imports.
from .base import Model

@dataclass
class Results(Model):
    """The final result for an analyte of an analysis after the
    appropriate calculation has been applied to the analyte's
    measurement."""
    _collection = 'organizations/%s/results'
    analysis: str = ''
    analysis_status: str = ''
    package_id: str = ''
    package_label: str = ''
    product_name: str = ''
    sample_id: str = ''
    sample_type: str = ''
    tested_at: datetime = None
    voided_at: datetime = None
    released: bool = False
    released_at: datetime = None
    status: str = ''
    result: float = 0.0
    units: str = ''
    notes: str = ''
    non_mandatory: bool = False
