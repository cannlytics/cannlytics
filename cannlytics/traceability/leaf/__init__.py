# -*- coding: utf-8 -*-
"""
cannlytics.traceability.leaf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Leaf Data Systems client library.
"""


__version__ = '0.0.1'
__author__ = 'Keegan Leon Skeate'


from .client import Client


def authorize(api_key, mme_code, client_class=Client):
    """Authorize the use of the Leaf Data Systems API
    using an API key and a MME (licensee) code.

    This is a shortcut function which instantiates `client_class`.

    By default :class:`cannlytics.traceability.leaf.Client` is used.

    Returns: `client_class` instance.
    """

    client = client_class(api_key, mme_code)
    return client
