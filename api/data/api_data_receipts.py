"""
Receipt Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 6/15/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with receipt data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile

# External imports
import google.auth
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.sales.receipts_ai import ReceiptsParser
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    update_documents,
)

# Maximum number of files that can be parsed in one request.
MAX_NUMBER_OF_FILES = 10

# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['png', 'jpg', 'jpeg']

# Maximum number of observations that can be downloaded at once.
MAX_OBSERVATIONS_PER_FILE = 200_000


@api_view(['GET', 'POST'])
def api_data_receipts(request, sample_id=None):
    """Manage receipt data (public API endpoint)."""

    # Authenticate the user.
    public, throttle = False, False
    claims = authenticate_request(request)
    total_cost = 0
    all_prompts = []
    if not claims:
        uid = 'cannlytics'
        public, throttle = True, True
        # return HttpResponse(status=401)
    else:
        uid = claims['uid']
    
    # Log the user ID.
    print('USER:', uid)

    # Get previously parsed receipts.
    if request.method == 'GET':

        # FIXME: Implement querying of receipts.
        data = []
        params = request.query_params
        ref = f'users/{uid}/receipts'

        # Return the data.
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Parse posted receipt images.
    if request.method == 'POST':

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))
        except:
            body = {}
        
        # Get any user-posted files.
        images = []
        request_files = request.FILES.getlist('file')
        if request_files is not None:

            # Log the posted files.
            print('POSTED FILES:', request_files)

            # Save each file to the temporary directory.
            for image_file in request_files:

                # File safety check.
                ext: str = image_file.name.split('.').pop()

                # Reject files that are too large.
                if image_file.size >= MAX_FILE_SIZE:
                    message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)
                
                # Reject files that are not PDFs or ZIPs or common image types.
                if ext.lower() not in FILE_TYPES:
                    message = 'Invalid file type. Valid file types are: %s' % ', '.join(FILE_TYPES)
                    response = {'error': True, 'message': message}
                    return JsonResponse(response, status=406)

                # Save the file as a temp file for parsing.
                temp = tempfile.mkstemp(f'.{ext}')
                temp_file = os.fdopen(temp[0], 'wb')
                temp_file.write(image_file.read())
                temp_file.close()
                images.append(temp[1])

        # Return an error if no PDFs or URLs are passed.
        if not images:
            message = 'Expecting request files. Valid file types are: %s' % ', '.join(FILE_TYPES)
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Return an error if too many PDFs or URLs are passed.
        if len(images) > MAX_NUMBER_OF_FILES:
            message = f'Too many files, please limit your request to {MAX_NUMBER_OF_FILES} files at a time.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Initialize OpenAI.
        try:
            _, project_id = google.auth.default()
            openai_api_key = access_secret_version(
                project_id=project_id,
                secret_id='OPENAI_API_KEY',
                version_id='latest',
            )
        except:
            try:
                openai_api_key = os.environ['OPENAI_API_KEY']
            except:
                # Load credentials from a local environment variables file if provided.
                from dotenv import dotenv_values
                env_file = os.path.join('../../', '.env')
                if os.path.isfile(env_file):
                    config = dotenv_values(env_file)
                    key = 'OPENAI_API_KEY'
                    os.environ[key] = config[key]
        
        # Return an error if OpenAI can't be initialized.
        if not openai_api_key:
            message = 'OpenAI API key not found.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Parse the receipts.
        parser = ReceiptsParser()
        data = []
        total_cost = 0
        for image in images:
            receipt_data, cost = parser.parse(
                image,
                openai_api_key=openai_api_key,
                verbose=True,
                user=uid,
            )
            total_cost += cost
            data.append(receipt_data)

        # Close the parser.
        parser.quit()

        # Create a usage log and save the user's results.
        changes, refs, docs = [], [], []
        for obs in data:
            doc_id = obs['hash']

            # Create entries for the user.
            if uid:
                refs.append(f'users/{uid}/receipts/{doc_id}')
                docs.append(obs)

            # Create a log entry.
            changes.append(obs)
        
        # Create a usage log.
        create_log(
            'logs/data/receipts',
            claims=claims,
            action='Parsed receipts.',
            log_type='data',
            key='api_data_receipts',
            changes=changes
        )

        # FIXME: Record cost and prompts.
        ai_model = 'bud_spender'
        timestamp = datetime.now().isoformat()
        doc_id = timestamp.replace(':', '-').replace('.', '-')
        refs.append(f'admin/ai/{ai_model}_usage/{doc_id}')
        docs.append({
            'ai_model': ai_model,
            'uid': uid,
            'timestamp': timestamp,
            'total_cost': total_cost,
            # 'prompts': all_prompts,
        })
        if claims:
            refs.append(f'users/{uid}/usage/{doc_id}')
            docs.append({
                'ai_model': ai_model,
                'timestamp': timestamp,
                'total_cost': total_cost,
            })

        # Update the database.
        if refs:
            update_documents(refs, docs)

        # Return the data.
        response = {'success': True, 'data': data}
        return Response(response, status=200)


@api_view(['POST'])
def download_receipts_data(request):
    """Download posted data as a .xlsx file. Pass a `data` field in the
    body with the data, an object or an array of objects, to standardize
    and save in a workbook."""

    # TODO: Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        throttle = True
        # return HttpResponse(status=401)

    # Read the posted data.
    data = loads(request.body.decode('utf-8'))['data']
    if len(data) > MAX_OBSERVATIONS_PER_FILE:
        message = f'Too many observations, please limit your request to {MAX_OBSERVATIONS_PER_FILE} observations at a time.'
        response = {'success': False, 'message': message}
        return Response(response, status=400)

    # Create an Excel Workbook response.
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    filename = f'coa-data-{timestamp}.xlsx'
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={filename}'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = '*'

    # Create the Workbook and save it to the response.
    pd.DataFrame(data).to_excel(response, index=False, sheet_name='Data')
    return response
