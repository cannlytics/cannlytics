"""
Data Models | Cannlytics Engine
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/8/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Base data model schema for Cannlytics data models.
"""

# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# External imports.
# pylint: disable=no-member
import ulid


@dataclass
class Model:
    """Base data model schema for Cannlytics data models."""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    uid: str = ulid.new().str.lower()
    ref: str = ''

    @classmethod
    def from_dict(cls, data):
        """Initiate a document from a dictionary."""

        # Split the kwargs into native ones and new ones.
        native_args, new_args = {}, {}
        for key, value in data.items():
            if key in cls.__annotations__:
                native_args[key] = value
            else:
                new_args[key] = value

        # Use the native arguments to create the class.
        ret = cls(**native_args)

        # Add the arguments to the model.
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)

        return ret

    def to_dict(self) -> dict:
        """Returns the model's properties as a dictionary."""
        return vars(self).copy()
