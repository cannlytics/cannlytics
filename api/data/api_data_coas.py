"""
COA Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with COA data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile
import uuid

# External imports
import google.auth
from django.http.response import JsonResponse
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pdfplumber

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.coas.coas import CoADoc
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    create_short_url,
    get_collection,
    get_document,
    get_file_url,
    increment_value,
    update_documents,
    upload_file,
    delete_document,
    delete_file,
)
from website.settings import FIREBASE_API_KEY, STORAGE_BUCKET


# Maximum number of files that can be parsed in one request.
MAX_NUMBER_OF_FILES = 10

# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['pdf', 'png', 'jpg', 'jpeg']

# Maximum number of observations that can be downloaded at once.
MAX_OBSERVATIONS_PER_FILE = 200_000


def save_file(uid, file, collection='files', project_id=None) -> dict:
    """Save a user's file to Firebase Storage."""

    # If the file is a URL, then download the file.
    if file.startswith('https'):
        ext = file.split('.')[-1].split('?')[0].lower()
        response = requests.get(file)
        temp = tempfile.mkstemp(f'.{ext}')
        with os.fdopen(temp[0], 'wb') as temp_file:
            temp_file.write(response.content)
        filepath = temp[1]

    # If the file is a PDF, then create an image of the first page.
    elif filepath.endswith('.pdf'):
        filepath = 'coa.png'
        pdf = pdfplumber.open(filepath)
        image = pdf.pages[0].to_image(resolution=96)
        image.save(filepath)

    # Otherwise, assume that it is an image.
    else:
        filepath = file

    # Create a document ID.
    doc_id = str(uuid.uuid4())

    # Upload the file to Firebase Storage.
    ext = filepath.split('.').pop()
    ref = 'users/%s/%s/%s.%s' % (uid, collection, doc_id, ext)
    upload_file(
        destination_blob_name=ref,
        source_file_name=image,
        bucket_name=STORAGE_BUCKET
    )

    # Get download and short URLs.
    download_url = get_file_url(ref, bucket_name=STORAGE_BUCKET)
    short_url = create_short_url(
        api_key=FIREBASE_API_KEY,
        long_url=download_url,
        project_name=project_id,
    )
    return {
        'file_ref': ref,
        'download_url': download_url,
        'short_url': short_url,
    }


