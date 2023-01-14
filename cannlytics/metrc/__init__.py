"""
Cannlytics Metrc Client Initialization | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 1/14/2023
"""
from typing import Any, Optional
from .client import Metrc
from .exceptions import MetrcAPIError
from .models import (
    Delivery,
    Category,
    Employee,
    Facility,
    Item,
    Location,
    Harvest,
    Package,
    Patient,
    Plant,
    PlantBatch,
    LabResult,
    Receipt,
    Strain,
    Transfer,
    TransferTemplate,
    Transaction,
    Waste,
)


def initialize_metrc(
        vendor_api_key: str,
        user_api_key: str,
        logs: Optional[bool] = False,
        test: Optional[bool] = False,
        primary_license: Optional[str] = '',
        state: Optional[str] = 'ca',
        client_class: Any = Metrc,
    ) -> Metrc:
    """This is a shortcut function which instantiates a Metrc
    client using a user API key and the vendor API key.
    Args:
        vendor_api_key (str): The vendor's API key.
        user_api_key (str): The user's API key.
        primary_license (str): An optional primary license to use if no license is specified.
        state (str): The state of the traceability system, `ca` by default.
        client_class: By default :class:`cannlytics.metrc.client.Client` is used.
    Returns:
        (Metrc): Returns an instance of the Metrc client.
    """
    return client_class(
        vendor_api_key,
        user_api_key,
        logs=logs,
        test=test,
        primary_license=primary_license,
        state=state,
    )

__all__ = [
    initialize_metrc,
    Metrc,
    MetrcAPIError,
    Delivery,
    Category,
    Employee,
    Facility,
    Item,
    Location,
    Harvest,
    Package,
    Patient,
    Plant,
    PlantBatch,
    LabResult,
    Receipt,
    Strain,
    Transfer,
    TransferTemplate,
    Transaction,
    Waste,
]
