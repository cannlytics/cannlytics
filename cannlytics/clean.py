"""
Cleaning Primitives | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/27/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    One behavior for each field-cleaning primitive. Before 1.0.4 the
    state license collectors carried thirteen ``clean_zip_code``
    functions with eight behaviors, ten ``parse_date`` functions with
    nine, and nine ``clean_phone_number`` functions with eight, so the
    published files were formatted differently state by state. These
    are the rules now, and every collector imports them.

    Every function accepts whatever a regulator's export or a pandas
    frame hands it (``None``, ``NaN``, numbers, padded strings) and
    returns ``None`` for anything that carries no value, so that a
    non-value never becomes a stored string such as ``'N/A'``.

        from cannlytics.clean import parse_date, clean_zip_code, clean_phone_number

        parse_date('1/5/24')            # '2024-01-05'
        parse_date(45306)               # '2024-01-15' (an Excel serial)
        clean_zip_code(2134)            # '02134'
        clean_phone_number('555.123.4567')   # '(555) 123-4567'

    Needs only the standard library and ``python-dateutil``.
"""
# Standard imports:
from __future__ import annotations

import calendar
import math
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional, Tuple

# External imports:
from dateutil import parser as _dateparser

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Placeholders                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

# Strings (lower case, stripped) that mean "no value". Deliberately
# absent: '0', '0.0', 'false', 'no'. A zero is a measurement and a
# boolean is a value; treating them as blanks is how non-detects turn
# into zeros and back (the null-versus-zero doctrine).
SENTINELS = frozenset({
    '', 'nan', 'none', 'null', 'nat', '<na>', 'n/a', 'n.a.', 'na', 'n a',
    '-', '--', '---', '.', '?', 'not available', 'not published',
    'not disclosed', 'not provided', 'not applicable', 'not listed',
    'unknown', 'unavailable', 'undefined', 'tbd', 'to be determined',
    'missing', 'no data', 'none listed', 'none provided', 'confidential',
    'exempt from public disclosure', 'redacted', '#n/a', '#ref!', '#value!',
    '#name?', '#div/0!', 'inf', '-inf', 'nil',
})

def is_placeholder(value: Any) -> bool:
    """Whether a value stands for "no value".

    ``None``, ``NaN`` (float or pandas), and any string in ``SENTINELS``
    are placeholders. Zero, ``False``, and every other number are not.

    Args:
        value: Anything from a regulator's export or a data frame.

    Returns:
        ``True`` if the value carries no information.
    """
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str):
        return value.strip().lower() in SENTINELS
    if type(value).__name__ in ('NAType', 'NaTType'):   # pandas.NA, pandas.NaT
        return True
    try:
        # numpy.nan and datetime.NaT are not equal to themselves.
        return bool(value != value)
    except (TypeError, ValueError):
        return False

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Text                                                             ║
# ╚══════════════════════════════════════════════════════════════════╝

_WHITESPACE = re.compile(r'\s+')
_CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

def normalize_whitespace(text: str) -> str:
    """Collapse every run of whitespace, including non-breaking, to one space."""
    return _WHITESPACE.sub(' ', str(text).replace('\u00a0', ' ')).strip()

def clean_text(value: Any) -> Optional[str]:
    """Return a value as clean text, or ``None`` if it carries no value.

    Unicode is normalized to NFKC (so full-width and ligature forms
    compare equal), control characters are dropped, quotes around the
    whole value are stripped, and whitespace is collapsed.

    Args:
        value: Anything.

    Returns:
        The cleaned string, or ``None`` for a placeholder.
    """
    if is_placeholder(value):
        return None
    text = unicodedata.normalize('NFKC', str(value))
    text = _CONTROL.sub('', text)
    text = normalize_whitespace(text)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in '"\'':
        text = text[1:-1].strip()
    return text if text and text.lower() not in SENTINELS else None

# Words kept lower case inside a name (never at the start).
_SMALL_WORDS = frozenset({'a', 'an', 'and', 'at', 'by', 'de', 'del', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'y'})

