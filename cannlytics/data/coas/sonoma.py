"""
Parse Sonoma Lab Works CoAs
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 8/2/2022
Updated: 8/2/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse an Sonoma Lab Works CoA.

Data Points:

Static Data Points:

"""
# Standard imports.
from ast import literal_eval
import re
from typing import Any

# External imports.
import pandas as pd
import pdfplumber

# Internal imports.
from cannlytics.data.data import create_sample_id
from cannlytics.utils.utils import (
    snake_case,
    split_list,
    strip_whitespace,
)

# It is assumed that the lab has the following details.
SONOMA =  {
    'coa_algorithm': 'sonoma.py',
    'coa_algorithm_entry_point': 'parse_sonoma_coa',
    'lims': 'Sonoma Lab Works',
    'lab': 'Sonoma Lab Works',
    'lab_website': '',
}
