"""
WSGI Configuration | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/24/2021
Updated: 12/23/2021
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: This script exposes the WSGI callable as a module-level variable
named ``application``. For more information on this file, see:
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""
# Internal imports.
import os

# External imports.
import django
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Specify the name of the settings file.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()

# FIXME: This causes the following error in production.
# /usr/local/lib/python3.9/site-packages/whitenoise/base.py:115: UserWarning: No directory at: /app/public/website/static/
# warnings.warn(u"No directory at: {}".format(root))

# Main Django app with static file serving by WhiteNoise.
try:
    application = WhiteNoise(get_wsgi_application())
except:
    application = get_wsgi_application()
