"""
Utility Functions | Cannabis Data Science
Copyright (c) 2021-2022 Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 10/27/2021
Updated: 1/18/2022
License: MIT License <https://opensource.org/licenses/MIT>
"""
# Standard imports.
from datetime import datetime
import re
from typing import Any, List, Optional, Tuple

# External imports.
import pandas as pd
from pandas import DataFrame, Series, to_datetime
from pandas.tseries.offsets import MonthEnd


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


def end_of_period_timeseries(data: DataFrame, period: Optional[str] = 'M') -> DataFrame:
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


# def forecast_arima(
#         model: Any,
#         forecast_horizon: Any,
#         exogenous: Optional[Any] = None,
# ) -> Tuple[Any]:
#     """Format an auto-ARIMA model forecast as a time series.
#     Args:
#         model (ARIMA): An pmdarima auto-ARIMA model.
#         forecast_horizon (DatetimeIndex): A series of dates.
#         exogenous (DataFrame): Am optional DataFrame of exogenous variables.
#     Returns:
#         forecast (Series): The forecast series with forecast horizon index.
#         conf (Array): A 2xN array of lower and upper confidence bounds.
#     """
#     periods = len(forecast_horizon)
#     forecast, conf = model.predict(
#         n_periods=periods,
#         return_conf_int=True,
#         X=exogenous,
#     )
#     forecast = Series(forecast)
#     forecast.index = forecast_horizon
#     return forecast, conf


def format_billions(value: float, pos: Optional[int] = None) -> str: #pylint: disable=unused-argument
    """The two args are the value and tick position."""
    return '%1.1fB' % (value * 1e-9)


def format_millions(value: float, pos: Optional[int] = None) -> str: #pylint: disable=unused-argument
    """The two args are the value and tick position."""
    return '%1.1fM' % (value * 1e-6)


def format_thousands(value: float, pos: Optional[int] = None) -> str: #pylint: disable=unused-argument
    """The two args are the value and tick position."""
    return '%1.0fK' % (value * 1e-3)


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


def reverse_dataframe(data: DataFrame) -> DataFrame:
    """Reverse the ordering of a DataFrame.
    Args:
        data (DataFrame): A DataFrame to re-order.
    Returns:
        (DataFrame): The re-ordered DataFrame.
    """
    return data[::-1].reset_index(drop=True)


def set_training_period(series: Series, date_start: str, date_end: str) -> Series:
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


def sorted_nicely(unsorted_list: List[str]) -> List[str]:
    """Sort the given iterable in the way that humans expect.
    Credit: Mark Byers <https://stackoverflow.com/a/2669120/5021266>
    License: CC BY-SA 2.5 <https://creativecommons.org/licenses/by-sa/2.5/>
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alpha = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(unsorted_list, key=alpha)


def rmerge(left, right, **kwargs):
    """Perform a merge using pandas with optional removal of overlapping
    column names not associated with the join.

    Though I suspect this does not adhere to the spirit of pandas merge 
    command, I find it useful because re-executing IPython notebook cells 
    containing a merge command does not result in the replacement of existing
    columns if the name of the resulting DataFrame is the same as one of the
    two merged DataFrames, i.e. data = pa.merge(data,new_dataframe). I prefer
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
        skipcols = set(flatten([v for k, v in myargs.items() if k in ['on', 'left_on', 'right_on']]))
        leftcols = set(left.columns)
        rightcols = set(right.columns)
        dropcols = list((leftcols & rightcols).difference(skipcols))

        # Remove the overlapping column names from the appropriate DataFrame
        if myargs['replace'].lower() == 'left':
            left = left.copy().drop(dropcols, axis=1)
        elif myargs['replace'].lower() == 'right':
            right = right.copy().drop(dropcols, axis=1)

    return pd.merge(left, right, **kwargs)
