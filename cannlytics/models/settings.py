"""
Settings Models | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Settings data model.
"""
# Standard imports.
from dataclasses import dataclass

# Internal imports.
from .base import Model


@dataclass
class OrganizationSettings(Model):
    """An organizations's primary settings.
    An organization's `data_models` is the metadata that governs data
    collection. For example:

    "data_models": {
        "analytes": {
            "abbreviation": "AT",
            "current_count": "0",
            "fields": [
                {"key": "analyte_id", "label": "Analyte ID"},
                .
                .
                .
            ],
            "id_schema": "{{ abbreviation }}%y%m%d-{{ count }}",
            "singular": "analyte",
        },
        .
        .
        .
    }
    """
    _collection = 'organizations/%s/settings'
    traceability_provider: str = ''
    public: bool = False
    # data_models: dict = {}


@dataclass
class UserSettings(Model):
    """An organizations's primary settings."""
    _collection = 'users/%s/settings'
    public: bool = False
