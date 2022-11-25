"""
CCRS Models | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/10/2022
Updated: 9/23/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: CCRS models.
"""

# Internal imports.
from cannlytics.firebase import get_document, update_document
from cannlytics.utils.utils import (
    clean_nested_dictionary,
    snake_case
)


class Model(object):
    """Base class for all Metrc models."""

    def __init__(
            self,
            client,
            context,
            license_number='',
            function=snake_case
    ):
        """Initialize the model, setting keys as properties."""
        self.client = client
        self._license = license_number
        properties = clean_nested_dictionary(context, function)
        for key in properties:
            self.__dict__[key] = properties[key]

    def __getattr__(self, key):
        return self.__dict__[key]

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    @property
    def uid(self):
        """The model's unique ID."""
        return self.__dict__.get('id')

    @classmethod
    def from_dict(cls, client, json):
        """Initiate a class instance from a dictionary."""
        obj = cls(client, json)
        try:
            obj.create()
        except KeyError:
            pass
        return obj

    @classmethod
    def from_fb(cls, client, ref):
        """Initialize a class from Firebase data.
        Args:
            client (Client): A Metrc client instance.
            ref (str): The reference to the document in Firestore.
        Returns:
            (Model): A Metrc model.
        """
        data = get_document(ref)
        obj = cls(client, data)
        return obj

    def to_dict(self):
        """Returns the model's properties as a dictionary."""
        data = vars(self).copy()
        [data.pop(x, None) for x in ['_license', 'client', '__class__']]
        return data

    def to_fb(self, ref='', col=''):
        """Upload the model's properties as a dictionary to Firestore.
        Args:
            ref (str): The Firestore document reference.
            col (str): A Firestore collection, with the UID as document ID.
        """
        data = vars(self).copy()
        [data.pop(x, None) for x in ['_license', 'client']]
        if col:
            update_document(f'{col}/{self.uid}', data)
        else:
            update_document(ref, data)


class Area(Model):
    """A model for controlled cannabis production areas.
    ```json
        {
            "area_id": "",
            "created_by": "",
            "created_date": "",
            "external_identifier": "",
            "is_deleted": "",
            "is_quarantine": "",
            "licensee_id": "",
            "name": "",
            "updated_by": "",
            "updated_date": ""
        }
    ```
    """
    pass


# TODO: Contacts


# TODO: Integrators


class Inventory(Model):
    """A model for cannabis inventory.
    ```json
        {
            "area_id": "",
            "created_by": "",
            "created_date": "",
            "external_identifier": "",
            "initial_quantity": "",
            "inventory_id": "",
            "inventory_identifier": "",
            "is_deleted": "",
            "is_medical": "",
            "licensee_id": "",
            "product_id": "",
            "quantity_on_hand": "",
            "strain_id": "",
            "total_cost": "",
            "updated_by": "",
            "updated_date": ""
        }
    ```
    """
    pass


# TODO: Inventory Adjustments


# TODO: Inventory Plant Transfers


# TODO: Lab Results


# TODO: Licensees


# TODO: Plants


# TODO: Plant destructions


# TODO: Products


# TODO: Sale Headers


# TODO: Sale Details


# TODO: Strains


# TODO: Transfers (hard)



# === Tests ===
# if __name__ == '__main__':

# {camel_to_snake(y): "" for y in sorted(x)}
