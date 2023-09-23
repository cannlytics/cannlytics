#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

Usage:

    set PROJECT=console & python manage.py runserver

"""
import os
import sys


def main():
    """ Run administrative tasks. """
    # Allow user to specify project from the command line.
    project = os.environ.get('PROJECT', 'website').strip()
    print('DJANGO PROJECT:', project)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project}.settings')
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
