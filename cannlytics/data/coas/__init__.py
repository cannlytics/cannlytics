"""
Cannlytics CoA Data Initialization | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/21/2022
Updated: 1/23/2024
"""
try:
    from .coas import CoADoc, get_result_value
    __all__ = [
        CoADoc,
        get_result_value,
    ]
except ImportError:
    pass
