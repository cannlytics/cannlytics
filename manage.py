#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ

def main():
    """Run administrative tasks."""
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'console.settings'
    )

    # Set Google Application credentials.
    try:
        # FIXME:
        env = environ.Env()
        env.read_env('.env')
        credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    except:
        print('Could not set GOOGLE_APPLICATION_CREDENTIALS')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
