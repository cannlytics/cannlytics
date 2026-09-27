"""
Utility Functions | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 9/26/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: This module contains general Cannlytics utility functions.
"""
# Standard imports:
import unicodedata
from datetime import datetime, timedelta
import glob
import json
import os
from re import split, sub, findall
import secrets
from typing import Any, Callable, List, Optional, Tuple
try:
    from zoneinfo import ZoneInfo
except ImportError as _zoneinfo_error:  # pragma: no cover
    # `zoneinfo` is stdlib from Python 3.9. A library must not print to
    # stdout at import time, and letting this pass would only defer the
    # failure to a later NameError on ZoneInfo.
    raise ImportError(
        'cannlytics requires Python 3.9 or later (zoneinfo is unavailable).'
    ) from _zoneinfo_error

# External imports:
from dateutil import parser
from pandas import ExcelWriter, merge

# Internal imports:
from cannlytics.constants import RANDOM_STRING_CHARS  # noqa: F401 (re-exported)
from cannlytics.constants.states import TIME_ZONES as state_time_zones  # noqa: F401 (re-exported)
from cannlytics.utils.hashing import hash_file  # noqa: F401 (re-exported)

# A map of state abbreviations to timezone.

#-----------------------------------------------------------------------
# String utilities.
#-----------------------------------------------------------------------

def camelcase(string: str) -> str:
    """Turn a given string to CamelCase."""
    key = string.replace('&', 'and')
    key = key.replace('%', 'percent')
    key = key.replace('#', 'number')
    key = key.replace('$', 'dollars')
    key = key.replace('/', 'to')
    key = key.replace('.', '_')
    key = ''.join(x for x in key.title() if not x.isspace())
    key = key.replace('_', '').replace('-', '')
    return key

def camel_to_snake(string: str) -> str:
    """Turn a camel-case string to a snake-case string."""
    return sub(r'(?<!^)(?=[A-Z])', '_', string).lower()

def kebab_case(string: str, max_length: Optional[int] = None) -> str:
    """Turn a string into a kebab-case slug, for IDs and URLs.

    One rule for strain IDs, analyte slugs, and license slugs, which had
    three (``to_kebab_case`` in cannabis_strains, ``kebab_case`` in
    cannabis_analytes, ``slugify`` in cannabis_licenses). Characters are
    folded or spelled out rather than deleted, so that spellings of one
    name share one slug:

    - Accents fold (``Café Racer`` is ``cafe-racer``, not ``caf-racer``)
      and Greek letters are spelled (``Δ9-THC`` is ``delta-9-thc``).
    - ``&`` is ``and``: ``Cookies & Cream`` and ``Cookies and Cream``
      share ``cookies-and-cream``.
    - Apostrophes and abbreviation periods are dropped:
      ``Charlotte's Web`` is ``charlottes-web``, ``GSC (f.k.a. Girl
      Scout Cookies)`` is ``gsc-fka-girl-scout-cookies``.
    - Every other run of punctuation or space is one hyphen: ``GG#4``,
      ``GG 4``, and ``GG-4`` are all ``gg-4``.
    - Trademark signs are dropped.

    Args:
        string: The text to slug.
        max_length: Truncate to this many characters (never ending in
            a hyphen).

    Returns:
        A lower-case ASCII slug, possibly empty.
    """
    text = str(string).replace('&', ' and ')
    for symbol, spelled in GREEK_LETTERS.items():
        text = text.replace(symbol, spelled)
    for symbol in TRADEMARK_SYMBOLS:
        text = text.replace(symbol, '')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.replace("'", '')
    text = sub(r'(?<=[A-Za-z])\.', '', text)          # f.k.a. -> fka; 1.0 keeps its point
    slug = sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    # 'delta9-thc' (from 'Δ9-THC') reads better as 'delta-9-thc'.
    slug = sub(r'(delta|alpha|beta|gamma)(\d)', r'\1-\2', slug)
    if max_length is not None:
        slug = slug[:max_length].rstrip('-')
    return slug

