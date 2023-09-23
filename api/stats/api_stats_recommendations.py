"""
Recommendation Stats Views | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/1/2021
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with cannabis patent statistics.

References:

- https://github.com/TracyRenee61/House-Prices/blob/master/Boston_Housing_SelectKBest_.ipynb

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


#---------------------------------------------------------------
# TODO: User requests recommendations given a
# list of desired effects and aromas.
# A list of strains is returned that match the desired
# effects and aromas ranked by the number of matched effects.
# Future work: Return statistics for the probability of reporting
# effects and aromas.
# Optional: Let user pass aromas=false to get only effects and
# pass effects=false to get only aromas.
#---------------------------------------------------------------


@api_view(['GET', 'POST'])
def recommendation_stats(request, format=None):
    """Get, create, or update statistics about strain or product recommendations."""
    data = []
    if request.method == 'GET':


        # TODO: User passes list of desired effects / aromas.
        # A list of strains is returned that match the desired effects / aromas,
        # ranked by the number of matched effects.
        # Optionally: statistics for how well the match is is returned.
        raise NotImplementedError

    elif request.method == 'POST':

        # Optional: User passes link to lab results data and / or reviews
        # data to train their own model.
        # TODO: User posts if the recommendation was useful or not.
        raise NotImplementedError
