"""
Cannlytics Module Initialization | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 4/8/2023
"""
from .cannlytics import Cannlytics
import cannlytics.auth as auth
import cannlytics.data as data
import cannlytics.firebase as firebase
import cannlytics.lims as lims
import cannlytics.metrc as metrc
import cannlytics.models as models
import cannlytics.stats as stats
import cannlytics.utils as utils


__all__ = [
    'Cannlytics',
    'auth',
    'data',
    'firebase',
    'lims',
    'metrc',
    'models',
    'paypal',
    'stats',
    'utils',
]
__title__ = 'cannlytics'
__version__ = '0.0.15'
__author__ = 'Keegan Skeate <https://github.com/keeganskeate>'
__license__ = 'MIT <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>'
__copyright__ = 'Copyright (c) 2022-2023 Cannlytics'
