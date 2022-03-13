"""
Analysis Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Analysis data model.
"""
# Standard imports
from dataclasses import dataclass
from typing import List

from .base import Model

@dataclass
class Analysis(Model):
    """Analyses represent scientific tests, such as cannabinoid
    analysis and pesticide screening. An analysis may contain
    multiple analytes, specific compound or substances that are
    being measured."""
    _collection = 'organizations/%s/analysis'
    analytes: list = List
    analyte_count: int = 0
    key: str = ''
    name: str = ''
    panel: bool = False
    price: float = 0.0
    public: bool = False
