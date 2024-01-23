"""
Django Project Settings | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 1/5/2021
Updated: 8/24/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Django settings powered by environment variables and
secured by Google Cloud Secret Manager.
"""
# Standard imports.
import json
import io
import os
import re

# External imports.
from cannlytics.firebase import (
    access_secret_version,
    initialize_firebase,
)
from dotenv import dotenv_values
import google.auth
from django.template import base


#----------------------------------------------------------------------#
# Project variables.
#----------------------------------------------------------------------#

# Define project namespaces.
PROJECT_NAME = 'website'
ROOT_URLCONF = f'{PROJECT_NAME}.urls'
WSGI_APPLICATION = f'{PROJECT_NAME}.core.wsgi.application'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get the version number.
with open(os.path.join(BASE_DIR, 'package.json')) as v_file:
    package = json.loads(v_file.read())
    APP_VERSION_NUMBER = package['version']

#----------------------------------------------------------------------#
# Environment variables.
# Pulling django-environ settings file, stored in Secret Manager.
# Docs: https://cloud.google.com/secret-manager/docs/overview
# Example: https://codelabs.developers.google.com/codelabs/cloud-run-django
#----------------------------------------------------------------------#

# Load credentials from a local environment variables file if provided.
env_file = os.path.join(BASE_DIR, '.env')
if os.path.isfile(env_file):
    config = dotenv_values(env_file)
    key = 'GOOGLE_APPLICATION_CREDENTIALS'
    os.environ[key] = config[key]

# Otherwise retrieve the environment variables from Secret Manager,
# loading the project credentials from the cloud environment.
else:
    try:
        _, project_id = google.auth.default()
        os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
        SECRET_SETTINGS_NAME = os.environ['SETTINGS_NAME']
        payload = access_secret_version(project_id, SECRET_SETTINGS_NAME, 'latest')
        config = dotenv_values(stream=io.StringIO(payload))
    except (KeyError, google.auth.exceptions.DefaultCredentialsError):
        raise Exception('No local .env or GOOGLE_CLOUD_PROJECT detected.')

# Initialize Firebase.
try:
    initialize_firebase()
except ValueError:
    pass

# Access the secret key.
SECRET_KEY = config['SECRET_KEY']

# Get production status. When publishing, ensure that PRODUCTION is 'True'.
try:
    PRODUCTION = config['PRODUCTION']
except:
    PRODUCTION = 'True'

# Toggle Django debug mode if not in production.
if PRODUCTION == 'True':
    DEBUG = False
else:
    DEBUG = True
    print('WARNING: Debug mode is enabled.')

#----------------------------------------------------------------------#
# Apps
# https://docs.djangoproject.com/en/3.1/ref/applications/
#----------------------------------------------------------------------#

# Define apps used in the project.
INSTALLED_APPS = [
    PROJECT_NAME,
    'api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_feather',
    'django_robohash',
    'corsheaders',
]

#----------------------------------------------------------------------#
# Middleware
# https://docs.djangoproject.com/en/3.1/topics/http/middleware/
#----------------------------------------------------------------------#

# Define middleware that is executed by Django.
# CorsMiddleware should be placed before any middleware that can generate responses.
# WhiteNoise should be below SecurityMiddleWare and above all others.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    f'{PROJECT_NAME}.core.middleware.BlockUserAgentsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django_permissions_policy.PermissionsPolicyMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    f'{PROJECT_NAME}.core.middleware.AppendOrRemoveSlashMiddleware',
]

# Allow CORS from the following domains.
# See: https://github.com/adamchainz/django-cors-headers/tree/main
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r"^https://\w+\.cannlytics\.com$",
#     r"^https://cannlytics-website-[\w-]+\.a\.run\.app$",
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "origin",
    "token",
)

#----------------------------------------------------------------------#
# Livereload
# https://github.com/tjwalch/django-livereload-server
#----------------------------------------------------------------------#

# Hot-reload for development.
if PRODUCTION == 'False':
    INSTALLED_APPS.insert(0, 'livereload')
    MIDDLEWARE.insert(0, 'livereload.middleware.LiveReloadScript')
    MIDDLEWARE_CLASSES = 'livereload.middleware.LiveReloadScript'

#----------------------------------------------------------------------#
# Templates
# https://docs.djangoproject.com/en/3.1/ref/templates/language/
#----------------------------------------------------------------------#

# Define where templates can be found and should be processed.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, f'{PROJECT_NAME}/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Include certain variables in all templates.
                'website.core.context_processors.selected_settings',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#----------------------------------------------------------------------#
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
#----------------------------------------------------------------------#

# Define default language.
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#----------------------------------------------------------------------#
# Security
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/web_application_security
#----------------------------------------------------------------------#

# Specify allowed domains depending on production or development status.
# FIXME:
ALLOWED_HOSTS = ['*']
if PRODUCTION != 'True':
    ALLOWED_HOSTS.extend(['*'])
try:
    ALLOWED_HOSTS.append(config['CUSTOM_DOMAIN'])
except KeyError:
    pass
try:
    ALLOWED_HOSTS.append(config['FIREBASE_HOSTING_URL'])
except KeyError:
    pass
try:
    ALLOWED_HOSTS.append(config['CLOUD_RUN_URL'])