@api_view(['GET', 'POST', 'DELETE'])
def api_data_coas(request, coa_id=None):
    """Get COA data (public API endpoint)."""

    # Authenticate the user.
    public, throttle = True, True
    claims = authenticate_request(request)
    total_cost = 0
    all_prompts = []
    if not claims:
        uid = 'cannlytics'
    else:
        uid = claims['uid']

    # Log the user ID and their level of support.
    support_level = claims.get('support_level', 'free')
    print('USER:', uid)
    print('SUPPORT LEVEL:', support_level)

    # Allow enterprise user's to have private lab results.
    if support_level == 'enterprise':
        public, throttle = False, False

    # Allow pro and premium users to query more than 1000 observations.
    elif support_level == 'pro' or support_level == 'premium':
        throttle = False
    
    # Get a specific COA or query public COAs.
    if request.method == 'GET':

         # Get a specific receipt.
        if coa_id:
            ref = f'users/{uid}/coas/{coa_id}'
            data = get_document(ref)
            response = {'success': True, 'data': data}
            return Response(response, status=200)

        # Query receipts.
        data, filters = [], []
        available_queries = [
            {
                'key': 'product_name',
                'operation': '==',
                'param': 'product_name',
            },
            {
                'key': 'product_type',
                'operation': '==',
                'param': 'product_type',
            },
            {
                'key': 'date_tested',
                'operation': '>=',
                'param': 'date',
            },
            {
                'key': 'total_thc',
                'operation': '>=',
                'param': 'thc',
            },
            {
                'key': 'total_cbd',
                'operation': '>=',
                'param': 'cbd',
            },
            {
                'key': 'total_terpenes',
                'operation': '>=',
                'param': 'terpenes',
            },
            {
                'key': 'lab',
                'operation': '==',
                'param': 'lab',
            },
            {
                'key': 'producer',
                'operation': '==',
                'param': 'producer',
            },
        ]
        params = request.query_params
        for query in available_queries:
            key = query['key']
            value = params.get(key)
            if value:
                filters.append({
                    'key': key,
                    'operation': params.get(key + '_op', query['operation']),
                    'value': value,
                })

        # Limit the number of observations.
        limit = int(params.get('limit', 1000))

        # Throttle the number of observations for free users.
        if throttle and limit > 1000:
            limit = 1000
        else:
            limit = None

        # Order the data.
        order_by = params.get('order_by', 'coa_parsed_at')
        desc = params.get('desc', True)

        # Query documents.
        ref = f'public/data/lab_results'
        data = get_collection(
            ref,
            desc=desc,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

        # Return the data.
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    # Parse posted COA PDFs or URLs.
    if request.method == 'POST':

        # Get the user's number of tokens.
        user_subscription = get_document(f'subscribers/{uid}')
        if not user_subscription:
            current_tokens = 0
        else:
            current_tokens = user_subscription.get('tokens', 0)
        if current_tokens < 1:
            message = 'You have 0 Cannlytics AI tokens. You need 1 AI token per AI job. You can purchase more tokens at https://cannlytics.com/account/subscriptions.'
            response = {'success': False, 'message': message}
            return Response(response, status=402)

        # Get any user-posted data.
        try:
            body = loads(request.body.decode('utf-8'))

            # Allow enterprise users to post public or private lab results.
            if support_level == 'enterprise':
                public = body.get('public', public)

        # Otherwise, the user must have only posted files.
        except:
            body = {}
        urls = body.get('urls', [])

        # Log the posted data.
        print('POSTED URLS:', urls)

        # Get any user-posted files.
        pdfs, images = [], []
        request_files = request.FILES.getlist('file')
        if request_files is not None:

            # Log the posted files.
            print('POSTED FILES:', request_files)

            # Save each file to the temporary directory.
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
        
        # Return an error if OpenAI can't be initialized.
        if not openai_api_key:
            message = 'OpenAI API key not found.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Try to parse URLs and PDFs.
        for doc in urls + pdfs:

            # Save user's file to Firebase Storage.
            try:
                file_data = save_file(uid, doc, 'coas', project_id=project_id)
            except:
                file_data = {}

            # Parse the document.
            try:
                print('Parsing:', doc)
                data = parser.parse(doc)
                parsed_data.append({**data[0], **file_data})
            except:
                try:

                    # Require tokens to parse with AI.
                    if current_tokens < 1:
                        continue

                    # Parse COA with AI.
                    print('Parsing with AI:', doc)
                    data, prompts, cost = parser.parse_with_ai(
                        doc,
                        openai_api_key=openai_api_key,
                        user=uid,
                        use_cached=True,
                        verbose=True,
                    )
                    parsed_data.append({**data, **file_data})
                    all_prompts.extend(prompts)
                    total_cost += cost
                    
                    # Debit the tokens from the user's account.
                    current_tokens -= 1
                    increment_value(
                        ref=f'subscribers/{uid}',
                        field='tokens',
                        amount=-1,
                    )
                except:
                    print('Failed to parse:', doc)
                    continue

        # Try to parse images.
        for doc in images:

            # Save user's file to Firebase Storage.
            try:
                file_data = save_file(uid, doc, 'coas', project_id=project_id)
            except:
                file_data = {}

            coa_url = None
            try:
                print('Scanning:', doc)
                coa_url = parser.scan(doc)
                print('Scanned:', coa_url)
                data = parser.parse(coa_url)
                parsed_data.append({**data[0], **file_data})
            except:

                # Require tokens to parse with AI.
                if current_tokens < 1:
                    continue

                # Try to parse with AI.
                try:
                    print('Parsing with AI:', doc)
                    data, prompts, cost = parser.parse_with_ai(
                        doc,
                        openai_api_key=openai_api_key,
                        user=uid,
                        use_cached=True,
                        verbose=True,
                    )
                    parsed_data.append({**data, **file_data})
                    all_prompts.extend(prompts)
                    total_cost += cost

                    # Debit the tokens from the user's account.
                    current_tokens -= 1
                    increment_value(
                        ref=f'subscribers/{uid}',
                        field='tokens',
                        amount=-1,
                    )
                except:
                    print('Failed to parse URL:', coa_url)
                    continue

        # Finish parsing.
        parser.quit()

        # Create a usage log and save any public lab results.
        changes, refs, docs = [], [], []
        for obs in parsed_data:
            sample_id = obs['sample_id']

            # Create public lab result entries.
            if obs.get('public') or public:
                refs.append(f'public/data/lab_results/{sample_id}')
                docs.append(obs)

            # Create entries for the user.
            if uid:
                refs.append(f'users/{uid}/lab_results/{sample_id}')
                docs.append(obs)

            # Create a log entry.
            changes.append(sample_id)
            changes.append(obs)

        # Create a usage log.
        create_log(
            'logs/data/coas',
            claims=claims,
            action='Parsed COAs.',
            log_type='data',
            key='api_data_coas',
            changes=changes
        )

        # Record cost and prompts.
        ai_model = 'coa_doc'
        timestamp = datetime.now().isoformat()
        doc_id = timestamp.replace(':', '-').replace('.', '-')
        refs.append(f'admin/ai/{ai_model}_usage/{doc_id}')
        docs.append({
            'ai_model': ai_model,
            'uid': uid,
            'timestamp': timestamp,
            'total_cost': total_cost,
            'prompts': all_prompts,
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

        # Return any extracted data.
        response = {'success': True, 'data': parsed_data}
        return Response(response, status=200)
    
    # Return the data.
    if request.method == 'DELETE':

        # Get the document ID.
        if not coa_id:
            try:
                coa_id = loads(request.body.decode('utf-8'))['id']
            except:
                message = 'Please provide an `id` in the URL or your request body.'
                response = {'success': False, message: message}
                return Response(response, status=200)
        
        # Delete the document.
        ref = f'users/{uid}/coas/{coa_id}'
        doc = get_document(ref)
        file_ref = doc.get('file_ref')
        delete_document(ref)

        # Delete any image file.
        if file_ref:
            delete_file(file_ref, bucket_name=STORAGE_BUCKET)

        # Return a success message.
        message = f'COA {coa_id} deleted.'
        response = {'success': True, 'data': [], 'message': message}
        return Response(response, status=200)


@api_view(['POST'])
def download_coa_data(request):
    """Download posted data as a .xlsx file. Pass a `data` field in the
    body with the data, an object or an array of objects, to standardize
    and save in a workbook."""

    # Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        uid = 'cannlytics'
        throttle = True
    else:
        uid = claims['uid']

    # TODO: Allow the user to specify the Firestore query
    # that they want to download.

    # Read the posted data.
    data = loads(request.body.decode('utf-8'))['data']
    if len(data) > MAX_OBSERVATIONS_PER_FILE:
        message = f'Too many observations, please limit your request to {MAX_OBSERVATIONS_PER_FILE} observations at a time.'
        response = {'success': False, 'message': message}
        return Response(response, status=400)
    
    # Specify the filename.
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    filename = f'coa-data-{timestamp}.xlsx'

    # Save a temporary workbook.
    try:
        parser = CoADoc(init_all=False)
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
            parser.save(data, temp.name)
            parser.quit()
    except:
        import pandas as pd
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
            pd.DataFrame(data).to_excel(temp.name, index=False, sheet_name='Data')

    # Upload the file to Firebase Storage.
    ref = 'users/%s/lab_results/%s' % (uid, filename)
    _, project_id = google.auth.default()
    upload_file(
        destination_blob_name=ref,
        source_file_name=temp.name,
        bucket_name=STORAGE_BUCKET
    )

    # Get download and short URLs.
    download_url = get_file_url(ref, bucket_name=STORAGE_BUCKET)
    short_url = create_short_url(
        api_key=FIREBASE_API_KEY,
        long_url=download_url,
        project_name=project_id
    )
    data = {
        'file_ref': ref,
        'download_url': download_url,
        'short_url': short_url,
    }

    # Delete the temporary file and return the data.
    os.unlink(temp.name)
    response = {'success': True, 'data': data}
    return Response(response, status=200)
