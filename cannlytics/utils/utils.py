# -*- coding: utf-8 -*-
"""
cannlytics.traceability..utils.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains general cannabis analytics utility functions.
"""

from datetime import datetime, timedelta


def get_timestamp(past=0, future=0, tz='local'):
    """Get an ISO formatted timestamp.
    Args:
        past (int): Number of minutes in the past to get a timestamp.
        future (int): Number of minutes into the future to get a timestamp.

    # TODO: Set time in timezone of state (e.g. {'state': 'OK'} -> CDT)
    """
    now = datetime.now()
    now += timedelta(minutes=future)
    now -= timedelta(minutes=past)
    if tz is None:
        return now.isoformat()[:19]
    else:
        return now.isoformat()
