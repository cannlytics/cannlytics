"""
Cannlytics CoA Data Initialization | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 5/13/2023
"""
try:
    from .receipt_parser import BudSpender
    __all__ = [
        BudSpender,
    ]
except ImportError:
    pass
