"""
Instrument Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Instrument data model.
"""
# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# Internal imports.
from .base import Model


@dataclass
class Instrument(Model):
    """A scientific instrument that produces measurements. Instrument
    data is collected through data files, processed with routine
    automation or data importing."""
    _collection = 'instruments/%s'
    area_id: str = ''
    area_name: str = ''
    name: str = ''
    calibrated_at: datetime = None
    calibrated_by: str = ''
    data_path: str = ''
    description: str = ''
    notes: str = ''

    def create_maintenance_log(self):
        """Create a maintenance log."""
        return NotImplementedError
