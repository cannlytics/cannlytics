"""
CoA Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 6/14/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with CoA data.
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

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.coas.coas import CoADoc
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
FILE_TYPES = ['pdf', 'png', 'jpg', 'jpeg']

# Maximum number of observations that can be downloaded at once.
MAX_OBSERVATIONS_PER_FILE = 200_000


# def initialize_openai() -> None:
#     """Initialize OpenAI."""
#     _, project_id = google.auth.default()
#     openai_api_key = access_secret_version(
#         project_id=project_id,
#         secret_id='OPENAI_API_KEY',
#         version_id='latest',
#     )
#     openai.api_key = openai_api_key


@api_view(['GET', 'POST'])
def api_data_coas(request, sample_id=None):
    """Get CoA data (public API endpoint)."""

    # Authenticate the user.
    public, throttle = False, False
    claims = authenticate_request(request)
    total_cost = 0
    all_prompts = []
    if not claims:
        uid = None
        public, throttle = True, True
        # return HttpResponse(status=401)
    else:
        uid = claims['uid']
    
    print('USER:', uid)

    # Get a specific CoA or query open-source CoAs.
    if request.method == 'GET':

        # FIXME: Implement querying of pre-parsed CoA data!
        data = []
        params = request.query_params
        ref = 'public/data/lab_results'


        # Return the data.
        response = {'success': True, 'data': data}
        return Response(response, status=200)


    # Parse posted CoA PDFs or URLs.
    if request.method == 'POST':

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))
        except:
            body = {}
        urls = body.get('urls', [])

        print('POSTED URLS:', urls)

        # Get any user-posted files.
        pdfs, images = [], []
        request_files = request.FILES.getlist('file')
        if request_files is not None:
            print('POSTED FILES:', request_files)
            for coa_file in request_files:

                # File safety check.
                ext: str = coa_file.name.split('.').pop()

                # Reject files that are too large.
                if coa_file.size >= MAX_FILE_SIZE:
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
                temp_file.write(coa_file.read())
                temp_file.close()
                filepath = temp[1]

                # TODO: Save user's file to Firebase Storage.
                
                # Parse PDFs and images separately.
                if ext.lower() == 'pdf':
                    pdfs.append(filepath)
                else:
                    images.append(filepath)

        # Return an error if no PDFs or URLs are passed.
        if not urls and not pdfs and not images:
            message = 'Expecting an array of `urls`, `pdfs`, or `images` in the request body.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Return an error if too many PDFs or URLs are passed.
        if len(urls) > MAX_NUMBER_OF_FILES:
            message = f'Too many files, please limit your request to {MAX_NUMBER_OF_FILES} files at a time.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Parse COA data.
        parser = CoADoc()
        parsed_data = []

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
        
        if not openai_api_key:
            message = 'OpenAI API key not found.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Try to parse URLs and PDFs.
        for doc in urls + pdfs:
            try:
                print('Parsing:', doc)
                data = parser.parse(doc)
                parsed_data.extend(data)
            except:
                try:
                    print('Parsing with AI:', doc)
                    data, prompts, cost = parser.parse_with_ai(
                        doc,
                        openai_api_key=openai_api_key,
                        user=uid,
                        use_cached=True,
                        verbose=True,
                    )
                    parsed_data.extend([data])
                    all_prompts.extend(prompts)
                    total_cost += cost
                except:
                    print('Failed to parse:', doc)
                    continue
            

        # Try to parse images.
        for doc in images:
            coa_url = None
            try:
                print('Scanning:', doc)
                coa_url = parser.scan(doc)
                print('Scanned:', coa_url)
                data = parser.parse(coa_url)
                parsed_data.extend(data)
            except:
                try:
                    print('Parsing with AI:', doc)
                    data, prompts, cost = parser.parse_with_ai(
                        doc,
                        openai_api_key=openai_api_key,
                        user=uid,
                        use_cached=True,
                        verbose=True,
                    )
                    parsed_data.extend([data])
                    all_prompts.extend(prompts)
                    total_cost += cost
                except:
                    print('Failed to parse URL:', coa_url)
                    continue

        # Finish parsing.
        parser.quit()

        # TODO: Create a thumbnail of PDFs.

        # Create a usage log and save any public lab results.
        changes, refs, docs = [], [], []
        for obs in parsed_data:
            sample_id = obs['sample_id']

            # Create public lab result entries.
            if obs.get('public') or public:
                refs.append(f'public/data/lab_results/{sample_id}')
                docs.append(obs)

            # Create entries for the user.
            if claims:
                refs.append(f'users/{uid}/lab_results/{sample_id}')
                docs.append(obs)

            # Create a log entry.
            changes.append(obs)

        # Create a usage log.
        create_log(
            'logs/website/coa_doc',
            claims=claims,
            action='Parsed COAs.',
            log_type='coa_data',
            key='coa_data',
            changes=changes
        )

        # Record cost and prompts.
        timestamp = datetime.now().isoformat()
        doc_id = timestamp.replace(':', '-').replace('.', '-')
        refs.append(f'admin/ai/coa_doc_usage/{doc_id}')
        docs.append({
            'uid': uid,
            'timestamp': timestamp,
            'total_cost': total_cost,
            'prompts': all_prompts,
        })
        if claims:
            refs.append(f'users/{uid}/usage/{doc_id}')
            docs.append({
                'timestamp': timestamp,
                'total_cost': total_cost,
            })

        # Update the database.
        if refs:
            update_documents(refs, docs)

        # Return any extracted data.
        response = {'success': True, 'data': parsed_data}
        return Response(response, status=200)


@api_view(['POST'])
def download_coa_data(request):
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
    try:
        parser = CoADoc(init_all=False)
        parser.save(data, response)
        parser.quit()
    except:
        import pandas as pd
        pd.DataFrame(data).to_excel(response, index=False, sheet_name='Data')
    return response
