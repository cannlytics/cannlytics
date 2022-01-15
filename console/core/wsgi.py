"""
WSGI Configuration | Cannlytics Console
Copyright (c) 2021 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/24/2021
Updated: 11/24/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description:

    This script exposes the WSGI callable as a
    module-level variable named ``application``.
    For more information on this file, see
    https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""
# Internal imports.
import os

# External imports.
from django.core.wsgi import get_wsgi_application
try:
    from dj_static import Cling
except ImportError:
    pass

# Specify the name of the settings file.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'console.settings')

# Use dj-static if installed.
try:
    application = Cling(get_wsgi_application())
except:
    application = get_wsgi_application()
