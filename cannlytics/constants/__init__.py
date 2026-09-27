"""
Cannlytics Constants | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The tables every part of the Cannlytics ecosystem shares, in one
    place: jurisdictions, analyses, analytes, product types, the license
    taxonomy, units, and the compound reference. Everything here imports
    only the standard library, so any module can depend on it without a
    cycle or an optional extra.

        from cannlytics.constants import (
            normalize_analyte_key, normalize_analysis_name,
            normalize_product_type, state_code, state_slug, DECARB,
        )
"""
from .analyses import (
    ANALYSIS_ALIASES,
    STANDARD_ANALYSES,
    STANDARD_ANALYSIS_KEYS,
    normalize_analysis_name,
)
from .analytes import (
    ALL_ANALYTE_KEYS,
    ANALYTE_ALIASES,
    ANALYTE_FAMILIES,
    ANALYTE_KEYS,
    ANALYTE_NAMES,
    ANALYTE_TO_ANALYSIS,
    CANNABINOIDS,
    FOREIGN_MATTER,
    HEAVY_METALS,
    MICROBES,
    MOISTURE,
    MYCOTOXINS,
    PESTICIDES,
    RESIDUAL_SOLVENTS,
    TERPENES,
    analysis_for_analyte,
    normalize_analyte_key,
    snake_case_analyte,
)
from .compounds import cannabinoids, heavy_metals, pesticides, terpenes
from .licenses import (
    ACTIVE_STATUSES,
    LICENSE_CATEGORIES,
    LICENSE_STATUSES,
    LICENSE_TYPE_KEYWORDS,
    LICENSE_TYPE_PRIORITY,
    PLACEHOLDER_VALUES,
    LicenseCategory,
)
from .products import (
    FLOWER_PRODUCT_TYPES,
    METRC_PRODUCT_TYPES,
    PRODUCT_TYPES,
    STANDARD_PRODUCT_TYPES,
    is_flower_product,
    normalize_product_type,
)
from .states import (
    CANADIAN_PROVINCES,
    JURISDICTIONS,
    STATE_SLUGS,
    TIME_ZONES,
    US_STATES,
    US_TERRITORIES,
    VALID_CANADIAN_PROVINCES,
    VALID_JURISDICTIONS,
    VALID_US_JURISDICTIONS,
    VALID_US_STATES,
    is_canadian_province,
    is_us_state,
    slugify_name,
    state_code,
    state_name,
    state_slug,
    state_time_zone,
)
from .units import (
    CODINGS,
    DECARB,
    PERCENT_UNITS,
    STANDARD_UNITS,
    TO_PERCENT,
    to_percent,
)

# A browser-like User-Agent for the few public sources that refuse the
# default `requests` one.
DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    ),
}

# Characters used by `cannlytics.utils.get_random_string`.
RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

__all__ = [
    'ACTIVE_STATUSES', 'ALL_ANALYTE_KEYS', 'ANALYSIS_ALIASES', 'ANALYTE_ALIASES',
    'ANALYTE_FAMILIES', 'ANALYTE_KEYS', 'ANALYTE_NAMES', 'ANALYTE_TO_ANALYSIS',
    'CANADIAN_PROVINCES', 'CANNABINOIDS', 'CODINGS', 'DECARB', 'DEFAULT_HEADERS',
    'FLOWER_PRODUCT_TYPES', 'FOREIGN_MATTER', 'HEAVY_METALS', 'JURISDICTIONS',
    'LICENSE_CATEGORIES', 'LICENSE_STATUSES', 'LICENSE_TYPE_KEYWORDS',
    'LICENSE_TYPE_PRIORITY', 'METRC_PRODUCT_TYPES', 'MICROBES', 'MOISTURE',
    'MYCOTOXINS', 'PERCENT_UNITS', 'PESTICIDES', 'PLACEHOLDER_VALUES',
    'PRODUCT_TYPES', 'RANDOM_STRING_CHARS', 'RESIDUAL_SOLVENTS',
    'STANDARD_ANALYSES', 'STANDARD_ANALYSIS_KEYS', 'STANDARD_PRODUCT_TYPES',
    'STANDARD_UNITS', 'STATE_SLUGS', 'TERPENES', 'TIME_ZONES', 'TO_PERCENT',
    'US_STATES', 'US_TERRITORIES', 'VALID_CANADIAN_PROVINCES', 'VALID_JURISDICTIONS',
    'VALID_US_JURISDICTIONS', 'VALID_US_STATES', 'LicenseCategory',
    'analysis_for_analyte', 'cannabinoids', 'heavy_metals', 'is_canadian_province',
    'is_flower_product', 'is_us_state', 'normalize_analysis_name',
    'normalize_analyte_key', 'normalize_product_type', 'pesticides',
    'slugify_name', 'snake_case_analyte', 'state_code', 'state_name',
    'state_slug', 'state_time_zone', 'terpenes', 'to_percent',
]