# Tokens kept upper case wherever they appear: legal forms, compass
# points, cannabis abbreviations, Roman numerals, and the state codes
# that are not also English words (so 'OR', 'IN', 'ME', 'OK', 'HI',
# 'OH', 'LA', 'MA', 'PA', 'CO', 'DE', 'ID', and 'MO' are not here).
_ACRONYMS = frozenset({
    'llc', 'llp', 'lp', 'pllc', 'pc', 'plc', 'dba', 'aka', 'ceo',
    'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw',
    'cbd', 'cbg', 'cbn', 'thc', 'thca', 'thcv', 'co2', 'rso', 'mmj', 'mso', 'rx',
    'usa', 'nyc', 'ii', 'iii', 'iv', 'vi', 'vii', 'viii', 'ix',
    'ak', 'al', 'ar', 'az', 'ca', 'ct', 'dc', 'fl', 'ga', 'ia', 'il', 'ks', 'ky',
    'md', 'mi', 'mn', 'ms', 'mt', 'nc', 'nd', 'nh', 'nj', 'nm', 'nv', 'ny', 'ri',
    'sc', 'sd', 'tn', 'tx', 'ut', 'va', 'vt', 'wa', 'wi', 'wv', 'wy',
})

_EDGE_PUNCTUATION = re.compile(r'^([^\w]*)(.*?)([^\w]*)$', re.S)

def _title_core(core: str, first: bool) -> str:
    """Case one word with no leading or trailing punctuation."""
    lower = core.lower()
    if lower.replace('.', '') in _ACRONYMS:
        return core.upper()
    if lower in _SMALL_WORDS and not first:
        return lower
    for separator in ('-', '&', '/'):
        if separator in core:
            return separator.join(_title_core(part, True) for part in core.split(separator))
    if "'" in core and len(core) > 2:
        head, _, tail = core.partition("'")
        if len(head) == 1:                       # O'Malley, D'Angelo
            return head.upper() + "'" + tail[:1].upper() + tail[1:].lower()
        return head[:1].upper() + head[1:].lower() + "'" + tail.lower()   # Don't, Mary's
    if lower.startswith('mc') and len(core) > 3 and core[2:].isalpha():
        return 'Mc' + core[2:3].upper() + core[3:].lower()
    return core[:1].upper() + core[1:].lower()

def _title_word(word: str, first: bool) -> str:
    lead, core, trail = _EDGE_PUNCTUATION.match(word).groups()
    return lead + (_title_core(core, first) if core else '') + trail

def smart_title_case(value: Any) -> Optional[str]:
    """Title-case a business or product name without mangling it.

    Legal forms, compass points, and cannabis abbreviations stay upper
    case (``LLC``, ``NW``, ``CBD``), small words stay lower inside the
    name, apostrophes, ``Mc`` names, and ``A&B`` are handled, a digit
    does not start a capital (``3rd``, where ``str.title`` gives
    ``3Rd``), and an already mixed-case name is left alone: the source
    knew what it meant.

        smart_title_case('GREEN THUMB INDUSTRIES LLC')   # 'Green Thumb Industries LLC'
        smart_title_case("o'malley's dispensary")        # "O'Malley's Dispensary"
        smart_title_case('123 MAIN ST NW, SUITE 3RD')    # '123 Main St NW, Suite 3rd'
        smart_title_case('Curaleaf NY, LLC')             # 'Curaleaf NY, LLC' (unchanged)

    Args:
        value: The raw name.

    Returns:
        The cased name, or ``None`` for a placeholder.
    """
    text = clean_text(value)
    if text is None:
        return None
    if text != text.upper() and text != text.lower():
        return text  # Already mixed case: the source knew what it meant.
    words = text.split(' ')
    return ' '.join(_title_word(word, index == 0) for index, word in enumerate(words))

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Numbers                                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

_NON_DETECT = frozenset({'nd', 'n.d.', 'not detected', 'none detected', 'bdl', 'blq', 'bql', 'nt', 'not tested', 'pass', 'fail'})

