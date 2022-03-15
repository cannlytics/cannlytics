"""
Metrc Utility Functions | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

This module contains common Metrc utility functions.
"""
# Standard imports.
from base64 import b64encode, decodebytes
from datetime import datetime, timedelta
from re import sub
from typing import Callable, List

# External imports.
from pandas import read_csv

# Internal imports.
from .constants import parameters


def camel_to_snake(text: str) -> str:
    """Turn a camel-case string to a snake-case string.
    Args:
        text (str): The string to convert to snake-case.
    Returns:
        (str): Returns the string in snake_case.
    """
    return sub(r'(?<!^)(?=[A-Z])', '_', text).lower()


def snake_to_camel(text: str) -> str:
    """Turn a snake-case string to a camel-case string.
    Args:
        text (str): The string to convert to camel-case.
    Returns:
        (str): Returns the string in CamelCase
    """
    return ''.join([*map(str.title, text.split('_'))])


def clean_dictionary(data: dict, function: Callable = camel_to_snake) -> dict:
    """Format dictionary keys with given function, snake case by default.
    Args:
        data (dict): A dictionary to clean.
        function (function): A function to apply to each key.
    Returns:
        (dict): Returns the input dictionary with a function applied to the keys.
    """
    return {function(k): v for k, v in data.items()}


def clean_nested_dictionary(data: dict, function: Callable = camel_to_snake) -> dict:
    """Format nested (at most 2 levels) dictionary keys with a given function,
    snake case by default.
    Args:
        data (dict): A dictionary to clean, allowing dictionaries as values.
        function (function): A function to apply to each key.
    Returns:
        (dict): Returns the input dictionary with cleaned keys.
    """
    clean = clean_dictionary(data, function)
    for key, value in clean.items():
        try:
            clean[key] = clean_dictionary(value, function)
        except AttributeError:
            pass
    return clean


def decode_pdf(data: str, destination: str):
    """Save an base-64 encoded string as a PDF.
    Args:
        data (str): Base-64 encoded string representing a PDF.
        destination (str): The destination for the PDF file.
    """
    bits = decodebytes(data)
    with open(destination, 'wb') as pdf:
        pdf.write(bits)


def encode_pdf(filename: str) -> str:
    """Open a PDF file in binary mode.
    Args:
        filename (str): The full file path of a PDF to encode.
    Returns:
        (str): A string encoded in base-64.
    """
    with open(filename, 'rb') as pdf:
        return b64encode(pdf.read())


def format_params(**kwargs: dict) -> dict:
    """Format Metrc request parameters.
    Args:
        kwargs (dict): Keywords to format as parameters.
    Returns:
        (dict): Returns the parameters as a dictionary.
    """
    params = {}
    for param in kwargs:
        if kwargs[param]:
            key = parameters[param]
            params[key] = kwargs[param]
    return params


def get_timestamp(past: int = 0, future: int = 0, time_zone: str = 'local') -> str:
    """Get an ISO formatted timestamp.
    Args:
        past (int): Number of minutes in the past to get a timestamp.
        future (int): Number of minutes into the future to get a timestamp.

    # TODO: Set time in timezone of state (e.g. {'state': 'OK'} -> CDT)
    """
    now = datetime.now()
    now += timedelta(minutes=future)
    now -= timedelta(minutes=past)
    if time_zone is None:
        return now.isoformat()[:19]
    else:
        return now.isoformat()


def remove_dict_fields(data: dict, fields: List[str]):
    """Remove multiple keys from a dictionary.
    Args:
        data (dict): The dictionary to clean.
        fields (list): A list of keys (str) to remove.
    Returns:
        (dict): Returns the dictionary with specified fields removed.
    """
    for key in fields:
        if key in data:
            del data[key]
    return data


def remove_dict_nulls(data: dict) -> dict:
    """Return a shallow copy of a dictionary with all `None` values excluded.
    Args:
        data (dict): The dictionary to reduce.
    Returns:
        (dict): Returns the dictionary without keys that have null values.
    """
    return {k: v for k, v in data.items() if v is not None}


def update_context(context: dict, function: Callable = snake_to_camel, **kwargs: dict) -> dict:
    """Update context with keyword arguments.
    Args:
        context (dict): Data to be formatted.
        function (function): Function to apply to final dictionary keys.
        kwargs (dict): Key / value pairs to add to the data.
    Returns:
        (dict): Returns data nicely formatted.
    """
    entry = {}
    for key in kwargs:
        entry[key] = kwargs[key]
    data = {
        **clean_nested_dictionary(context, function),
        **clean_nested_dictionary(entry, function)
    }
    return data


def import_tags(file_path: str) -> dict:
    """Import plant and package tags.
    Args:
        file_path (str): The file location of the tags.
    Returns:
        (dict): Returns the tags as a dictionary.
    """
    records = read_csv(file_path, sep=',')
    data = records.to_dict('records')
    return clean_dictionary(data)


# TODO: Data import
# 1. Create Plantings / Plantings from Plants / Plantings from Packages
# 2. Immature Plants Growth Phase
# 3. Record Immature Plants Waste
# 4. Immature Plants Packages
# 5. Destroy Immature Plants
# 6. Plants Location
# 7. Plants Growth Phase
# 8. Record Plants Waste
# 9. Manicure Plants
# 10.Harvest Plants
# 11.Destroy Plants
# 12.Packages from Harvest
# 13.Lab Results
# 14.Package Adjustment
# 15.Sales (new)
# 16.Sales (update)
# If uploading multiple types of CSV files, it is recommended that they be uploaded in the
# order listed above to avoid data collisions. For instance, if uploading a CSV to
# Manicure Plants and another to Destroy Plants and the same plant is included on both
# files, the manicure must be recorded prior to the destruction of the plant.
# Except for Lab Results, all CSV files are limited to 500 rows per file. When adding
# plants to the same harvest or manicure batch using multiple CSV files, it is
# recommended that they be uploaded one file at a time.
# Please reference the CA CSV Guide available under the Metrc Support menu for
# additional Data Import assistance.
