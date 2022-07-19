"""
CoA Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 7/17/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with CoA data.
"""
# Standard imports.
from json import loads

# External imports
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.data.coas import CoADoc

# For safety, restrict the possible URLs to a whitelist.
WHITELIST = [
    'https://lims.tagleaf.com',
    'https://orders.confidentcannabis.com',

]

@api_view(['GET', 'POST'])
def coa_data(request, sample_id=None):

    # Get a specific CoA or query open-source CoAs.
    if request.method == 'GET':

        # TODO: Implement getting CoA data!
        params = request.query_params
        ref = 'public/coas/coa_data'

    # Parse posted CoA PDFs or URLs.
    if request.meth == 'POST':

        # ref = 'public/coas/coa_data'

        # Get the data the user posted.
        body = loads(request.body.decode('utf-8'))
        urls = body.get('urls')
        if urls is None:
            message = 'Expecting an array of `urls` in the request body.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Allow the user to pass parameters:
        # - headers
        # - kind
        # - lims
        # - max_delay
        # - persist

        # FIXME: Figure out how to handle URLs vs. PDFs.

        # Parse CoA data.
        parser = CoADoc()
        data = parser.parse(urls)
        parser.quit()

        # Return either file or JSON.
        response = {'success': True, 'data': data}
        return Response(response, status=200)