def safe_float(value: Any) -> Optional[float]:
    """Return a number as a float, or ``None`` when it is not one.

    Strings may carry thousands separators, a currency sign, or a
    percent sign. A bound (``'< 0.05'``, ``'>100'``) is not a
    measurement and returns ``None``, as do booleans, placeholders, and
    laboratory codes such as ``ND``: never zero.

    Args:
        value: Anything.

    Returns:
        A float, or ``None``.
    """
    if isinstance(value, bool) or is_placeholder(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if text in _NON_DETECT:
        return None
    if text[:1] in '<>≤≥':
        return None
    text = text.replace(',', '').replace('%', '').replace('$', '').strip()
    try:
        number = float(text)
    except ValueError:
        return None
    return None if math.isnan(number) or math.isinf(number) else number

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Dates                                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

_EXCEL_EPOCH = datetime(1899, 12, 30)
_MIN_YEAR, _MAX_YEAR = 1900, 2100
_MAX_UNIX_SECONDS = 4_102_444_800        # 2100-01-01; Windows rejects years past 3000

# dateutil fills a missing year, month, or day from its `default`, which
# is today: 'January 2024' would parse as the 26th on the 26th. Parsing
# twice with two different defaults exposes what was missing, so a
# partial date is recognized as partial instead of being completed with
# today's date.
_DEFAULT_A = datetime(1901, 2, 3)
_DEFAULT_B = datetime(1902, 4, 5)
_ISO_DATE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})(?:[T ].*)?$')
_COMPACT_DATE = re.compile(r'^(\d{4})(\d{2})(\d{2})$')

# Partial dates written without words: '2024-01', '01/2024', '2024/1', '2024'.
_ISO_MONTH = re.compile(r'^(\d{4})[-/.](\d{1,2})$')
_MONTH_YEAR = re.compile(r'^(\d{1,2})[-/.](\d{4})$')
_YEAR = re.compile(r'^(\d{4})$')

# What to do with a date that has no day (or no month and day):
#   'keep'  return it at the precision given: '2024-01', '2024' (lossless)
#   'start' complete it to the first day of the period: '2024-01-01'
#   'end'   complete it to the last day of the period: '2024-01-31'
#   None    return None
# Conventions: an expiration or "valid through" date stated as a month and
# year runs through the month's last day (the pharmaceutical labelling
# convention), so use 'end'; an issue, effective, or start date begins on
# the first, so use 'start'; a testing, collection, or receipt date should
# not be completed at all, so keep it and record its precision.
PARTIAL_DATE_POLICIES = ('keep', 'start', 'end', None)

def _plausible(moment: datetime) -> Optional[datetime]:
    return moment if _MIN_YEAR <= moment.year <= _MAX_YEAR else None

def _check_policy(partial: Optional[str], allow_keep: bool = True) -> None:
    allowed = PARTIAL_DATE_POLICIES if allow_keep else ('start', 'end', None)
    if partial not in allowed:
        raise ValueError(f'partial must be one of {allowed}, not {partial!r}.')

