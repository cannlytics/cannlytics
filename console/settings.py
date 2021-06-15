"""
Django Settings with Environment Variables | Cannlytics Console

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 6/5/2021
Updated: 6/8/2021
Description:
    Django settings secured by Google Cloud Secret Manager.

References:
    https://docs.djangoproject.com/en/3.1/topics/settings/
    https://docs.djangoproject.com/en/3.1/ref/settings/
    https://cloud.google.com/secret-manager/docs/overview
    https://codelabs.developers.google.com/codelabs/cloud-run-django
"""

# Standard imports
import json
import io
import os
import re

# External imports
import environ
import google.auth
from google.cloud import secretmanager as sm
from django.template import base

# Optional: Caching for production.
# https://docs.djangoproject.com/en/3.2/ref/templates/api/#django.template.loaders.cached.Loader

# Optional: Hashing for production.
# https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#manifeststaticfilesstorage

# ------------------------------------------------------------#
# Project variables
# ------------------------------------------------------------#
PROJECT_NAME = 'console'
ROOT_URLCONF = 'console.urls'
SETTINGS_NAME = 'cannlytics_settings'
WSGI_APPLICATION = 'console.wsgi.application'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get the version number.
with open(os.path.join(BASE_DIR, 'package.json')) as v_file:
    package = json.loads(v_file.read())
    APP_VERSION_NUMBER = package['version']

# ------------------------------------------------------------#
# Environment variables.
# Pulling django-environ settings file, stored in Secret Manager.
# ------------------------------------------------------------#

# Set Google Cloud credentials. (Is this needed?)
# env = environ.Env()
# env.read_env(os.path.join(BASE_DIR, '.env'))
# credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

# Load secrets stored as environment variables.
try:
    env_file = os.path.join(BASE_DIR, '.env')
    if not os.path.isfile('.env'):
        import google.auth
        from google.cloud import secretmanager as sm

        _, project = google.auth.default()
        if project:
            client = sm.SecretManagerServiceClient()
            # path = client.secret_version_path(project, SETTINGS_NAME, 'latest')
            name = f"projects/{project}/secrets/{SETTINGS_NAME}/versions/latest"
            payload = client.access_secret_version(name=name).payload.data.decode('UTF-8')
            with open(env_file, 'w') as f:
                f.write(payload)

    env = environ.Env()
    env.read_env(io.StringIO(payload))
    SECRET_KEY = env('SECRET_KEY')
    # DEBUG = env('DEBUG') # TODO: Set PRODUCTION in Secret Manager secret.

except:
    # Create a default secret key for development.
    # https://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys
    env = environ.Env()
    try:
        from console.secret_key import SECRET_KEY
    except ImportError:
        from console.utils import generate_secret_key
        SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
        SECRET_KEY = generate_secret_key(os.path.join(SETTINGS_DIR, 'secret_key.py'))

# ------------------------------------------------------------#
# Ensure PRODUCTION is set to True in your .env when publishing!
# ------------------------------------------------------------#
try:
    PRODUCTION = env('PRODUCTION')
except:
    PRODUCTION = 'False'
if PRODUCTION == 'True':
    DEBUG = False
else:
    print('DEVELOPMENT MODE')
    DEBUG = True

# ------------------------------------------------------------#
# Apps
# https://docs.djangoproject.com/en/3.1/ref/applications/
# ------------------------------------------------------------#
INSTALLED_APPS = [
    'api',
    'cannlytics',
    'console',
    'crispy_forms',
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

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# ------------------------------------------------------------#
# Middleware
# https://docs.djangoproject.com/en/3.1/topics/http/middleware/
# ------------------------------------------------------------#
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'console.core.middleware.AppendOrRemoveSlashMiddleware',
]

# ------------------------------------------------------------#
# Livereload
# https://github.com/tjwalch/django-livereload-server
# ------------------------------------------------------------#
if PRODUCTION == 'False':
    INSTALLED_APPS.insert(0, 'livereload')
    MIDDLEWARE.insert(0, 'livereload.middleware.LiveReloadScript')
    MIDDLEWARE_CLASSES = 'livereload.middleware.LiveReloadScript'

# ------------------------------------------------------------#
# Templates
# https://docs.djangoproject.com/en/3.1/ref/templates/language/
# ------------------------------------------------------------#
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
                'console.core.context_processors.selected_settings', # Adds select settings to the context.
            ],
        },
    },
]

