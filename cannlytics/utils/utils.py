"""
Utility Functions | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 8/1/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: This module contains general utility functions.
"""
# Standard imports.
from base64 import b64encode, decodebytes
from datetime import datetime, timedelta
import os
from re import split, sub, findall
import secrets
from typing import Any, Callable, List, Optional, Tuple
from zipfile import ZipFile
try:
    from zoneinfo import ZoneInfo
except ImportError:
    print('Operating with Python < 3.9 is not recommended.')

# External imports.
from dateutil import parser, relativedelta
from fredapi import Fred
from pandas import ExcelWriter, merge, NaT, to_datetime
from pandas.tseries.offsets import MonthEnd
import requests

# Internal imports.
try:
    from cannlytics.utils.constants import (
        RANDOM_STRING_CHARS,
        state_time_zones,
    )
except ImportError:
    print('Failed to load constants.')


#-----------------------------------------------------------------------
# String utilities.
#-----------------------------------------------------------------------

def camelcase(string: str) -> str:
    """Turn a given string to CamelCase.
    Args:
        string (str): A given string to turn to CamelCase.
    Returns:
        (str): A string in CamelCase.
    """
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
    """Turn a camel-case string to a snake-case string.
    This function handles CamelCase better than `snake_case`.
    The function does not do well with all caps, e.g. "APP_ID".
    Args:
        string (str): The string to convert to snake-case.
    Returns:
        (str): Returns the string in snake_case.
    """
    return sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


def kebab_case(string: str) -> str:
    """Turn a string into a kebab-case string."""
    key = string.replace(' ', '-')
    key = key.replace('&', 'and')
    key = key.replace('%', 'percent')
    key = key.replace('#', 'number')
    key = key.replace('$', 'dollars')
    key = key.replace('/', 'to')
    key = key.replace(r'\\', '-').lower()
    key = sub('[!@#$%^&*()[]{};:,./<>?\|`~-=+]', ' ', key)
    keys = findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', key)
    return '-'.join(map(str.lower, keys))


def format_billions(value: float, pos: Optional[int] = None) -> str: #pylint: disable=unused-argument
    """The two args are the value and tick position."""
    return '%1.1fB' % (value * 1e-9)


def format_millions(value: float, pos: Optional[int] = None) -> str: #pylint: disable=unused-argument
    """The two args are the value and tick position."""
    return '%1.1fM' % (value * 1e-6)


def format_thousands(value: float, pos: Optional[int] = None) -> str: #pylint: disable=unused-argument
    """The two args are the value and tick position."""
    return '%1.0fK' % (value * 1e-3)


def get_keywords(string: str) -> List[str]:
    """Get keywords for a given string.
    Args:
        string (str): A string to get keywords for.
    Returns:
        (list): A list of keywords.
    """
    keywords = string.lower().split(' ')
    keywords = [x.strip() for x in keywords if x]
    keywords = list(set(keywords))
    return keywords


def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice,
           this list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.

        3. Neither the name of Django nor the names of its contributors may be used
           to endorse or promote products derived from this software without
           specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    return ''.join(secrets.choice(allowed_chars) for i in range(length))


def sentence_case(s):
    """
    Author: Zizouz212 https://stackoverflow.com/a/39969233/5021266
    License: CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/
    """
    return '. '.join(i.capitalize() for i in s.split('. ')).strip()


REPLACEMENTS = [
    {'text': ' ', 'key': '_'},
    {'text': '&', 'key': 'and'},
    {'text': '%', 'key': 'percent'},
    {'text': '#', 'key': 'number'},
    {'text': '$', 'key': 'dollars'},
    {'text': '/', 'key': 'to'},
    {'text': 'α', 'key': 'alpha'},
    {'text': 'β', 'key': 'beta'},
    {'text': 'γ', 'key': 'gamma'},
    {'text': 'Δ', 'key': 'delta'},
    {'text': 'δ', 'key': 'delta'},
]

def snake_case(string: str) -> str:
    """Turn a given string to snake case.
    Handles CamelCase, replaces known special characters with
    preferred namespaces, replaces spaces with underscores,
    and removes all other nuisance characters.
    Args:
        string (str): The string to turn to snake case.
    Returns:
        (str): A snake case string.
    """
    key = string.replace(r'\\', '_').lower()
    for x in REPLACEMENTS:
        key = key.replace(x['text'], x['key'])
    key = sub('[!@#$%^&*()[]{};:,./<>?\|`~-=+]', ' ', key)
    keys = findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', key)
    return '_'.join(map(str.lower, keys))


