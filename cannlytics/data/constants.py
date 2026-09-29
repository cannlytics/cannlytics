"""
Constants (deprecated location) | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 9/16/2021
Updated: 9/28/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Deprecated: import from ``cannlytics.constants``. This module
    re-exports it, so that ``from cannlytics.data.constants import X``
    keeps working through 1.x; it will be removed in 2.0.

    Retired in 1.0.5, when nothing in the package, the dataset
    repositories, or the website used them:

    - ``ANALYSES`` and ``ANALYTES``, label maps: every label they held
      resolves through ``normalize_analysis_name`` and
      ``normalize_analyte_key``, some to a corrected answer (their
      p-mentha-1,5-diene was myrcene; their spinosad, spinosyn A).
    - ``STANDARD_FIELDS``, the retired first parser's field map, which
      had errors of its own (``Labeled Amount`` as the sample weight).
    - ``STRAINS``, fourteen merges that dropped phenotypes
      (``Cannatonic #4`` as ``Cannatonic``); strain IDs follow the slug
      rule of ``cannlytics.utils.kebab_case``.

    ``PRODUCT_TYPES`` is ``METRC_PRODUCT_TYPES``; ``state_names`` and
    ``state_time_zones`` keep their 0.x meanings.
"""
# Standard imports:
import warnings

# Internal imports:
from cannlytics.constants import *  # noqa: F401,F403
from cannlytics.constants import METRC_PRODUCT_TYPES as PRODUCT_TYPES  # noqa: F401
# The 0.x dict (on cannlytics.constants, `states` is the submodule).
from cannlytics.constants.states import US_STATES as states  # noqa: F401
from cannlytics.constants.states import JURISDICTIONS as _JURISDICTIONS
from cannlytics.constants.states import TIME_ZONES as state_time_zones  # noqa: F401

# A 0.x name, kept through 1.x: jurisdiction name to code.
state_names = {name: code for code, name in _JURISDICTIONS.items()}

warnings.warn(
    'cannlytics.data.constants is deprecated and will be removed in 2.0; '
    'import from cannlytics.constants.',
    DeprecationWarning,
    stacklevel=2,
)
