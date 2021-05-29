# -*- coding: utf-8 -*-

"""
cannlytics.traceability.metrc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Metrc client library.
"""


__version__ = '0.0.1'
__author__ = 'Keegan Skeate'


from .client import Client
# from .models import (
#     Area,
#     Batch,
#     Disposal,
#     InventoryType,
#     Inventory,
#     InventoryAdjustment,
#     InventoryTransfer,
#     LabResult,
#     Plant,
#     Sale,
#     Strain,
#     Licensee,
#     User,
# )

# from .exceptions import (
#     TraceabilityException,
# )


def authorize(vendor_api_key, user_api_key, client_class=Client):
    """Authorize use of the Leaf Data Systems API
    using an API key and MME (licensee) code.

    This is a shortcut function which
    instantiates `client_class`.
    By default :class:`cannlytics.traceability.leaf.Client` is used.
    
    Returns: `client_class` instance.
    """

    client = client_class(vendor_api_key, user_api_key)
    return client
