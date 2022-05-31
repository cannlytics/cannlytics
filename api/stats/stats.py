"""
Stats Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 5/27/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with laboratory statistics.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def effects_stats(request, format=None):
    """Get, create, or update statistics about reported effects and aromas."""
    data = []
    if request.method == 'GET':

        # TODO: # User requests recommendations given a
        # list of desired effects and aromas.
        # A list of strains is returned that match the desired
        # effects and aromas ranked by the number of matched effects.
        # Future work: Return statistics for the probability of reporting
        # effects and aromas.

        # Optional: Let user pass aromas=false to get only effects and
        # pass effects=false to get only aromas.

    elif request.method == 'POST':

        # TODO: Implement stats_effects endpoint!

        # TODO: User passes lab results.

            # A list of potential effects / aromas are returned.
            # The concentration quantile is also returned.


        # TODO: User posts effects, aromas, and/or lab results that they
        # observed for a strain (feedback / actual).


        # TODO: User passes link to lab results data and / or reviews
        # data to train their own model.


    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET', 'POST'])
def recommendations_stats(request, format=None):
    """Get, create, or update statistics about strain or product recommendations."""
    data = []
    if request.method == 'GET':


    # TODO: User passes list of desired effects / aromas.

        # A list of strains is returned that match the desired effects / aromas,
        # ranked by the number of matched effects.
        # Optionally: statistics for how well the match is is returned.
    

    elif request.method == 'POST':

        # Optional: User passes link to lab results data and / or reviews
        # data to train their own model.


        # TODO: User posts if the recommendation was useful or not.


@api_view(['GET', 'POST'])
def patents_stats(request, format=None):
    """Get, create, or update statistics about cannabis plant patents."""
    data = []
    if request.method == 'GET':

        # TODO: Return statistics about patents or a specific patent.
    
    elif request.method == 'POST':

        # TODO: Predict if a given set of lab results would be a good
        # candidate for a patent.
