"""
CoA Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 8/20/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with CoA data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile

# External imports
from django.http import HttpResponse
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.coas import CoADoc
from cannlytics.firebase.firebase import create_log, update_documents

# Maximum number of files that can be parsed in 1 request.
MAX_NUMBER_OF_FILES = 420

# Maximum file size for a single file: 100 MB.
MAX_FILE_SIZE = 1024 * 1000 * 100

# For safety, restrict the possible URLs to a whitelist.
WHITELIST = [
    'https://orders.confidentcannabis.com',
    'https://client.sclabs.com',
    'https://reports.mcrlabs.com',
    'https://lims.tagleaf.com',
]

@api_view(['GET', 'POST'])
def coa_data(request, sample_id=None):
    """Get CoA data (public API endpoint)."""

    # Authenticate the user.
    throttle = False
    claims = authenticate_request(request)
    print('User:', claims)
    if not claims:
        # return HttpResponse(status=401)
        throttle = True

    # Get a specific CoA or query open-source CoAs.
    if request.method == 'GET':

        # TODO: Implement getting CoA data!
        params = request.query_params
        ref = 'public/coas/coa_data'

        # TODO: Get Metrc results here!!!


    # Parse posted CoA PDFs or URLs.
    if request.method == 'POST':

        # ref = 'public/coas/coa_data'

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))
        except:
            body = {}
        print('User data:', body)
        urls = body.get('urls', [])

        # Get any user-posted files.
        print('Files:', request.FILES)
        request_files = request.FILES
        if request_files is not None:
            for key, coa_file in request.FILES.items():

                # File safety check.
                ext = coa_file.name.split('.').pop()
                if coa_file.size >= MAX_FILE_SIZE:
                    message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)
                if ext != 'pdf' and ext != 'zip':
                    message = 'Invalid file type. Expecting a .pdf or .zip file.'
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)

                # Keep temp file to open as a PDF.
                temp = tempfile.mkstemp(key)
                temp_file = os.fdopen(temp[0], 'wb')
                temp_file.write(coa_file.read())
                temp_file.close()
                filepath = temp[1]
                urls.append(filepath)

        if not urls:
            message = 'Expecting an array of `urls` in the request body.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Allow the user to pass parameters:
        # - headers
        # - kind
        # - lims
        # - max_delay
        # - persist

        if len(urls) > MAX_NUMBER_OF_FILES:
            message = 'Too many files, please limit your request to 420 files at a time.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # FIXME: Figure out how to handle URLs vs. PDFs.
        print('URLs:', urls)

        # FIXME: Parse CoA data.
        parser = CoADoc()
        data = parser.parse(urls)
        parser.quit()

        # PRODUCTION:
        # Create usage log and save any public lab results.
        # changes = []
        # refs = []
        # docs = []
        # for item in data:
        #     if item.get('public'):
        #         changes.append(item)
        #         sample_id = item['sample_id']
        #         refs.append(f'public/data/lab_results/{sample_id}')
        #         docs.append(item)
        # if refs:
        #     update_documents(refs, docs)
        # create_log(
        #     'logs/website/coa_doc',
        #     claims=claims,
        #     action='Parsed CoAs.',
        #     log_type='coa_data',
        #     key='coa_data',
        #     changes=changes
        # )

        # Return either file or JSON.
        response = {'success': True, 'data': data}
        return Response(response, status=200)


def download_coa_data(request):
    """Download posted data as a CSV file."""
    # TODO: Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        # return HttpResponse(status=401)
        throttle = True

    # FIXME: Gracefully handle errors!

    # Read the posted data.
    data = loads(request.body.decode('utf-8'))['data']

    # TODO: Perform safety checks on the data?

    # FIXME:
    # Create an Excel Workbook response.
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    filename = f'coa-data-{timestamp}.xlsx'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # application/vnd.ms-excel
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Create the Workbook and save it to the response.
    parser = CoADoc()
    parser.save(data, response)
    return response
