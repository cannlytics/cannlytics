"""
Django Settings | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 6/5/2021
Updated: 7/8/2021
License: MIT License
Description:
    Django settings secured by Google Cloud Secret Manager.
"""

# Standard imports
import json
import io
import os
import re

# External imports
import environ
import google.auth
from google.cloud import secretmanager
from django.template import base

# ------------------------------------------------------------#
# Project variables
# ------------------------------------------------------------#

# Define project namespaces.
PROJECT_NAME = 'console'
ROOT_URLCONF = 'console.urls'
WSGI_APPLICATION = 'console.core.wsgi.application'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get the version number.
with open(os.path.join(BASE_DIR, 'package.json')) as v_file:
    package = json.loads(v_file.read())
    APP_VERSION_NUMBER = package['version']

# ------------------------------------------------------------#
# Environment variables.
# Pulling django-environ settings file, stored in Secret Manager.
# Docs: https://cloud.google.com/secret-manager/docs/overview
# Example: https://codelabs.developers.google.com/codelabs/cloud-run-django
# ------------------------------------------------------------#

# Load secrets stored as environment variables.
env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, '.env')

# Attempt to load the Project ID into the environment, safely failing on error.
try:
    _, os.environ['GOOGLE_CLOUD_PROJECT'] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass

# Use a local secret file, if provided.
if os.path.isfile(env_file):
    env.read_env(env_file)

# Retrieve the .env from Secret Manager.
elif os.environ.get('GOOGLE_CLOUD_PROJECT', None):
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    client = secretmanager.SecretManagerServiceClient()
    settings_name = env('SETTINGS_NAME')
    name = f'projects/{project_id}/secrets/{settings_name}/versions/latest'
    payload = client.access_secret_version(name=name).payload.data.decode('UTF-8')
    env.read_env(io.StringIO(payload))
else:
    raise Exception('No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.')

# Access the secret key.
SECRET_KEY = env('SECRET_KEY')

# Ensure PRODUCTION is set to True in your .env when publishing!
try:
    PRODUCTION = env('PRODUCTION')
except:
    PRODUCTION = 'True'
    DEBUG = False
if PRODUCTION == 'True':
    DEBUG = False
else:
    print('\n-------------\nDEVELOPMENT MODE\n-------------\n')
    DEBUG = True

# ------------------------------------------------------------#
# Apps
# https://docs.djangoproject.com/en/3.1/ref/applications/
# ------------------------------------------------------------#

# Define apps used in the project.
INSTALLED_APPS = [
    'api',
    'cannlytics',
    'console',
    # 'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_feather',
    'django_robohash',
]

# ------------------------------------------------------------#
# Middleware
# https://docs.djangoproject.com/en/3.1/topics/http/middleware/
# ------------------------------------------------------------#

# Define middleware that is executed by Django.
MIDDLEWARE = [
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'console.core.middleware.AppendOrRemoveSlashMiddleware',
]

# FIXME: Enable CORS for PDFs
# https://stackoverflow.com/questions/28046422/django-cors-headers-not-work

# ------------------------------------------------------------#
# Livereload
# https://github.com/tjwalch/django-livereload-server
# ------------------------------------------------------------#

# Hot-reload for development.
if PRODUCTION == 'False':
    INSTALLED_APPS.insert(0, 'livereload')
    MIDDLEWARE.insert(0, 'livereload.middleware.LiveReloadScript')
    MIDDLEWARE_CLASSES = 'livereload.middleware.LiveReloadScript'

# ------------------------------------------------------------#
# Templates
# https://docs.djangoproject.com/en/3.1/ref/templates/language/
# ------------------------------------------------------------#

# Define where templates can be found and should be processed.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'console/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'console.core.context_processors.selected_settings',
            ],
        },
    },
]

# ------------------------------------------------------------#
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
# ------------------------------------------------------------#

# Define default language.
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------------------------------------------------------------#
# Security
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/web_application_security
# ------------------------------------------------------------#

# Specify allowed domains depending on production or development status.
ALLOWED_HOSTS = ['*']

# FIXME: Restrict domains in production.
# try:
#     ALLOWED_HOSTS.append(env('CUSTOM_DOMAIN'))
# except:
#     pass
# try:
#     ALLOWED_HOSTS.append(env('FIREBASE_HOSTING_URL'))
# except:
#     pass
# try:
#     ALLOWED_HOSTS.append(env('CLOUD_RUN_URL'))
# except:
#     pass

if PRODUCTION == 'False':
    ALLOWED_HOSTS.extend(['*', 'localhost:8000', '127.0.0.1'])

# ------------------------------------------------------------#
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# ------------------------------------------------------------#

# An unused (under-utilized) SQL database required by Django.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# ------------------------------------------------------------#
# Email
# https://docs.djangoproject.com/en/3.1/topics/email/
# ------------------------------------------------------------#

# Define variables to be able to send emails.
EMAIL_USE_TLS = True
try:
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env('EMAIL_PORT')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
    LIST_OF_EMAIL_RECIPIENTS = [EMAIL_HOST_USER]
except:
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    DEFAULT_FROM_EMAIL = EMAIL_HOST
    LIST_OF_EMAIL_RECIPIENTS = [EMAIL_HOST_USER]
    print('Warning: Email not entirely configured.')

# ------------------------------------------------------------#
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
# ------------------------------------------------------------#

# Setup validators.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------#
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
# ------------------------------------------------------------#

# List of directories where Django will also look for static files
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'console/static'),)

# The directory from where files are served. (web accessible folder)
STATIC_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'public/static')
)

# The relative path to serve files.
STATIC_URL = '/static/'

# ------------------------------------------------------------#
# Sessions
# https://docs.djangoproject.com/en/3.1/topics/http/sessions/
# ------------------------------------------------------------#

# Enable Django's session engine for storing user sessions.
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Whether to expire the session when the user closes their browser.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# The age of session cookies, in seconds. (Currently: 5 days)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 5


# ------------------------------------------------------------#
# Cross-Origin Resource Sharing (CORS)
# Not working!
# https://github.com/adamchainz/django-cors-headers#configuration
# ------------------------------------------------------------#

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = False
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r"^https://firebasestorage$",
#     r"^https://firebasestorage\.googleapis\.com/v0/b/\w+\.appspot.com$",
# ]

# ------------------------------------------------------------#
# Customization
# ------------------------------------------------------------#

# Remove trailing slash from URLs.
APPEND_SLASH = False

# Allow Django template tags to span multiple lines.
# https://stackoverflow.com/questions/49110044/django-template-tag-on-multiple-line
base.tag_re = re.compile(base.tag_re.pattern, re.DOTALL)