def _read_date(value: Any, dayfirst: bool = False) -> Optional[Tuple[datetime, str]]:
    """Read a value into ``(moment, precision)``; precision is 'day', 'month', or 'year'.

    A partial date's missing parts are 1 in ``moment``; ``precision``
    says which parts were given.
    """
    if isinstance(value, bool) or is_placeholder(value):
        return None
    if isinstance(value, (datetime, date, int, float)):
        moment = _read_complete(value)
        return (moment, 'day') if moment else None
    text = normalize_whitespace(str(value))
    for pattern, year_group, month_group in ((_ISO_MONTH, 1, 2), (_MONTH_YEAR, 2, 1)):
        match = pattern.match(text)
        if match:
            year, month = int(match.group(year_group)), int(match.group(month_group))
            if not 1 <= month <= 12 or not _MIN_YEAR <= year <= _MAX_YEAR:
                return None
            return datetime(year, month, 1), 'month'
    match = _YEAR.match(text)
    if match:
        year = int(match.group(1))
        return (datetime(year, 1, 1), 'year') if _MIN_YEAR <= year <= _MAX_YEAR else None
    moment = _read_complete(text, dayfirst)
    if moment is not None:
        return moment, 'day'
    if not text or re.fullmatch(r'\d+(\.\d+)?', text):
        return None
    try:
        first = _dateparser.parse(text, dayfirst=dayfirst, default=_DEFAULT_A)
        second = _dateparser.parse(text, dayfirst=dayfirst, default=_DEFAULT_B)
    except (ValueError, OverflowError, TypeError):
        return None
    if first.year != second.year or not _MIN_YEAR <= first.year <= _MAX_YEAR:
        return None                          # no (plausible) year: it cannot be placed
    if first.month != second.month:
        return datetime(first.year, 1, 1), 'year'
    return datetime(first.year, first.month, 1), 'month'

def _complete(moment: datetime, precision: str, partial: Optional[str]) -> Optional[datetime]:
    """Complete a partial date by the policy, or ``None`` to decline."""
    if precision == 'day' or partial == 'start':
        return moment
    if partial == 'end':
        month = 12 if precision == 'year' else moment.month
        return datetime(moment.year, month, calendar.monthrange(moment.year, month)[1])
    return None

def date_precision(value: Any, dayfirst: bool = False) -> Optional[str]:
    """How precisely a value states a date: ``'day'``, ``'month'``, ``'year'``, or ``None``.

    Record it beside a date column when some rows are partial, so that
    no reader mistakes a completed date for an observed one.
    """
    found = _read_date(value, dayfirst)
    return found[1] if found else None

def parse_datetime(value: Any, dayfirst: bool = False, partial: Optional[str] = None) -> Optional[datetime]:
    """Read a date or timestamp of any common form into a ``datetime``.

    Accepts ``date``/``datetime`` objects (pandas timestamps included),
    ISO strings, ``YYYYMMDD``, US ``M/D/YYYY`` and ``M/D/YY``, written
    months (``January 15, 2024``, ``Jan 15 2024``), Excel serial numbers
    (``45306``), and Unix timestamps in seconds or milliseconds. An
    impossible date (``2024-13-45``), a date with no year, a
    placeholder, or a year outside 1900--2100 returns ``None`` rather
    than a wrong date. Nothing depends on today's date, so a re-run
    gives the same answer.

    Args:
        value: The raw value.
        dayfirst: Read ``05/01/2024`` as 5 January (European) rather
            than 1 May.
        partial: How to treat a date without a day (``'March 2026'``):
            the ``'start'`` or ``'end'`` of the period, or ``None`` (the
            default) to return ``None``. A ``datetime`` cannot hold a
            partial date, so ``'keep'`` is for ``parse_date`` only.

    Returns:
        A naive ``datetime``, or ``None``.
    """
    _check_policy(partial, allow_keep=False)
    found = _read_date(value, dayfirst)
    return _complete(*found, partial) if found else None

