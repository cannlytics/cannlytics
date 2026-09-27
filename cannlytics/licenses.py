"""
Licenses | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The license-number rules that ``cannabis_licenses`` and
    ``cannabis_results`` share, so that the two products can be joined.
    Before 1.0.4 the number was normalized four ways and the two that
    reached published files disagreed on every California number
    (``C10-0000123`` on one side, ``C10-123`` on the other).

    Two things, kept apart:

    - The **identifier** is what the regulator issued. It is stored
      verbatim apart from case, whitespace, and quotes, and it is what
      ``license_number`` holds in every product: ``C10-0000936-LIC``.
      ``normalize_license_number`` produces it.
    - The **key** is derived from the identifier for *matching only*:
      prefixes such as ``LIC#`` and the ``-LIC`` suffix dropped,
      separators and leading zeros removed, upper case. It is never
      stored as the identifier. ``license_key`` produces it, and both
      sides of a join compute it from the same function.

        from cannlytics.licenses import normalize_license_number, license_key

        normalize_license_number('  c10-0000936-lic ')   # 'C10-0000936-LIC'
        license_key('C10-0000936-LIC')                   # 'C10-936'
        license_key('Lic# C10 0000936')                  # 'C10-936'

    Merging is a cascade, most faithful first: the identifier, then the
    key, then the compact key (``license_key(value, compact=True)``,
    separators removed and zeros kept, so ``MMTC-2015-0001`` meets
    ``MMTC20150001``). ``license_match_level`` says which level joined
    two numbers; store it with a merge so the join can be audited.
    A match never rewrites either identifier.

    Needs only the standard library.
"""
# Standard imports:
from __future__ import annotations

import re
from typing import Any, List, Optional

