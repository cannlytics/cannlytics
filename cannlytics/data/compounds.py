"""
Compounds (alias) | Cannlytics
Copyright (c) 2024-2026 Cannlytics

Description:
    The compound reference tables now live in ``cannlytics.constants.compounds``.
    This module keeps the old import path working.
"""
from cannlytics.constants.compounds import *  # noqa: F401,F403
from cannlytics.constants.compounds import (  # noqa: F401
    COMPOUNDS,
    cannabinoids,
    foreign_matter,
    heavy_metals,
    microbes,
    mycotoxins,
    pesticides,
    residual_solvents,
    terpenes,
)
