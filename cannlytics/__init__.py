"""
Cannlytics Module Initialization | Cannlytics
Copyright (c) 2021-2024 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 8/10/2024
"""
# from .cannlytics import Cannlytics
import cannlytics.auth as auth
import cannlytics.data as data
import cannlytics.firebase as firebase
import cannlytics.metrc as metrc
import cannlytics.utils as utils
import cannlytics.compounds as compounds


__all__ = [
    # Cannlytics,
    auth,
    data,
    firebase,
    metrc,
    utils,
    compounds,
]
__title__ = 'cannlytics'
__version__ = '0.0.18'
__author__ = 'Keegan Skeate <https://github.com/keeganskeate>'
__license__ = 'MIT <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>'
__copyright__ = 'Copyright (c) 2021-2024 Cannlytics'