# Internal imports:
from cannlytics.clean import clean_text, normalize_whitespace
from cannlytics.constants.licenses import (
    ACTIVE_STATUSES,
    LICENSE_STATUSES,
    LICENSE_TYPE_KEYWORDS,
    LicenseCategory,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ The identifier                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

# Separators between several license numbers in one field.
_COMPOUND_SPLIT = re.compile(r'\s*(?:[;,/|]|\band\b|&|\n)\s*', re.IGNORECASE)

def normalize_license_number(value: Any) -> Optional[str]:
    """Return a license number as the regulator issued it.

    Only case, surrounding whitespace and quotes, and inner runs of
    whitespace are touched. Prefixes, suffixes, and leading zeros are
    part of the identifier and are kept; see ``license_key`` for
    matching.

    Args:
        value: The raw value.

    Returns:
        The upper-case identifier, or ``None`` for a placeholder. A whole
        number that a spreadsheet stored as a float (``412345.0``) is the
        number the regulator issued (``'412345'``).
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, float) and value == value and value.is_integer():
        value = int(value)
    text = clean_text(value)
    if text is None:
        return None
    return normalize_whitespace(text).upper() or None

def split_license_numbers(value: Any) -> List[str]:
    """Split a field that lists several license numbers.

    ``'C10-0000123-LIC; C11-0000456-LIC'`` gives two identifiers.

    Args:
        value: The raw value.

    Returns:
        The identifiers, in order, without placeholders.
    """
    text = clean_text(value)
    if text is None:
        return []
    numbers = []
    for part in _COMPOUND_SPLIT.split(text):
        number = normalize_license_number(part)
        if number and number not in numbers:
            numbers.append(number)
    return numbers

# ╔══════════════════════════════════════════════════════════════════╗
# ║ The matching key                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

# Labels a source prepends to a number. A label must end where a word
# ends ('DEA' is a label, 'DEAL-123' is a number), and a bare 'NO' or
# 'NUMBER' needs a mark after it ('No. 123', 'No# 123').
_PREFIXES = re.compile(
    r'^(?:'
    r'(?:FL\s+)?(?:LICENSE|LICENCE|LIC|PERMIT|REGISTRATION|REG|DEA|CLIA)(?![A-Z])'
    r'(?:\s*(?:NO\.?|NUMBER|#)(?![A-Z]))?'
    r'|NO\s*[.#:]|NUMBER\s*[#:]'
    r'|#'
    r')\s*[:#\-]?\s*',
    re.IGNORECASE,
)

# Suffixes that carry no identity. The suffix must be separated from the
# number or follow a digit, so 'PUBLIC' keeps its 'LIC'.
_SUFFIXES = re.compile(r'(?:[-\s]+|(?<=\d))(?:LIC|LICENSE)$', re.IGNORECASE)

# Values that are not cannabis license numbers at all, anywhere.
_REJECT = [
    re.compile(r'X{4,}', re.IGNORECASE),                   # masked
    re.compile(r'^10D\d{7}$'),                             # CLIA IDs
    re.compile(r'\b(?:cultivation|retail|dispensary|manufactur|process|distribut|transport|testing|laboratory|microbusiness|vertically|adult[- ]use|medical|license type)\w*', re.IGNORECASE),
]

# Florida identifiers that appear in license fields but are not
# licenses. Applied to Florida only: rejecting a real license elsewhere
# loses a join, while keeping one of these costs nothing (it matches no
# license).
_REJECT_FL = [
    re.compile(r'^[A-Z]{2}\d{5}-\d{2}$'),                  # accreditation IDs (IA15009-04)
    re.compile(r'^MTM-\d{4}$'),
]

def license_key(value: Any, state: Optional[str] = None, compact: bool = False) -> Optional[str]:
    """Derive the key two records are matched on.

    The key is tolerant of the ways one number gets written: labels
    (``LIC#``), the ``-LIC`` suffix, spaces or dots for hyphens, and
    zero-padding (``C10-0000936`` and ``C10-936`` share a key). It is
    for matching only; store ``normalize_license_number`` instead.

    Args:
        value: A license number in any form.
        state: The two-letter jurisdiction, for the few state-specific
            repairs (Florida's ``FL-`` prefix, New York's site suffix).
        compact: Remove separators but keep zeros (``MMTC20150001``):
            the third level of the merge cascade, for sources that drop
            hyphens and spaces.

    Returns:
        The key, or ``None`` when the value is a placeholder or is
        recognizably not a license number.
    """
    number = normalize_license_number(value)
    if number is None:
        return None
    text = _PREFIXES.sub('', number).strip()
    text = _SUFFIXES.sub('', text).strip()
    code = (state or '').upper()
    if code == 'FL':
        text = re.sub(r'^FL[\s\-]+', '', text)
    if code == 'NY':
        text = re.sub(r'^OCM\s*#?\s*', 'OCM-', text)
        text = re.sub(r'-P\d+$', '', text)                 # site or phase suffix
    for pattern in _REJECT + (_REJECT_FL if code == 'FL' else []):
        if pattern.search(text):
            return None
    # Alphanumeric groups only, separators collapsed to one hyphen, and
    # leading zeros dropped from each group ('C10-0000936' is 'C10-936').
    groups = [group for group in re.split(r'[^A-Z0-9]+', text.upper()) if group]
    if not groups:
        return None
    if compact:
        return ''.join(groups)
    return '-'.join(group.lstrip('0') or '0' for group in groups)

def license_match_level(left: Any, right: Any, state: Optional[str] = None) -> Optional[str]:
    """The most faithful level at which two license numbers agree.

    Args:
        left: A license number from one source.
        right: A license number from another.
        state: The jurisdiction of both.

    Returns:
        ``'identifier'`` (the same number as issued), ``'key'`` (the
        same after labels, separators, and zero-padding are set aside),
        ``'compact'`` (the same once every separator is removed), or
        ``None`` (different, or either is missing).
    """
    a, b = normalize_license_number(left), normalize_license_number(right)
    if a is None or b is None:
        return None
    if a == b:
        return 'identifier'
    key_a, key_b = license_key(a, state), license_key(b, state)
    if key_a is not None and key_a == key_b:
        return 'key'
    compact_a, compact_b = license_key(a, state, compact=True), license_key(b, state, compact=True)
    if compact_a is not None and compact_a == compact_b:
        return 'compact'
    return None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Types and statuses                                               ║
# ╚══════════════════════════════════════════════════════════════════╝

def categorize_license_type(license_type: Any) -> str:
    """Fold a jurisdiction's license type into one of the categories.

    The first keyword found decides, in the table's order, so a
    ``'Retail Dispensary and Cultivation'`` is retail (the table lists
    the specific before the general).

    Args:
        license_type: The type as the regulator names it.

    Returns:
        A ``LicenseCategory`` value; ``'Other/Unclassified'`` when no
        keyword matches or the value is a placeholder.
    """
    text = clean_text(license_type)
    if text is None:
        return LicenseCategory.OTHER.value
    lowered = text.lower()
    for keyword, category in LICENSE_TYPE_KEYWORDS.items():
        if keyword in lowered:
            return category
    return LicenseCategory.OTHER.value

_STATUS_KEYWORDS = [
    ('not active', 'inactive'), ('non-active', 'inactive'), ('nonactive', 'inactive'),
    ('revoked', 'revoked'), ('revocation', 'revoked'), ('surrender', 'surrendered'),
    ('cancel', 'cancelled'), ('denied', 'denied'), ('deny', 'denied'),
    ('suspend', 'suspended'), ('expire', 'expired'), ('lapsed', 'expired'),
    ('inactive', 'inactive'), ('closed', 'inactive'), ('terminated', 'inactive'),
    ('provisional', 'provisional'), ('conditional', 'provisional'), ('temporary', 'provisional'),
    ('pending', 'pending'), ('renewal in process', 'pending'), ('in process', 'pending'),
    ('under review', 'pending'), ('applied', 'pending'), ('application', 'pending'),
    ('active', 'active'), ('issued', 'active'), ('approved', 'active'), ('operating', 'active'),
    ('operational', 'active'), ('current', 'active'), ('valid', 'active'), ('open', 'active'),
    ('complete', 'active'), ('licensed', 'active'), ('granted', 'active'), ('good standing', 'active'),
]

def standardize_license_status(status: Any) -> str:
    """Fold a jurisdiction's status wording into a standard status.

    Args:
        status: The status as the regulator names it.

    Returns:
        One of ``LICENSE_STATUSES``; ``'unknown'`` for a placeholder or
        an unrecognized value.
    """
    text = clean_text(status)
    if text is None:
        return 'unknown'
    lowered = text.lower()
    if lowered in LICENSE_STATUSES:
        return lowered
    # The leading word is the status; what follows qualifies it
    # ('Active - Pending Renewal' is active).
    for keyword, standard in _STATUS_KEYWORDS:
        if lowered.startswith(keyword):
            return standard
    for keyword, standard in _STATUS_KEYWORDS:
        if keyword in lowered:
            return standard
    return 'unknown'

def is_active_status(status: Any) -> bool:
    """Whether a status means the license is in force."""
    text = clean_text(status)
    if text is None:
        return False
    lowered = text.lower()
    if lowered in ACTIVE_STATUSES:
        return True
    return standardize_license_status(text) == 'active'

__all__ = [
    'categorize_license_type', 'is_active_status', 'license_key', 'license_match_level',
    'normalize_license_number', 'split_license_numbers', 'standardize_license_status',
]
