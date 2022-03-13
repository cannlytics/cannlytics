"""
Analyte Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Analyte data model.
"""
# Standard imports.
from dataclasses import dataclass
from typing import Optional

# Internal imports.
from .base import Model

@dataclass
class Analyte(Model):
    """An analyte is a specific measurement, such as the concentration
    of THCA, CBDV, or piperonyl butoxide. An analyte can have many
    supporting fields, such as lowest order of detection (LOD),
    lowest order of quantification (LOQ), regulatory limit and more."""
    _collection = 'organizations/%s/analytes'
    cas: str = ''
    public: bool = False
    formula: str = ''
    name: str = ''
    key: str = ''
    limit: Optional[float] = None
    lod: Optional[float] = None
    loq: Optional[float] = None
    units: Optional[str] = ''
    calculation_id: str = ''
