"""
Cannlytics Sales Data Initialization | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 5/13/2023
"""
try:
    from .receipts_ai import ReceiptsParser
    __all__ = [
        ReceiptsParser,
    ]
except ImportError:
    pass
