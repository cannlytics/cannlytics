"""
Cannlytics Sales Data Initialization | Cannlytics
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 5/13/2023
"""
try:
    from .label_parser import LabelParser
    __all__ = [
        LabelParser,
    ]
except ImportError:
    pass