# `kebab_case` under the name most people look for.
slugify = kebab_case

def get_keywords(string: str) -> List[str]:
    """Get keywords for a given string."""
    keywords = string.lower().split(' ')
    keywords = [x.strip() for x in keywords if x]
    keywords = list(set(keywords))
    return keywords

def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    """Return a securely generated random string.
    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved. BSD License.
    """
    return ''.join(secrets.choice(allowed_chars) for i in range(length))

# Symbols that carry no meaning in a key or slug.
TRADEMARK_SYMBOLS = ('\u2122', '\u00ae', '\u00a9', '\u2120')

# Greek letters spelled out, so that keys and slugs are ASCII.
GREEK_LETTERS = {
    '\u03b1': 'alpha', '\u03b2': 'beta', '\u03b3': 'gamma',
    '\u0394': 'delta', '\u03b4': 'delta', '\u00b5': 'u', '\u03bc': 'u',
}

REPLACEMENTS = [
    {'text': ' ', 'key': '_'},
    {'text': '&', 'key': 'and'},
    {'text': '%', 'key': 'percent'},
    {'text': '#', 'key': 'number'},
    {'text': '$', 'key': 'dollars'},
    {'text': '/', 'key': 'to'},
    {'text': '\u03b1', 'key': 'alpha'},
    {'text': '\u03b2', 'key': 'beta'},
    {'text': '\u03b3', 'key': 'gamma'},
    {'text': '\u0394', 'key': 'delta'},
    {'text': '\u03b4', 'key': 'delta'},
]

def snake_case(string: str) -> str:
    """Turn a given string to snake case.
    Handles CamelCase, replaces known special characters with
    preferred namespaces, replaces spaces with underscores,
    and removes all other nuisance characters.
    """
    key = string.replace(r'\\', '_').lower()
    for x in REPLACEMENTS:
        key = key.replace(x['text'], x['key'])
    key = sub(r'[!@#$%^&*()\[\]{};:,./<>?\\|`~\-=+]', ' ', key)
    keys = findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', key)
    return '_'.join(map(str.lower, keys))

def strip_whitespace(string: str) -> str:
    """Strip whitespace from a string."""
    return string.replace('\n', '').strip()

#-----------------------------------------------------------------------
# Number utilities.
#-----------------------------------------------------------------------

def convert_to_numeric(string: str, strip: Optional[str] = False) -> Any:
    """Convert a string to numeric, optionally replacing non-numeric characters."""
    if strip:
        s = sub(r'[^\d.]', '', string)
    else:
        s = string
    try:
       return float(s)
    except (TypeError, ValueError):
        return s

#-----------------------------------------------------------------------
# List utilities.
#-----------------------------------------------------------------------

