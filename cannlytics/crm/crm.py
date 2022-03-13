"""
Contact Relationship Management | Cannlytics Module
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <contact@cannlytics.com>
Created: 11/2/2021
Updated: 11/2/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

This module contains Cannlytics contact features and functionality.
"""
# Standard imports.
from typing import Dict


class Contact:
    """An instance of this class is the entry point into Cannlytics."""

    def __init__(self, config: Dict) -> None:
        """Initialize Cannlytics contact class.

        Usage: Make a new Cannlytics contact instance

        `contact = Contact({...})`

        This class provides the main top-level functions for contacts.
        """

        if isinstance(config, dict):
            config_dict = {}
            config = {**config_dict, **config}
        self.config = config