def strip_whitespace(string: str) -> str:
    """Strip whitespace from a string."""
    return string.replace('\n', '').strip()


#-----------------------------------------------------------------------
# Number utilities.
#-----------------------------------------------------------------------

def convert_to_numeric(string: str, strip: Optional[str] = False) -> str:
    """Convert a string to numeric, optionally replacing non-numeric
    characters.
    Args:
        string (str): The string to attempt to parse to a number.
    Returns:
        (float): Returns either the original or the parsed number.
    """
    if strip:
        s = sub('[^\d\.]', '', string)
    else:
        s = string
    try:
       return float(s)
    except (TypeError, ValueError):
        return s


#-----------------------------------------------------------------------
# List utilities.
#-----------------------------------------------------------------------

def sandwich_list(a) -> list:
    """Create a range that cycles from start to the end to the middle.
    Credit: Norman <https://stackoverflow.com/a/36533868/5021266>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    Args:
        a (str): The iterable to sandwich.
    Returns:
        (list): The sandwich index.
    """
    return [a[-i//2] if i % 2 else a[i//2] for i in range(len(a))]

def sorted_nicely(unsorted_list: List[str]) -> List[str]:
    """Sort the given iterable in the way that humans expect.
    Credit: Mark Byers <https://stackoverflow.com/a/2669120/5021266>
    License: CC BY-SA 2.5 <https://creativecommons.org/licenses/by-sa/2.5/>
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alpha = lambda key: [convert(c) for c in split('([0-9]+)', key)]
    return sorted(unsorted_list, key=alpha)


def split_list(a_list: list, at_index: Optional[int] = None) -> Tuple:
    """Split a list in half or at a given index.
    Credit: Jason Coon <https://stackoverflow.com/a/752330/5021266>
    License: CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>
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
    """Format dictionary keys with given function, snake case by default.
    Args:
        d (dict): A dictionary to clean.
        function (function): A function to apply to each key.
    Returns:
        (dict): Returns the input dictionary with a function applied to the keys.
    """
    return {function(k): v for k, v in data.items()}


def clean_nested_dictionary(data: dict, function: Callable = snake_case) -> dict:
    """Format nested (at most 2 levels) dictionary keys with a given function,
    snake case by default.
    Args:
        d (dict): A dictionary to clean, allowing dictionaries as values.
        function (function): A function to apply to each key.
    Returns:
        (dict): Returns the input dictionary with cleaned keys.
    """
    clean = clean_dictionary(data, function)
    for k, value in clean.items():
        try:
            clean[k] = clean_dictionary(value, function)
        except AttributeError:
            pass
    return clean


def remove_dict_fields(data: dict, fields: List[str]) -> dict:
    """Remove multiple keys from a dictionary.
    Args:
        data (dict): The dictionary to clean.
        fields (list): A list of keys (str) to remove.
    Returns:
        (dict): Returns the dictionary with the keys removed.
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
        (dict): Returns the dictionary with the keys with
            null values removed.
    """
    return {k: v for k, v in data.items() if v is not None}


def update_dict(context: dict, function: Callable = camel_to_snake, **kwargs) -> dict:
    """Update dictionary with keyword arguments.
    Args:
        context (dict): A dictionary of context to update.
        function (function): Function to apply to final dictionary keys.
        kwargs (*args): Key/value arguments to update in the dictionary.
    Returns:
        (dict): Returns the dictionary with updated keys.
    """
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
    """
    Args:
        data (DataFrame): A DataFrame with any column names.
        column (str): The column of the DataFrame to clean.
    Returns:
        (DataFrame): A DataFrame with snake_case column names.
    """
    data[column] = data[column].str.strip()
    data[column] = data[column].str.rstrip('.)]')
    data[column] = data[column].str.replace('%', 'percent', regex=True)
    data[column] = data[column].str.replace('#', 'number', regex=True)
    data[column] = data[column].str.replace('[/,]', '_', regex=True)
    data[column] = data[column].str.replace('[.,(,)]', '', regex=True)
    data[column] = data[column].str.replace("\'", '', regex=True)
    data[column] = data[column].str.replace("[[]", '_', regex=True)
    data[column] = data[column].str.replace(r"[]]", '', regex=True)
    data[column] = data[column].str.replace('β', 'beta', regex=True)
    data[column] = data[column].str.replace('Δ', 'delta', regex=True)
    data[column] = data[column].str.replace('δ', 'delta', regex=True)
    data[column] = data[column].str.replace('α', 'alpha', regex=True)
    data[column] = data[column].str.replace('__', '', regex=True)
    return data


def end_of_period_timeseries(data: Any, period: Optional[str] = 'M') -> Any:
    """Convert a DataFrame from beginning-of-the-period to
    end-of-the-period timeseries.
    Args:
        data (DataFrame): The DataFrame to adjust timestamps.
        period (str): The period of the time series, monthly "M" by default.
    Returns:
        (DataFrame): The adjusted DataFrame, with end-of-the-month timestamps.
    """
    data.index = data.index.to_period(period).to_timestamp(period)
    return data


def nonzero_columns(data):
    """Return the non-zero column names of a DataFrame."""
    nonzero = (data != 0).any()
    return data.columns[nonzero].to_list()


def nonzero_rows(data):
    """Return the non-zero row keys of a DataFrame."""
    nonzero = (data != 0)
    return nonzero.index[nonzero].to_list()


def combine_columns(
        df: Any,
        new_key: str,
        old_key: str,
        drop: Optional[bool] = True,
    ):
    """Combine two numeric columns of a DataFrame.
    Args:
        df (DataFrame): The DataFrame with the columns.
        new_key (str): The column to have values filled.
        old_key (str): The column to use to fill values.
        drop (bool): Whether or not to drop the old column, the default
            is `True` (optional).
    Returns:
        (DataFrame): Returns the DataFrame with combined columns.
    """
    df.loc[df[new_key] == 0, new_key] = df[old_key]
    df[new_key].fillna(df[old_key], inplace=True)
    if drop:
        df.drop(columns=[old_key], inplace=True)
    return df


def reverse_dataframe(data: Any) -> Any:
    """Reverse the ordering of a DataFrame.
    Args:
        data (DataFrame): A DataFrame to re-order.
    Returns:
        (DataFrame): The re-ordered DataFrame.
    """
    return data[::-1].reset_index(drop=True)


def sum_columns(
        df: Any,
        new_key: str,
        columns: list,
        drop: Optional[bool] = True,
    ):
    """Sum multiple numeric columns of a DataFrame.
    Args:
        df (DataFrame): The DataFrame with the columns.
        new_key (str): The column to have values filled.
        columns (list): The columns to use to fill values.
        drop (bool): Whether or not to drop the old column, the default
            is `True` (optional).
    Returns:
        (DataFrame): Returns the DataFrame with summed columns.
    """
    df[new_key] = 0
    for column in columns:
        df[new_key] += df[column].fillna(0)
    if drop:
        df.drop(columns=columns, inplace=True)
    return df


def rmerge(left, right, **kwargs):
    """Perform a merge using pandas with optional removal of overlapping
    column names not associated with the join.

    Though I suspect this does not adhere to the spirit of pandas merge
    command, I find it useful because re-executing IPython notebook cells
    containing a merge command does not result in the replacement of existing
    columns if the name of the resulting DataFrame is the same as one of the
    two merged DataFrames, i.e. data = pa.merge(data, df). I prefer
    this command over pandas df.combine_first() method because it has more
    flexible join options.

    The column removal is controlled by the 'replace' flag which is
    'left' (default) or 'right' to remove overlapping columns in either the
    left or right DataFrame. If 'replace' is set to None, the default
    pandas behavior will be used. All other parameters are the same
    as pandas merge command.

    Author: Michelle Gill
    Source: https://gist.github.com/mlgill/11334821

    Examples
    --------
    >>> left       >>> right
       a  b   c       a  c   d
    0  1  4   9    0  1  7  13
    1  2  5  10    1  2  8  14
    2  3  6  11    2  3  9  15
    3  4  7  12

    >>> rmerge(left,right,on='a')
       a  b  c   d
    0  1  4  7  13
    1  2  5  8  14
    2  3  6  9  15

    >>> rmerge(left,right,on='a',how='left')
       a  b   c   d
    0  1  4   7  13
    1  2  5   8  14
    2  3  6   9  15
    3  4  7 NaN NaN

    >>> rmerge(left,right,on='a',how='left',replace='right')
       a  b   c   d
    0  1  4   9  13
    1  2  5  10  14
    2  3  6  11  15
    3  4  7  12 NaN

    >>> rmerge(left,right,on='a',how='left',replace=None)
       a  b  c_x  c_y   d
    0  1  4    9    7  13
    1  2  5   10    8  14
    2  3  6   11    9  15
    3  4  7   12  NaN NaN
    """

    # Function to flatten lists from http://rosettacode.org/wiki/Flatten_a_list#Python
    def flatten(lst):
        return sum(([x] if not isinstance(x, list) else flatten(x) for x in lst), [])

    # Set default for removing overlapping columns in "left" to be true
    myargs = {'replace':'left'}
    myargs.update(kwargs)

    # Remove the replace key from the argument dict to be sent to
    # pandas merge command
    kwargs = {k:v for k, v in myargs.items() if k != 'replace'}

    if myargs['replace'] is not None:
        # Generate a list of overlapping column names not associated with the join
        skip_cols = set(flatten([v for k, v in myargs.items() if k in ['on', 'left_on', 'right_on']]))
        left_cols = set(left.columns)
        right_cols = set(right.columns)
        drop_cols = list((left_cols & right_cols).difference(skip_cols))

        # Remove the overlapping column names from the appropriate DataFrame
        if myargs['replace'].lower() == 'left':
            left = left.copy().drop(drop_cols, axis=1)
        elif myargs['replace'].lower() == 'right':
            right = right.copy().drop(drop_cols, axis=1)

    return merge(left, right, **kwargs)


def set_training_period(series: Any, date_start: str, date_end: str) -> Any:
    """Helper function to restrict a series to the desired
    training time period.
    Args:
        series (Series): The series to clean.
        date_start (str): An ISO date to mark the beginning of the training period.
        date_end (str): An ISO date to mark the end of the training period.
    Returns
        (Series): The series restricted to the desired time period.
    """
    return series.loc[
        (series.index >= to_datetime(date_start)) & \
        (series.index < to_datetime(date_end))
    ]


def to_excel_with_style(
        df: Any,
        file_name: str,
        index: Optional[bool] = False,
        sheet_name: Optional[str] = 'Sheet1',
        style: Optional[dict] = None,
    ):
    """Save a DataFrame to Excel with no style.
    Args:
        df (DataFrame): The data to save.
        file_name (str): The name of the file.
        index (bool): Whether to include the index, `False` by default (optional).
        sheet_name (str): The name for the worksheet, `Sheet1` by default (optional).
        style (dict): The style to apply to the headers (optional). Applies
            a light green background with an underline by default.
    """
    if style is None:
        style = {'bottom': 1, 'bg_color': '#EBF1DE'}
    writer = ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(writer, index=index, sheet_name=sheet_name, startrow=1, header=False)
    worksheet = writer.sheets[sheet_name]
    workbook = writer.book
    bold = workbook.add_format(style)
    for idx, val in enumerate(df.columns):
        worksheet.write(0, idx, val, bold)
    writer.save()


#-----------------------------------------------------------------------
# Time utilities.
#-----------------------------------------------------------------------

def convert_month_year_to_date(x):
    """Convert a month, year series to datetime. E.g. `'April 2022'`."""
    try:
        return datetime.strptime(x.replace('.0', ''), '%B %Y')
    except:
        return NaT


def end_of_month(value: datetime) -> str:
    """Format a datetime as an ISO formatted date at the end of the month.
    Args:
        value (datetime): A datetime value to transform into an ISO date.
    Returns:
        (str): An ISO formatted date.
    """
    month = value.month
    if month < 10:
        month = f'0{month}'
    year = value.year
    day = value + MonthEnd(0)
    return f'{year}-{month}-{day.day}'


def end_of_year(value: datetime) -> str:
    """Format a datetime as an ISO formatted date at the end of the year.
    Args:
        value (datetime): A datetime value to transform into an ISO date.
    Returns:
        (str): An ISO formatted date.
    """
    return f'{value.year}-12-31'


def format_iso_date(date: str, sep: Optional[str] = '/') -> str:
    """Format a human-written date into an ISO formatted date.
    Ags:
        date (str): A human-written date.
        sep (str): The separating character, '/' by default (optional).
    Returns:
        (str): An ISO formatted date string.
    """
    mm, dd, yyyy = tuple(date.split(sep))
    if len(mm) == 1:
        mm = f'0{mm}'
    if len(dd) == 1:
        dd = f'0{dd}'
    if len(yyyy) == 2:
        yyyy = f'20{yyyy}'
    return '-'.join([yyyy, mm, dd])


def get_timestamp(
        date: Optional[str] = None,
        past: Optional[int] = 0,
        future: Optional[int] = 0,
        zone: Optional[str] = 'utc'
) -> str:
    """Get an ISO formatted timestamp.
    Args:
        date (str): An optional date to pin the timestamp to a specific time.
        past (int): Number of minutes in the past to get a timestamp.
        future (int): Number of minutes into the future to get a timestamp.
        zone (str): A specific timezone or US state abbreviation, e.g. CA.
    Returns:
        (str): An ISO formatted date/time string in the specified time zone,
            UTC by default.
    """
    time_zone = state_time_zones.get(str(zone).upper(), zone)
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


def months_elapsed(start, end):
    """Calculate the months elapsed between two datetimes,
    returning 0 if a negative time span.
    """
    diff = relativedelta.relativedelta(end, start)
    time_span = diff.months + diff.years * 12
    return time_span if time_span > 0 else 0


#-----------------------------------------------------------------------
# File utilities.
#-----------------------------------------------------------------------

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


def get_directory_files(
        target_dir: str,
        file_type: Optional[str] = 'pdf',
    ) -> list:
    """Get all of the files of a specified type in a given directory.
    Args:
        target_dir (str): The directory containing the files.
        file_type (str): The file type extension, 'pdf' by default (optional).
    Returns:
    """
    return [
        os.path.join(target_dir, f) for f in os.listdir(target_dir) \
        if os.path.isfile(os.path.join(target_dir, f)) \
        and f.endswith(file_type)
    ]


def get_blocks(files, size=65536):
    """Get a block of a file by the given size."""
    while True:
        block = files.read(size)
        if not block: break
        yield block


def get_number_of_lines(file_name, encoding='utf-16', errors='ignore'):
    """
    Read the number of lines in a large file.
    Credit: glglgl, SU3 <https://stackoverflow.com/a/9631635/5021266>
    License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/>
    """
    with open(file_name, 'r', encoding=encoding, errors=errors) as f:
        count = sum(bl.count('\n') for bl in get_blocks(f))
        print('Number of rows:', count)
        return count


def download_file_from_url(url, destination='', ext=''):
    """Download a file from a URL to a given directory.
    Author: H S Umer farooq <https://stackoverflow.com/a/53153505>
    License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
    """
    get_response = requests.get(url,stream=True)
    file_name = snake_case(url.split('/')[-1])
    file_path = os.path.join(destination, file_name + ext)
    with open(file_path, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return file_path


def unzip_files(zip_dir, extension='.zip'):
    """Unzip all files in a specified folder. Alternatively,
    pass a .zip file to extract that file.
    Author: nlavr https://stackoverflow.com/a/69101930
    License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/
    """
    single = ''
    zip_destinations = []
    if isinstance(zip_dir, str):
        parts = zip_dir.split('/')
        single = parts[-1]
        doc_dir = '/'.join(parts[:-1])
        if doc_dir == '':
            doc_dir = '.'
    else:
        doc_dir = zip_dir
    for item in os.listdir(doc_dir):
        if single and single not in item:
            continue
        abs_path = os.path.join(doc_dir, item)
        if item.endswith(extension):
            file_name = os.path.abspath(abs_path)
            zip_dest = os.path.join(doc_dir, item)
            if not os.path.exists(zip_dest):
                os.makedirs(zip_dest)
            zip_ref = ZipFile(file_name)
            zip_ref.extractall(zip_dest)
            zip_ref.close()
            os.remove(file_name)
            zip_destinations.append(zip_dest)
        elif os.path.isdir(abs_path):
            unzip_files(abs_path)
    return zip_destinations