def sorted_nicely(unsorted_list: List[str]) -> List[str]:
    """Sort the given iterable in a way that humans would expect.
    Credit: Mark Byers <https://stackoverflow.com/a/2669120/5021266>
    License: CC BY-SA 2.5
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alpha = lambda key: [convert(c) for c in split('([0-9]+)', key)]
    return sorted(unsorted_list, key=alpha)

def split_list(a_list: list, at_index: Optional[int] = None) -> Tuple:
    """Split a list in half or at a given index.
    Credit: Jason Coon <https://stackoverflow.com/a/752330/5021266>
    License: CC BY-SA 4.0
    """
    if at_index:
        half = at_index
    else:
        half = len(a_list)//2
    return a_list[:half], a_list[half:]

#-----------------------------------------------------------------------
# Dictionary utilities.
#-----------------------------------------------------------------------

def clean_dictionary(data: dict, function: Callable = snake_case) -> dict:
    """Format dictionary keys with given function, snake case by default."""
    return {function(k): v for k, v in data.items()}

def clean_nested_dictionary(data: dict, function: Callable = snake_case) -> dict:
    """Format nested (at most 2 levels) dictionary keys with a given function,
    snake case by default. Handles list of dictionaries."""
    clean = clean_dictionary(data, function)
    for k, value in clean.items():
        if isinstance(value, list):
            x = []
            for v in value:
                try:
                    x.append(clean_nested_dictionary(v, function))
                except (AttributeError, TypeError):
                    x.append(v)
            clean[k] = x
        elif isinstance(value, dict):
            try:
                clean[k] = clean_nested_dictionary(value, function)
            except AttributeError:
                pass
    return clean

def remove_dict_fields(data: dict, fields: List[str]) -> dict:
    """Remove multiple keys from a dictionary."""
    for key in fields:
        if key in data:
            del data[key]
    return data

def remove_dict_nulls(data: dict) -> dict:
    """Return a shallow copy of a dictionary with all `None` values excluded."""
    return {k: v for k, v in data.items() if v is not None}

def update_dict(context: dict, function: Callable = camel_to_snake, **kwargs) -> dict:
    """Update dictionary with keyword arguments."""
    entry = {}
    for key in kwargs:
        entry[key] = kwargs[key]
    data = {
        **clean_nested_dictionary(context, function),
        **clean_nested_dictionary(entry, function)
    }
    return data

#-----------------------------------------------------------------------
# DataFrame utilities.
#-----------------------------------------------------------------------

def clean_column_strings(data: Any, column: str) -> Any:
    """Clean the column names of a given DataFrame."""
    data[column] = data[column].str.strip()
    data[column] = data[column].str.rstrip('.)]')
    data[column] = data[column].str.replace('%', 'percent', regex=True)
    data[column] = data[column].str.replace('#', 'number', regex=True)
    data[column] = data[column].str.replace('[/,]', '_', regex=True)
    data[column] = data[column].str.replace('[.,(,)]', '', regex=True)
    data[column] = data[column].str.replace("\'", '', regex=True)
    data[column] = data[column].str.replace('[', '_', regex=False)
    data[column] = data[column].str.replace(r"[]]", '', regex=True)
    data[column] = data[column].str.replace('\u03b2', 'beta', regex=True)
    data[column] = data[column].str.replace('\u0394', 'delta', regex=True)
    data[column] = data[column].str.replace('\u03b4', 'delta', regex=True)
    data[column] = data[column].str.replace('\u03b1', 'alpha', regex=True)
    data[column] = data[column].str.replace('__', '', regex=True)
    return data

def dump_column(x):
    """Turn a column from JSON to dictionaries, handling errors."""
    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None

def nonzero_columns(data):
    """Return the non-zero column names of a DataFrame."""
    nonzero = (data != 0).any()
    return data.columns[nonzero].to_list()

def nonzero_rows(data):
    """Return the index labels of the non-zero values of a Series."""
    nonzero = (data != 0)
    return nonzero.index[nonzero].to_list()

def rmerge(left, right, **kwargs):
    """Perform a merge using pandas with optional removal of overlapping
    column names not associated with the join.
    Author: Michelle Gill
    Source: https://gist.github.com/mlgill/11334821
    """
    def flatten(lst):
        return sum(([x] if not isinstance(x, list) else flatten(x) for x in lst), [])
    myargs = {'replace':'left'}
    myargs.update(kwargs)
    kwargs = {k:v for k, v in myargs.items() if k != 'replace'}
    if myargs['replace'] is not None:
        skip_cols = set(flatten([v for k, v in myargs.items() if k in ['on', 'left_on', 'right_on']]))
        left_cols = set(left.columns)
        right_cols = set(right.columns)
        drop_cols = list((left_cols & right_cols).difference(skip_cols))
        if myargs['replace'].lower() == 'left':
            left = left.copy().drop(drop_cols, axis=1)
        elif myargs['replace'].lower() == 'right':
            right = right.copy().drop(drop_cols, axis=1)
    return merge(left, right, **kwargs)

def to_excel_with_style(
        df: Any,
        file_name: str,
        index: Optional[bool] = False,
        sheet_name: Optional[str] = 'Sheet1',
        style: Optional[dict] = None,
    ):
    """Save a DataFrame to Excel with styled headers.

    Requires ``XlsxWriter`` from the `utils` extra.
    """
    if style is None:
        style = {'bottom': 1, 'bg_color': '#EBF1DE'}
    try:
        writer = ExcelWriter(file_name, engine='xlsxwriter')
    except ImportError as error:
        raise ImportError(
            '`to_excel_with_style` requires the `utils` extra. Install it '
            'with:\n\n    pip install "cannlytics[utils]"\n'
        ) from error
    df.to_excel(writer, index=index, sheet_name=sheet_name, startrow=1, header=False)
    worksheet = writer.sheets[sheet_name]
    workbook = writer.book
    bold = workbook.add_format(style)
    for idx, val in enumerate(df.columns):
        worksheet.write(0, idx, val, bold)
    writer.close()

#-----------------------------------------------------------------------
# Time utilities.
#-----------------------------------------------------------------------

def format_iso_date(date: str, sep: Optional[str] = '/') -> str:
    """Format a human-written date into an ISO formatted date."""
    mm, dd, yyyy = tuple(date.split(sep))
    if len(mm) == 1:
        mm = f'0{mm}'
    if len(dd) == 1:
        dd = f'0{dd}'
    if len(yyyy) == 2:
        yyyy = f'20{yyyy}'
    return '-'.join([yyyy, mm, dd])

def get_date_range(start_date: str, end_date: str):
    """Generates a list of tuples containing ISO-formatted date strings
    for each consecutive day in a given range of dates."""
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = timedelta(days=1)
    date_range = []
    while start_date <= end_date:
        start = start_date.strftime('%Y-%m-%d')
        end = (start_date + delta).strftime('%Y-%m-%d')
        date_range.append((start, end))
        start_date += delta
    return date_range

def get_timestamp(
        date: Optional[str] = None,
        past: Optional[int] = 0,
        future: Optional[int] = 0,
        zone: Optional[str] = 'UTC'
) -> str:
    """Get an ISO formatted timestamp."""
    time_zone = state_time_zones.get(str(zone).upper(), zone)
    # IANA zone keys are case-sensitive and the canonical UTC key is
    # 'UTC'. A lowercase 'utc' falls through the lookup above and then
    # raises ZoneInfoNotFoundError, so normalize it here.
    if isinstance(time_zone, str) and time_zone.lower() == 'utc':
        time_zone = 'UTC'
    if date:
        now = parser.parse(date).replace(tzinfo=ZoneInfo(time_zone))
    elif time_zone is None:
        now = datetime.now()
    else:
        now = datetime.now(ZoneInfo(time_zone))
    now += timedelta(minutes=future)
    now -= timedelta(minutes=past)
    if time_zone is None:
        return now.isoformat()[:19]
    else:
        return now.isoformat()

#-----------------------------------------------------------------------
# File utilities.
#-----------------------------------------------------------------------

def get_directory_files(
        target_dir: str,
        file_type: Optional[str] = 'pdf',
    ) -> list:
    """Get all of the files of a specified type in a given directory."""
    return [
        os.path.join(target_dir, f) for f in os.listdir(target_dir) \
        if os.path.isfile(os.path.join(target_dir, f)) \
        and f.endswith(file_type)
    ]

def find_latest_file(data_dir: str, slug='all', ext='.xlsx') -> str:
    """Find the most recently modified data file in a specified directory
    that includes a given slug and extension in the title."""
    search_pattern = os.path.join(data_dir, f'*{slug}*-*-*-*-*{ext}')
    files = glob.glob(search_pattern)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    if files:
        return files[0]
    else:
        return ''