def _read_complete(value: Any, dayfirst: bool = False) -> Optional[datetime]:
    """Read a value that states a full date; ``None`` for anything else."""
    if isinstance(value, datetime):
        return _plausible(value.replace(tzinfo=None) if value.tzinfo else value)
    if isinstance(value, date):
        return _plausible(datetime(value.year, value.month, value.day))
    if isinstance(value, (int, float)):
        number = float(value)
        if 20_000 <= number <= 80_000:            # Excel serial (1954--2119)
            return _plausible(_EXCEL_EPOCH + timedelta(days=number))
        if 19_000_101 <= number <= 21_001_231 and float(number).is_integer():   # YYYYMMDD
            return _read_complete(str(int(number)))
        if 1e11 <= number < 1e13:                # Unix milliseconds
            number /= 1000
        if 1e8 <= number < _MAX_UNIX_SECONDS:    # Unix seconds
            try:
                return _plausible(datetime.fromtimestamp(number, timezone.utc).replace(tzinfo=None))
            except (OverflowError, OSError, ValueError):
                return None
        return None
    text = normalize_whitespace(str(value))
    if not text:
        return None
    match = _ISO_DATE.match(text) or _COMPACT_DATE.match(text)
    if match:
        try:
            moment = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
        if _ISO_DATE.match(text) and ('T' in text or ' ' in text):
            try:
                moment = _dateparser.isoparse(text.replace(' ', 'T', 1))
                moment = moment.replace(tzinfo=None) if moment.tzinfo else moment
            except ValueError:
                pass
        return _plausible(moment)
    if re.fullmatch(r'\d+(\.\d+)?', text):
        return _read_complete(float(text))
    try:
        first = _dateparser.parse(text, dayfirst=dayfirst, default=_DEFAULT_A)
        second = _dateparser.parse(text, dayfirst=dayfirst, default=_DEFAULT_B)
    except (ValueError, OverflowError, TypeError):
        return None
    if (first.year, first.month, first.day) != (second.year, second.month, second.day):
        return None   # partial: `_read_date` classifies it
    return _plausible(first.replace(tzinfo=None) if first.tzinfo else first)

def parse_date(value: Any, dayfirst: bool = False, partial: Optional[str] = 'keep') -> Optional[str]:
    """Read any common date form into an ISO 8601 date string.

    See ``parse_datetime`` for what is accepted. A full date is
    ``'YYYY-MM-DD'``. A partial one is, by default, kept at the precision
    it was given, ``'2024-01'`` or ``'2024'`` (also ISO 8601), so that
    nothing is discarded and no day is invented; ``date_precision`` tells
    them apart. Load mixed precision with pandas using
    ``pd.to_datetime(column, format='ISO8601')``.

    Args:
        value: The raw value.
        dayfirst: Read ``05/01/2024`` as 5 January.
        partial: ``'keep'`` (the default), the ``'start'`` or ``'end'`` of
            the period, or ``None``. Use ``'end'`` for expiration dates
            (a month-and-year expiration runs through the month's last
            day) and ``'start'`` for issue or effective dates.

    Returns:
        An ISO date string, or ``None``.
    """
    _check_policy(partial)
    found = _read_date(value, dayfirst)
    if found is None:
        return None
    moment, precision = found
    if precision != 'day' and partial == 'keep':
        return moment.strftime('%Y-%m' if precision == 'month' else '%Y')
    completed = _complete(moment, precision, partial)
    return completed.strftime('%Y-%m-%d') if completed else None

def parse_timestamp(value: Any, dayfirst: bool = False, partial: Optional[str] = None) -> Optional[str]:
    """Read any common date or time form into ISO ``YYYY-MM-DDTHH:MM:SS``.

    ``partial`` is as for ``parse_datetime``.
    """
    moment = parse_datetime(value, dayfirst=dayfirst, partial=partial)
    return moment.strftime('%Y-%m-%dT%H:%M:%S') if moment else None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Contact fields                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

_CANADIAN_POSTAL = re.compile(r'^([A-Z]\d[A-Z])\s*(\d[A-Z]\d)$')
_ZIP = re.compile(r'^(\d{3,5})(?:\.0+)?$')                   # '2134', '2134.0' (a float column)
_ZIP_PLUS4 = re.compile(r'^(\d{5})[\s-]?(\d{4})$')
_TRAILING_ZIP = re.compile(r'\b[A-Z]{2}\s+(\d{5})(?:-(\d{4}))?$')   # 'Olympia, WA 98501'

