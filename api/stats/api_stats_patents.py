"""
Patent Stats Views | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/1/2021
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with cannabis patent statistics.
"""
# Standard imports.
from datetime import datetime
from json import loads

# External imports.
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
import ulid

# Internal imports.
from cannlytics.firebase import (
    update_documents,
)
from cannlytics.stats.stats import (
    get_stats_model,
    predict_stats_model,
)


@api_view(['GET', 'POST'])
def patent_stats(request, format=None):
    """Get, create, or update statistics about cannabis plant patents."""
    data = []
    if request.method == 'GET':

        # TODO: Return statistics about patents or a specific patent.
        raise NotImplementedError

    elif request.method == 'POST':

        # TODO: Predict if a given set of lab results would be a good
        # candidate for a patent.

        

        raise NotImplementedError
