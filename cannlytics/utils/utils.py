# -*- coding: utf-8 -*-
"""
cannlytics.traceability..utils.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains general cannabis analytics utility functions.
"""

from datetime import datetime, timedelta
from re import sub, findall


def camelcase(string):
    """Turn a given string to CamelCase.
    Args:
        string (str): A given string to turn to CamelCase.
    Returns:
        (str): A string in CamelCase.
    """
    key = ''.join(x for x in string.title() if not x.isspace())
    key = key.replace('_', '').replace('-', '')
    return key


def get_timestamp(past=0, future=0, time_zone='local'):
    """Get an ISO formatted timestamp.
    Args:
        past (int): Number of minutes in the past to get a timestamp.
        future (int): Number of minutes into the future to get a timestamp.
        time_zone (str): UNIMPLEMENTED Set a given timezone.
    Returns:
        (str): An ISO formatted date/time string.
    """
    now = datetime.now()
    now += timedelta(minutes=future)
    now -= timedelta(minutes=past)
    if time_zone is None:
        return now.isoformat()[:19]
    else:
        return now.isoformat()


def snake_case(string):
    """Turn a given string to snake case.
    Handles CamelCase, replaces known special characters with
    preferred namespaces, replaces spaces with underscores,
    and removes all other nuisance characters.
    Args:
        string (str): The string to turn to snake case.
    Returns"
        (str): A snake case string.
    """
    key = string.replace(' ', '_')
    key = key.replace('&', 'and')
    key = key.replace('%', 'percent')
    key = key.replace('#', 'number')
    key = key.replace('$', 'dollars')
    key = key.replace('/', '_')
    key = key.replace(r'\\', '_')
    key = sub('[!@#$%^&*()[]{};:,./<>?\|`~-=+]', ' ', key)
    keys = findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', key)
    return '_'.join(map(str.lower, keys))