def clean_zip_code(value: Any, plus4: bool = False) -> Optional[str]:
    """Return a US ZIP code (or Canadian postal code) in one form.

    A US code is five digits with leading zeros restored (``2134`` from
    a spreadsheet that dropped the zero is ``'02134'``; three or four
    digits are restored, one or two are not a ZIP code); the +4 is
    dropped unless ``plus4`` is set. A field holding a whole
    ``'City, ST 98501'`` gives its ZIP. A Canadian code is
    ``'A1A 1A1'``. Anything else, including ``'PO Box 100'`` and
    ``'N/A'``, is ``None``: digits are never scraped out of text.

    Args:
        value: The raw code: a string, or a number from a data frame.
        plus4: Keep the ZIP+4 suffix when present.

    Returns:
        The code, or ``None``.
    """
    if isinstance(value, bool) or is_placeholder(value):
        return None
    if isinstance(value, (int, float)):
        if not float(value).is_integer() or not 0 < value < 1_000_000_000:
            return None
        value = str(int(value))
    text = normalize_whitespace(str(value)).upper()
    canadian = _CANADIAN_POSTAL.match(text.replace('-', ''))
    if canadian:
        return f'{canadian.group(1)} {canadian.group(2)}'
    match = _ZIP.match(text)
    if match:
        return match.group(1).zfill(5)
    match = _ZIP_PLUS4.match(text) or _TRAILING_ZIP.search(text)
    if match:
        zip5, four = match.group(1), match.group(2)
        return f'{zip5}-{four}' if plus4 and four else zip5
    return None

def clean_phone_number(value: Any) -> Optional[str]:
    """Return a North American phone number as ``(555) 123-4567``.

    A leading country code ``1`` is dropped, an extension is kept as
    ``ext. 12``, and anything without exactly ten digits is ``None``.

    Args:
        value: The raw number: a string, or a number from a data frame.

    Returns:
        The formatted number, or ``None``.
    """
    if isinstance(value, bool) or is_placeholder(value):
        return None
    text = str(int(value)) if isinstance(value, (int, float)) and float(value).is_integer() else str(value)
    text = text.lower()
    extension = None
    match = re.search(r'(?:ext\.?|extension|x)\s*(\d{1,6})\s*$', text)
    if match:
        extension = match.group(1)
        text = text[:match.start()]
    digits = re.sub(r'\D', '', text)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) != 10:
        return None
    number = f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
    return f'{number} ext. {extension}' if extension else number

_EMAIL = re.compile(r'^[a-z0-9._%+\-\']+@[a-z0-9.\-]+\.[a-z]{2,}$')

def clean_email(value: Any) -> Optional[str]:
    """Return one lower-case e-mail address, or ``None``.

    ``mailto:`` is stripped, a trailing note in parentheses dropped, and
    when several addresses are listed the first is kept.

    Args:
        value: The raw value.

    Returns:
        The address, or ``None`` if none is valid.
    """
    text = clean_text(value)
    if text is None:
        return None
    text = re.sub(r'\(.*?\)', ' ', text.lower().replace('mailto:', ''))
    for candidate in re.split(r'[;,\s]+', text):
        if _EMAIL.match(candidate):
            return candidate
    return None

def clean_url(value: Any) -> Optional[str]:
    """Return a web address with a scheme and a lower-case host, or ``None``."""
    text = clean_text(value)
    if text is None:
        return None
    text = text.split()[0].rstrip('.,;)')
    if not re.match(r'^[a-z][a-z0-9+.-]*://', text, re.I):
        if not re.match(r'^[\w.-]+\.[a-z]{2,}(?:[/?#:]|$)', text, re.I):
            return None
        text = 'https://' + text
    match = re.match(r'^([a-z][a-z0-9+.-]*://)([^/?#]+)(.*)$', text, re.I)
    if not match:
        return None
    scheme, host, rest = match.groups()
    if scheme.lower() not in ('http://', 'https://'):
        return None
    return scheme.lower() + host.lower() + (rest if rest and rest != '/' else '')

__all__ = [
    'PARTIAL_DATE_POLICIES', 'SENTINELS', 'clean_email', 'clean_phone_number',
    'clean_text', 'clean_url', 'clean_zip_code', 'date_precision', 'is_placeholder',
    'normalize_whitespace', 'parse_date', 'parse_datetime', 'parse_timestamp',
    'safe_float', 'smart_title_case',
]
