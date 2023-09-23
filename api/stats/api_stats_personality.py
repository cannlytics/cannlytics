"""
Personality Stats Views | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/20/2022
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with the Big Five personality test.
"""
# Standard imports.
from json import loads

# External imports.
from cannlytics.utils.utils import get_timestamp
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports.
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    get_document,
    update_documents,
)
from cannlytics.stats.personality_test import score_personality_test


@api_view(['GET', 'POST'])
def personality_stats(request):
    """GET the Big 5 personality test questions and rubric.
    POST your completed test to get the Big 5
    personality trait metrics on a 0 to 1 scale.
    """

    # Return the test questions on a GET request.
    if request.method == 'GET':
        data = get_document('public/data/variables/personality_test')
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Return the personality score to the user.
    elif request.method == 'POST':
        test = loads(request.body.decode('utf-8'))
        print('Test:', test)
        score = score_personality_test(test)
        print('Score:', score)
        data = {**{'test': test}, **{'score': score}}
        message = 'Test scored but not recorded.'
        if test.get('save', request.query_params.get('save')):
            claims = authenticate_request(request)
            try:
                uid = claims['uid']
                timestamp = get_timestamp()
                refs = [
                    f'users/{uid}/stats/personality_test',
                    f'logs/stats/personality_tests/{timestamp}',
                ]
                update_documents(refs, [data, data])
                message = 'Test Saved.'
            except KeyError:
                message = 'Unauthenticated, test not saved.'
        response = {'success': True, 'data': data, 'message': message}
        return Response(response, status=200)