# ------------------------------------------------------------#
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
# ------------------------------------------------------------#
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------#
# Authentication
# Optional: Setup custom authentication backend with Firebase.
# https://www.oscaralsing.com/firebase-authentication-in-django/
# ------------------------------------------------------------#
# AUTHENTICATION_BACKENDS = []
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'REST_framework.authentication.SessionAuthentication',
#         'cannlytics_auth.authentication.FirebaseAuthentication',
#     ),
# }

# ------------------------------------------------------------#
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
# ------------------------------------------------------------#
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------------------------------------------------------------#
# Security
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/web_application_security
# ------------------------------------------------------------#
ALLOWED_HOSTS = []
try:
    ALLOWED_HOSTS.append(env('CUSTOM_DOMAIN'),)
except:
    pass
try:
    ALLOWED_HOSTS.append(env('FIREBASE_HOSTING_URL'),)
except:
    pass
try:
    ALLOWED_HOSTS.append(env('CLOUD_RUN_URL'),)
except:
    pass

if PRODUCTION == 'False':
    ALLOWED_HOSTS.extend(['*', 'localhost:8000', '127.0.0.1'])

SECURE_SSL_REDIRECT = False

# ------------------------------------------------------------#
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# ------------------------------------------------------------#
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

EMAIL_USE_TLS = True
try:
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env('EMAIL_PORT')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
    LIST_OF_EMAIL_RECIPIENTS = [EMAIL_HOST_USER]
except:
    print('Warning: Email not entirely configured.')

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
# Google Cloud Storage alternative for serving static files
# Uncomment lines 237-267 to setup Firebase Storage.
# ------------------------------------------------------------#

# # Setup Google Cloud Storage for Django.
# # https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
# INSTALLED_APPS += ['storages'] # for django-storages

# # Define static storage via django-storages[google]
# try:
#     GOOGLE_APPLICATION_CREDENTIALS = env('GOOGLE_APPLICATION_CREDENTIALS')
# except:
#     pass

# # Set the default storage and bucket name in your settings.py file:
# DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
# try:
#     GS_BUCKET_NAME = env('GS_BUCKET_NAME')
# except:
#     pass

# # To allow django-admin collectstatic to automatically
# # put your static files in your bucket:
# STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

# # Specify file permissions.
# GS_DEFAULT_ACL = 'publicRead'

# # Tell Django the base url to access the static files. Think of this as the 'prefix' of the URL
# # to where your static files are. Note that if you browse through your bucket and happen to see a
# # URL such as 'https://storage.cloud.google.com/<your_bucket_name>/someFileYouHaveUploaded', such
# # URL requires that whoever accesses it should be currently logged-in with their Google accounts. If
# # you want your static files to be publicly accessible by anyone whether they are logged-in or not,
# # use the link 'https://storage.googleapis.com/<your_bucket_name>/someFileYouHaveUploaded' instead.
# STATIC_URL = 'https://storage.googleapis.com/your-lims.appspot.com/'

# # If the command 'collectstatic' is invoked, tell Django where to place all the collected static
# # files from all the directories included in STATICFILES_DIRS. Be aware that configuring it with a
# # path outside your /home/me means that you need to have permissions to write to that folder later
# # on when you invoke 'collectstatic', so you might need to login as root first or run it as sudo.
# STATIC_ROOT = 'https://storage.googleapis.com/your-lims.appspot.com/public/static/'

# ------------------------------------------------------------#
# Sessions
# https://docs.djangoproject.com/en/3.1/topics/http/sessions/
# ------------------------------------------------------------#

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# ------------------------------------------------------------#
# Customization
# ------------------------------------------------------------#

# Remove trailing slash from URLs.
APPEND_SLASH = False

# Allow Django template tags to span multiple lines.
# https://stackoverflow.com/questions/49110044/django-template-tag-on-multiple-line
base.tag_re = re.compile(base.tag_re.pattern, re.DOTALL)

# Host static documentation.
DOCS_DIR = os.path.join(BASE_DIR, f'{PROJECT_NAME}/static/{PROJECT_NAME}/docs')
DOCS_STATIC_NAMESPACE = os.path.basename(DOCS_DIR)

# Optional: Re-write to read docs directory directly.
# MKDOCS_CONFIG = os.path.join(BASE_DIR, 'mkdocs.yml')
# DOCS_DIR = ''
# DOCS_STATIC_NAMESPACE = ''
# with open(MKDOCS_CONFIG, 'r') as f:
#     DOCS_DIR = yaml.load(f, Loader=yaml.Loader)['site_dir']
#     DOCS_STATIC_NAMESPACE = os.path.basename(DOCS_DIR)
