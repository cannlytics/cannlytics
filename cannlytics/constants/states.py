"""
State Constants | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The one table of jurisdictions the ecosystem works in. Before 1.0.4
    ``STATE_NAMES`` existed in four repositories in three conventions
    (upper-case codes, Title Case names, kebab-case directory slugs) and
    no two spelled a key the same way. The convention now:

    - A *code* is the two-letter postal abbreviation, upper case:
      ``'CA'``. Functions accept any case.
    - A *name* is the official English name: ``'California'``,
      ``'District of Columbia'``, ``'Newfoundland and Labrador'``.
    - A *slug* is the name in kebab case, for directories and URLs:
      ``'new-jersey'``, ``'district-of-columbia'``.

        from cannlytics.constants import state_name, state_slug, state_code
        state_name('ca')                  # 'California'
        state_slug('NJ')                  # 'new-jersey'
        state_code('New Jersey')          # 'NJ'
        state_code('new-jersey')          # 'NJ'

    Standard library only.
"""
# Standard imports:
import re
import unicodedata
from typing import Dict, Optional

# The fifty states and the District of Columbia.
US_STATES: Dict[str, str] = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming',
}

# Inhabited territories that license cannabis or may.
US_TERRITORIES: Dict[str, str] = {
    'AS': 'American Samoa',
    'GU': 'Guam',
    'MP': 'Northern Mariana Islands',
    'PR': 'Puerto Rico',
    'VI': 'U.S. Virgin Islands',
}

# Canadian provinces and territories.
CANADIAN_PROVINCES: Dict[str, str] = {
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NS': 'Nova Scotia',
    'NT': 'Northwest Territories',
    'NU': 'Nunavut',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'YT': 'Yukon',
}

# Every jurisdiction, code to name.
JURISDICTIONS: Dict[str, str] = {**US_STATES, **US_TERRITORIES, **CANADIAN_PROVINCES}

# Convenience sets for validation.
VALID_US_STATES = frozenset(US_STATES)
VALID_US_JURISDICTIONS = frozenset(US_STATES) | frozenset(US_TERRITORIES)
VALID_CANADIAN_PROVINCES = frozenset(CANADIAN_PROVINCES)
VALID_JURISDICTIONS = frozenset(JURISDICTIONS)

# IANA time zone of each jurisdiction's capital (states that span two
# zones are given the zone of the capital).
TIME_ZONES: Dict[str, str] = {
    'AK': 'America/Anchorage',
    'AL': 'America/Chicago',
    'AR': 'America/Chicago',
    'AZ': 'America/Phoenix',
    'CA': 'America/Los_Angeles',
    'CO': 'America/Denver',
    'CT': 'America/New_York',
    'DC': 'America/New_York',
    'DE': 'America/New_York',
    'FL': 'America/New_York',
    'GA': 'America/New_York',
    'HI': 'Pacific/Honolulu',
    'IA': 'America/Chicago',
    'ID': 'America/Denver',
    'IL': 'America/Chicago',
    'IN': 'America/Indiana/Indianapolis',
    'KS': 'America/Chicago',
    'KY': 'America/New_York',
    'LA': 'America/Chicago',
    'MA': 'America/New_York',
    'MD': 'America/New_York',
    'ME': 'America/New_York',
    'MI': 'America/New_York',
    'MN': 'America/Chicago',
    'MO': 'America/Chicago',
    'MS': 'America/Chicago',
    'MT': 'America/Denver',
    'NC': 'America/New_York',
    'ND': 'America/North_Dakota/Center',
    'NE': 'America/Chicago',
    'NH': 'America/New_York',
    'NJ': 'America/New_York',
    'NM': 'America/Denver',
    'NV': 'America/Los_Angeles',
    'NY': 'America/New_York',
    'OH': 'America/New_York',
    'OK': 'America/Chicago',
    'OR': 'America/Los_Angeles',
    'PA': 'America/New_York',
    'RI': 'America/New_York',
    'SC': 'America/New_York',
    'SD': 'America/Chicago',
    'TN': 'America/Chicago',
    'TX': 'America/Chicago',
    'UT': 'America/Denver',
    'VA': 'America/New_York',
    'VT': 'America/New_York',
    'WA': 'America/Los_Angeles',
    'WI': 'America/Chicago',
    'WV': 'America/New_York',
    'WY': 'America/Denver',
    'AS': 'Pacific/Pago_Pago',
    'GU': 'Pacific/Guam',
    'MP': 'Pacific/Guam',
    'PR': 'America/Puerto_Rico',
    'VI': 'America/St_Thomas',
    'AB': 'America/Edmonton',
    'BC': 'America/Vancouver',
    'MB': 'America/Winnipeg',
    'NB': 'America/Moncton',
    'NL': 'America/St_Johns',
    'NS': 'America/Halifax',
    'NT': 'America/Yellowknife',
    'NU': 'America/Iqaluit',
    'ON': 'America/Toronto',
    'PE': 'America/Halifax',
    'QC': 'America/Toronto',
    'SK': 'America/Regina',
    'YT': 'America/Whitehorse',
}

def _fold(text: str) -> str:
    """Lower-case, fold accents, and collapse separators to one space."""
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()

def slugify_name(name: str) -> str:
    """Kebab-case a jurisdiction name: ``'New Jersey'`` to ``'new-jersey'``."""
    return _fold(name).replace(' ', '-')

# Name and slug, folded, to code. Built once.
_CODE_BY_NAME: Dict[str, str] = {}
for _code, _name in JURISDICTIONS.items():
    _CODE_BY_NAME[_fold(_name)] = _code
    _CODE_BY_NAME[_fold(_code)] = _code
_CODE_BY_NAME.update({
    'washington dc': 'DC', 'washington d c': 'DC', 'd c': 'DC', 'dc': 'DC',
    'newfoundland': 'NL', 'virgin islands': 'VI', 'us virgin islands': 'VI',
})
del _code, _name

# Slugs, code to slug.
STATE_SLUGS: Dict[str, str] = {code: slugify_name(name) for code, name in JURISDICTIONS.items()}

def state_code(value: Optional[str]) -> Optional[str]:
    """Resolve a code, name, or slug to the upper-case two-letter code.

    Args:
        value: ``'ca'``, ``'CA'``, ``'California'``, ``'california'``,
            or ``'new-jersey'``.

    Returns:
        The code, or ``None`` if the value names no jurisdiction.
    """
    if value is None:
        return None
    return _CODE_BY_NAME.get(_fold(value))

def state_name(value: Optional[str]) -> Optional[str]:
    """The official name of a jurisdiction given by code, name, or slug."""
    code = state_code(value)
    return JURISDICTIONS.get(code) if code else None

def state_slug(value: Optional[str]) -> Optional[str]:
    """The kebab-case slug of a jurisdiction given by code, name, or slug."""
    code = state_code(value)
    return STATE_SLUGS.get(code) if code else None

def state_time_zone(value: Optional[str]) -> Optional[str]:
    """The IANA time zone of a jurisdiction's capital."""
    code = state_code(value)
    return TIME_ZONES.get(code) if code else None

def is_us_state(value: Optional[str]) -> bool:
    """Whether the value names one of the fifty states or DC."""
    return state_code(value) in VALID_US_STATES

def is_canadian_province(value: Optional[str]) -> bool:
    """Whether the value names a Canadian province or territory."""
    return state_code(value) in VALID_CANADIAN_PROVINCES
