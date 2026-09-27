"""
Unit Constants | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Units, conversions, codings, and the decarboxylation factor.

    Standard library only.
"""
# Standard imports:
from typing import Dict, List, Optional

# The molecular-weight ratio that converts an acidic cannabinoid to its
# neutral form: total THC = THC + 0.877 x THCA.
DECARB: float = 0.877

# The unit each analysis is reported in, when standardised.
STANDARD_UNITS: Dict[str, str] = {
    'cannabinoids': 'percent',
    'foreign_matter': 'percent',
    'heavy_metals': 'μg/g',
    'microbes': 'CFU/g',
    'moisture': 'percent',
    'mycotoxins': 'μg/g',
    'pesticides': 'μg/g',
    'terpenes': 'percent',
    'water_activity': 'aW',
}

# Spellings of "percent" seen on certificates and in exports.
PERCENT_UNITS: List[str] = ['%', 'percent', 'percentage', 'pct', 'w/w', '% w/w', '%w/w']

# Multiply a value in the unit by the factor to express it in percent.
TO_PERCENT: Dict[str, float] = {'mg/g': 0.1, 'mg/kg': 0.0001, 'ppm': 0.0001, 'ug/g': 0.0001, 'µg/g': 0.0001, 'μg/g': 0.0001}

# Numeric stand-ins for a laboratory's qualitative codes, used by the
# first parser. A non-detect is *not* a zero: prefer null in new code.
CODINGS: Dict[str, Optional[float]] = {
    'ND': 1e-09,
    'No detection in 1 gram': 1e-09,
    'Negative/1g': 1e-09,
    'PASS': 1e-09,
    'LOD': 1e-08,
    '<LOD': 1e-08,
    '< LOD': 1e-08,
    '<LOQ': 1e-07,
    '< LOQ': 1e-07,
    '<LLoQ': 1e-07,
    '<LLOQ': 1e-07,
    'BLQ': 1e-07,
    '<LLoa': 1e-07,
    '≥ LOD': 10001,
    'NR': None,
    'N/A': None,
    'na': None,
    'NT': None,
}

def to_percent(value: float, unit: Optional[str]) -> Optional[float]:
    """Express a concentration in percent, if the unit is convertible.

    Args:
        value: The reported value.
        unit: The reported unit.

    Returns:
        The value in percent, or ``None`` when the unit is not a
        percentage and not convertible to one (CFU/g, aW, ppb).
    """
    if unit is None:
        return None
    key = str(unit).strip().lower()
    if key in {u.lower() for u in PERCENT_UNITS}:
        return float(value)
    factor = TO_PERCENT.get(key)
    return float(value) * factor if factor is not None else None
