"""
Receipt Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 5/13/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with receipt data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile

# External imports
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.sales.receipts_ai import BudSpender
from cannlytics.firebase.firebase import create_log, update_documents

# Maximum number of files that can be parsed in 1 request.
MAX_NUMBER_OF_FILES = 120

# Maximum file size for a single file: 100 MB.
MAX_FILE_SIZE = 1024 * 1000 * 100


@api_view(['GET', 'POST'])
def receipt_data(request, sample_id=None):
    """Manage receipt data (public API endpoint)."""

    # TODO: Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        throttle = True
        # return HttpResponse(status=401)

    # Get a specific CoA or query open-source CoAs.
    if request.method == 'GET':

        # FIXME: Allow the user to query their receipts.
        data = []
        response = {'success': True, 'data': data}
        return Response(response, status=200)


    # Parse posted CoA PDFs or URLs.
    if request.method == 'POST':

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))
        except:
            body = {}
        
        # Get any user-posted files.
        temp_files = []
        request_files = request.FILES
        if request_files is not None:
            for key, request_file in request.FILES.items():

                # File safety check.
                ext = request_file.name.split('.').pop()
                if request_file.size >= MAX_FILE_SIZE:
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
                temp_file.write(request_file.read())
                temp_file.close()
                filepath = temp[1]
                temp_files.append(filepath)

        # Return an error if no receipts are passed.
        if not temp_files:
            message = 'Expecting receipt files in the request.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Return an error if too many PDFs or URLs are passed.
        if len(temp_files) > MAX_NUMBER_OF_FILES:
            message = f'Too many files, please limit your request to {MAX_NUMBER_OF_FILES} files at a time.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # TODO: Parse the receipts!
        parser = BudSpender()
        data = parser.parse(temp_files)
        parser.quit()

        # TODO: Save the receipt data.
        changes, refs, docs = [], [], []
        # for item in data:
        #     if item.get('public'):
        #         changes.append(item)
        #         sample_id = item['sample_id']
        #         refs.append(f'public/data/lab_results/{sample_id}')
        #         docs.append(item)
        # if refs:
        #     update_documents(refs, docs)
        
        # Create a usage log.
        create_log(
            'logs/data/receipts',
            claims=claims,
            action='Parsed receipts.',
            log_type='data',
            key='receipt_data',
            changes=changes
        )

        # Return the data.
        response = {'success': True, 'data': docs}
        return Response(response, status=200)
