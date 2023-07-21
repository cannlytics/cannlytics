"""
WSGI Configuration | Cannlytics Console
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/24/2021
Updated: 12/20/2021
License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>

Description: This script exposes the WSGI callable as a module-level variable
named ``application``. For more information on this file, see:
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""
# Internal imports.
import os

# External imports.
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Specify the name of the settings file.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'console.settings')

# Main Django app with static file serving by WhiteNoise.
try:
    application = WhiteNoise(get_wsgi_application())
except:
    application = get_wsgi_application()
