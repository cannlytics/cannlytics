"""
WSGI (Web Server Gateway Interface) Configuration

Exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    from dj_static import Cling
except ImportError:
    pass

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'cannlytics_console.settings'
)

application = Cling(get_wsgi_application())
