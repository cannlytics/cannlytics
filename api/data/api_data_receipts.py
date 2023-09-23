"""
Receipt Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 9/20/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with receipt data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile
from urllib.parse import urlparse

# External imports
import google.auth
# from django.http.response import JsonResponse
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.sales.receipts_ai import ReceiptsParser
from cannlytics.data.strains.strains_ai import identify_strains
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
MAX_NUMBER_OF_FILES = 100

# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['png', 'jpg', 'jpeg']

# Maximum number of observations that can be downloaded at once.
MAX_OBSERVATIONS_PER_FILE = 200_000


def process_file_or_url(source, is_url=False, default_ext='jpg'):
    """
    If is_url is False, process a file and return the filepath.
    If is_url is True, download a file from a URL and return the filepath.
    """
    # Read the file.
    if is_url:
        parsed_url = urlparse(source)
        base_name = os.path.basename(parsed_url.path)
        ext = os.path.splitext(base_name)[1].lstrip('.')
        if not ext: ext = default_ext
        response = requests.get(source)
        if response.status_code != 200:
            print(f"Failed to download {source}")
            return None
        file_content = response.content
    else:
        ext: str = source.name.split('.').pop()
        file_content = source.read()

    # TODO: Reject files that are too large.
    # if len(file_content) >= MAX_FILE_SIZE:
    #     message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
    #     response = {'error': True, 'message': message}
    #     return JsonResponse(response, status=406)

    # TODO Reject files that are not of valid types.
    # if ext.lower() not in FILE_TYPES:
    #     message = 'Invalid file type. Valid file types are: %s' % ', '.join(FILE_TYPES)
    #     response = {'error': True, 'message': message}
    #     return JsonResponse(response, status=406)

    # Save the file as a temp file for parsing.
    temp = tempfile.mkstemp(f'.{ext}')
    with os.fdopen(temp[0], 'wb') as temp_file:
        temp_file.write(file_content)
    return temp[1]


@api_view(['GET', 'POST', 'DELETE', 'OPTIONS'])
def api_data_receipts(request, receipt_id=None):
    """Manage receipt data (public API endpoint)."""

    # Authenticate the user.
    throttle = False
    claims = authenticate_request(request)
    total_cost = 0
    if not claims:
        uid = 'cannlytics'
        throttle = True
    else:
        uid = claims['uid']

    # Log the user ID and their level of support.
    support_level = claims.get('support_level', 'free')
    print('USER:', uid)
    print('SUPPORT LEVEL:', support_level)

    # Allow enterprise, pro, and premium users to query more than 1000.
    if support_level in ['enterprise', 'pro', 'premium']:
        throttle = False

    # Get previously parsed receipts.
    if request.method == 'GET':

        # Get a specific receipt.
        if receipt_id:
            ref = f'users/{uid}/receipts/{receipt_id}'
            data = get_document(ref)
            response = {'success': True, 'data': data}
            return Response(response, status=200)

        # Query receipts.
        data, filters = [], []
        available_queries = [
            {
                'key': 'product_names',
                'operation': 'array_contains_any',
                'param': 'product_name',
            },
            {
                'key': 'product_types',
                'operation': 'array_contains_any',
                'param': 'product_type',
            },
            {
                'key': 'date_sold',
                'operation': '>=',
                'param': 'date',
            },
            {
                'key': 'total_price',
                'operation': '>=',
                'param': 'price',
            },
            {
                'key': 'retailer_license_number',
                'operation': '==',
                'param': 'license',
            },
            {
                'key': 'invoice_number',
                'operation': '==',
                'param': 'number',
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
            limit = params.get('limit')
        
        # Order the data.
        order_by = params.get('order_by', 'parsed_at')
        desc = params.get('desc', True)

        # Query documents.
        ref = f'users/{uid}/receipts'
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

    # Parse posted receipt images.
    if request.method == 'POST':

        # Get the user's level of support.
        user_subscription = get_document(f'subscribers/{uid}')
        current_tokens = user_subscription.get('tokens', 0) if user_subscription else 0
        if current_tokens < 1:
            message = 'You have 0 Cannlytics AI tokens. You need 1 AI token per AI job. You can purchase more tokens at https://cannlytics.com/account/subscriptions.'
            print(message)
            response = {'success': False, 'message': message}
            return Response(response, status=402)
        
        # Get any user-posted files.
        images = []
        request_files = request.FILES.getlist('file')
        if request_files:
            print('POSTED FILES:', request_files)
            for image_file in request_files:
                filepath = process_file_or_url(image_file)
                if filepath:
                    images.append(filepath)

        # Get any user-posted URLs.
        try:
            urls = loads(request.body.decode('utf-8')).get('urls', [])
            print('POSTED URLS IN BODY:', urls)
        except:
            try:
                urls = request.data.get('urls', [])
                print('POSTED URLS IN DATA:', urls)
            except:
                urls = []

        # Process the URLs.
        for url in urls:
            filepath = process_file_or_url(url, is_url=True)
            if filepath:
                images.append(filepath)

        # Return an error if no PDFs or URLs are passed.
        if not images:
            message = 'Expecting request files. Valid file types are: %s' % ', '.join(FILE_TYPES)
            print(message)
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Return an error if too many PDFs or URLs are passed.
        if len(images) > MAX_NUMBER_OF_FILES:
            message = f'Too many files, please limit your request to {MAX_NUMBER_OF_FILES} files at a time.'
            print(message)
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Initialize OpenAI.
        openai_api_key = None
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
            print(message)
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Parse the receipts.
        parser = ReceiptsParser()
        data = []
        for image in images:

            # Parse the receipt.
            print('Parsing receipt:', image)
            # FIXME:
            try:
                receipt_data = parser.parse(
                    image,
                    openai_api_key=openai_api_key,
                    max_tokens=3333,
                    verbose=True,
                    user=uid,
                )
            except Exception as e:
                print('Error parsing receipt:', e)

            # Extract strain names from product names.
            strain_names = []
            for name in receipt_data.get('product_names', []):
                try:
                    print('Identifying strain:', name)
                    names = identify_strains(name, user=uid)
                    if names:
                        strain_names.extend(names)
                except Exception as e:
                    print('Error identifying strain:', e)
            
            # Add the strain names to the receipt data.
            receipt_data['strain_names'] = strain_names

            # Upload the temporary image file to Firebase Storage.
            ext = image.split('.').pop()
            doc_id = receipt_data['hash']
            ref = 'users/%s/receipts/%s.%s' % (uid, doc_id, ext)
            print('Uploading receipt:', doc_id)
            upload_file(
                destination_blob_name=ref,
                source_file_name=image,
                bucket_name=STORAGE_BUCKET
            )

            # Get download and short URLs.
            print('Getting download URL for receipt.')
            download_url = get_file_url(ref, bucket_name=STORAGE_BUCKET)
            print('Getting short URL for receipt.')
            short_url = create_short_url(
                api_key=FIREBASE_API_KEY,
                long_url=download_url,
                project_name=project_id,
            )
            receipt_data['file_ref'] = ref
            receipt_data['download_url'] = download_url
            receipt_data['short_url'] = short_url

            # Record the extracted data
            data.append(receipt_data)

            # Debit the tokens from the user's account.
            print('Debiting tokens from user account.')
            current_tokens -= 1
            increment_value(
                ref=f'subscribers/{uid}',
                field='tokens',
                amount=-1,
            )

            # Stop parsing if the user runs out of tokens.
            if current_tokens < 1:
                break

        # Record the cost and close the parser.
        total_cost = parser.total_cost
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

        # Record costs for the admin and the user.
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
            print('Updating the database...')
            update_documents(refs, docs)

        # Return the data.
        response = {'success': True, 'data': data}
        return Response(response, status=200)
    
    # Return the data.
    if request.method == 'DELETE':

        # Get the receipt ID.
        if not receipt_id:
            try:
                receipt_id = loads(request.body.decode('utf-8'))['receipt_id']
            except:
                message = 'Please provide a `receipt_id` in the URL or your request body.'
                response = {'success': False, message: message}
                return Response(response, status=200)
        
        # Delete the receipt data.
        ref = f'users/{uid}/receipts/{receipt_id}'
        doc = get_document(ref)
        file_ref = doc.get('file_ref')
        delete_document(ref)

        # Delete the receipt file.
        if file_ref:
            delete_file(file_ref, bucket_name=STORAGE_BUCKET)

        # Return a success message.
        message = f'Receipt {receipt_id} deleted.'
        response = {'success': True, 'data': [], 'message': message}
        return Response(response, status=200)


@api_view(['POST'])
def download_receipts_data(request):
    """Download posted data as a .xlsx file. Pass a `data` field in the
    body with the data, an object or an array of objects, to standardize
    and save in a workbook."""

    # Authenticate the user, throttle requests if unauthenticated.
    throttle = False
    claims = authenticate_request(request)
    if not claims:
        uid = 'cannlytics'
        public, throttle = True, True
    else:
        uid = claims['uid']

    # Read the posted data.
    try:
        body = loads(request.body.decode('utf-8'))
        data = body['data']
    except:
        try:
            data = request.data.get('data', [])
        except:
            data = []

    # Handle no observations.
    if not data:
        message = f'No data, please post your data in a `data` field in the request body.'
        print(message)
        response = Response({'error': True, 'message': message}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    # Read the posted data.
    if len(data) > MAX_OBSERVATIONS_PER_FILE:
        message = f'Too many observations, please limit your request to {MAX_OBSERVATIONS_PER_FILE} observations at a time.'
        print(message)
        response = {'success': False, 'message': message}
        return Response(response, status=401)
    
    # Specify the filename.
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'receipt-data-{timestamp}.xlsx'

    # Save a temporary workbook.
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
        pd.DataFrame(data).to_excel(temp.name, index=False, sheet_name='Data')

    # Upload the file to Firebase Storage.
    ref = 'users/%s/receipts/%s' % (uid, filename)
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
        'filename': filename,
        'file_ref': ref,
        'download_url': download_url,
        'short_url': short_url,
    }

    # Delete the temporary file and return the data.
    os.unlink(temp.name)
    response = {'success': True, 'data': data}
    return Response(response, status=200)