except KeyError:
    pass

# TODO: Implement Content Security Policy and Permissions Policy.
# FIXME: PAYPAL DOES NOT WORK ANYMORE!!!
# CSP_DEFAULT_SRC = [
#     # "'none'",
#     # "'self'",
#     # 'connect-src',
#     'https://www.google-analytics.com',
#     'https://firebase.googleapis.com',
#     'https://firestore.googleapis.com',
#     'https://fonts.gstatic.com',
#     'https://identitytoolkit.googleapis.com',
#     'http://127.0.0.1:8000',
#     '*',
#     # '//127.0.0.1:35729',
#     # '//127.0.0.1:8080',
# ]
# CSP_FRAME_SRC = [
#     '*',
#     "https://docs.google.com",
#     'https://ghbtns.com',
#     'https://www.paypal.com/',
# ]
# CSP_IMG_SRC = [
#     # "'self'",
#     '*',
#     'https://www.google.com',
#     'https://googleads.g.doubleclick.net',
#     'https://www.facebook.com',
#     'https://t.paypal.com',
#     'https://www.paypalobjects.com/',
#     'https://px.ads.linkedin.com',
#     'https://firebasestorage.googleapis.com',
#     'data:',
# ]
# # CSP_INCLUDE_NONCE_IN = ["script-src"]
# CSP_SCRIPT_SRC = [
#     "'unsafe-eval'",
#     "'unsafe-inline'",
#     # 'script-src-elem',
#     'https://cdn.jsdelivr.net',
#     'https://code.jquery.com',
#     'https://www.googletagmanager.com',
#     # 'https://identitytoolkit.googleapis.com',
#     'https://www.paypal.com',
#     'https://www.paypalobjects.com',
#     'http://127.0.0.1:8000',
#     'http://127.0.0.1:35729',
#     'ws://127.0.0.1:8080/ws',
# ]
# CSP_STYLE_SRC = [
#     "'unsafe-inline'",
#     'https://fonts.googleapis.com',
#     # "style-src-elem"
# ]

# Provides a little extra protection against Cross-Site Scripting.
# SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = False

# Enable Strict-Transport-Security. Gradually work up to 1 year (31536000).
# SECURE_HSTS_SECONDS = 30 
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Define permissions policy.
# PERMISSIONS_POLICY = {
#     'accelerometer': [],
#     'autoplay': [],
#     'camera': [],
#     'display-capture': [],
#     'document-domain': [],
#     'encrypted-media': [],
#     'fullscreen': [],
#     'geolocation': [],
#     'gyroscope': [],
#     'magnetometer': [],
#     'microphone': [],
#     'midi': [],
#     'payment': [],
#     'usb': [],
# }

#----------------------------------------------------------------------#
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
#----------------------------------------------------------------------#

# An unused (under-utilized) SQL database required by Django.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

#----------------------------------------------------------------------#
# Email
# https://docs.djangoproject.com/en/3.1/topics/email/
#----------------------------------------------------------------------#

# Define variables to be able to send emails.
EMAIL_USE_TLS = True
try:
    EMAIL_HOST_USER = config['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
    EMAIL_HOST = config['EMAIL_HOST']
    EMAIL_PORT = config['EMAIL_PORT']
    DEFAULT_FROM_EMAIL = config['DEFAULT_FROM_EMAIL']
    LIST_OF_EMAIL_RECIPIENTS = [EMAIL_HOST_USER]
except KeyError:
    EMAIL_HOST_USER = config.get('EMAIL_HOST_USER')
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    DEFAULT_FROM_EMAIL = EMAIL_HOST
    LIST_OF_EMAIL_RECIPIENTS = [EMAIL_HOST_USER]
    print('WARNING: Email not configured. User or password not specified.')

#----------------------------------------------------------------------#
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
#----------------------------------------------------------------------#

# List of directories where Django will also look for static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, f'{PROJECT_NAME}/static'),
)

# The directory from where files are served. (web accessible folder)
STATIC_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', f'public/{PROJECT_NAME}/static')
)

# The relative path to serve files.
STATIC_URL = '/static/'

# Add support for forever-cacheable files and compression.
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# WHITENOISE_MANIFEST_STRICT = False

#----------------------------------------------------------------------#
# Sessions
# https://docs.djangoproject.com/en/3.1/topics/http/sessions/
#----------------------------------------------------------------------#

# Enable Django's session engine for storing user sessions.
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Whether to expire the session when the user closes their browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# The age of session cookies, in seconds. (Currently: 30 days)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30

#----------------------------------------------------------------------#
# Customization
#----------------------------------------------------------------------#

# Remove trailing slash from URLs.
APPEND_SLASH = False

# Allow Django template tags to span multiple lines.
# https://stackoverflow.com/questions/49110044/django-template-tag-on-multiple-line
base.tag_re = re.compile(base.tag_re.pattern, re.DOTALL)

# Make certain Firebase variables easy to reference.
FIREBASE_API_KEY = config['FIREBASE_API_KEY']
FIREBASE_PROJECT_ID = config['FIREBASE_PROJECT_ID']
STORAGE_BUCKET = config['FIREBASE_STORAGE_BUCKET']
