"""
COA Data Endpoints | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/17/2022
Updated: 9/20/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with COA data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile
from urllib.parse import urlparse
import uuid

# External imports
from django.views.decorators.csrf import csrf_exempt
import google.auth
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
MAX_NUMBER_OF_FILES = 100

# Maximum file size for a single file.
MAX_FILE_SIZE = 1024 * 1000 * 100 # (100 MB)

# Specify file types.
FILE_TYPES = ['pdf', 'png', 'jpg', 'jpeg']

# Maximum number of observations that can be downloaded at once.
MAX_OBSERVATIONS_PER_FILE = 999_999


def save_file(
        uid,
        file,
        collection='files',
        project_id=None,
    ) -> dict:
    """Save a user's file to Firebase Storage."""

    # If the file is a URL, then download the file.
    if file.startswith('https'):
        parsed_url = urlparse(file)
        base_name = os.path.basename(parsed_url.path)
        ext = os.path.splitext(base_name)[1].lstrip('.')
        if not ext:
            ext = 'pdf'
        response = requests.get(file)
        temp = tempfile.mkstemp(f'.{ext}')
        with os.fdopen(temp[0], 'wb') as temp_file:
            temp_file.write(response.content)
        filepath = temp[1]

    # FIXME: If the file is a PDF, then create a thumbnail of the first page.
    # elif filepath.endswith('.pdf'):
    #     filepath = 'coa.png'
    #     pdf = pdfplumber.open(filepath)
    #     image = pdf.pages[0].to_image(resolution=96)
    #     image.save(filepath)

    # Otherwise, assume that it is an image.
    else:
        filepath = file

    print('SAVING FILEPATH:', filepath)

    # Create a document ID.
    doc_id = str(uuid.uuid4())

    # Upload the file to Firebase Storage.
    try:
        ext = filepath.split('.').pop()
    except Exception as e:
        print('ERROR GETTING FILE EXTENSION:', str(e))
        ext = 'pdf'
    ref = 'users/%s/%s/%s.%s' % (uid, collection, doc_id, ext)
    upload_file(
        destination_blob_name=ref,
        source_file_name=filepath,
        bucket_name=STORAGE_BUCKET
    )

    # Get download and short URLs.
    download_url, short_url = None, None
    try:
        download_url = get_file_url(ref, bucket_name=STORAGE_BUCKET)
        short_url = create_short_url(
            api_key=FIREBASE_API_KEY,
            long_url=download_url,
            project_name=project_id,
        )
    except Exception as e:
        print('Failed to create URLs:', e)

    # Return the file data.
    filename = filepath.split('/')[-1].split('.')[0]
    return {
        'filepath': filepath,
        'filename': filename,
        'file_ref': ref,
        'download_url': download_url,
        'short_url': short_url,
    }


@api_view(['GET', 'POST', 'DELETE', 'OPTIONS'])
@csrf_exempt
def api_data_coas(request, coa_id=None):
    """Get COA data (public API endpoint)."""

    # Authenticate the user.
    claims = authenticate_request(request)
    uid = claims['uid'] if claims else 'cannlytics'

    # Parameters.
    public, throttle = True, True
    total_cost = 0
    all_prompts = []

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

        # Disallow unauthenticated requests.
        if uid == 'cannlytics':
            message = 'You need to authenticate with an Authentication: Bearer <token> header to request lab result data.'
            response = Response({'error': True, 'message': message}, status=402)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Get a specific receipt.
        if coa_id:
            print('GETTING COA:', coa_id)
            ref = f'users/{uid}/coas/{coa_id}'
            data = get_document(ref)
            response = {'success': True, 'data': data}
            response = Response(response, status=200)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Query receipts.
        print('QUERYING COAS...')
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

        # Order the data.
        order_by = params.get('order_by', 'coa_parsed_at')
        desc = params.get('desc', True)

        # Query documents.
        print('PARAMETERS:', order_by, desc, limit, str(filters))
        if params.get('public'):
            ref = f'public/data/lab_results'
        else:
            ref = f'users/{uid}/lab_results'
        print('REF:', ref)
        ref = f'public/data/lab_results'
        data = get_collection(
            ref,
            desc=desc,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )
        print('FOUND %i COAS.' % len(data))

        # Return the data.
        response = {'success': True, 'data': data}
        response = Response(response, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    # Parse posted COA PDFs or URLs.
    if request.method == 'POST':

        # Get the user's number of tokens.
        user_subscription = get_document(f'subscribers/{uid}')
        current_tokens = user_subscription.get('tokens', 0) if user_subscription else 0
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

                # try:
                #     pdfs.append(pdfplumber.open(coa_file))
                #     continue
                # except Exception as e:
                #     print('FAILED TO OPEN FILE AS PDF:', str(e))

                # File safety check.
                ext: str = coa_file.name.split('.').pop()

                # Reject files that are too large.
                if coa_file.size >= MAX_FILE_SIZE:
                    message = 'File too large. The maximum number of bytes is %i.' % MAX_FILE_SIZE
                    response = Response({'error': True, 'message': message}, status=406)
                    response['Access-Control-Allow-Origin'] = '*'
                    return response
                
                # Reject files that are not PDFs or ZIPs or common image types.
                if ext.lower() not in FILE_TYPES:
                    message = 'Invalid file type. Valid file types are: %s' % ', '.join(FILE_TYPES)
                    response = Response({'error': True, 'message': message}, status=406)
                    response['Access-Control-Allow-Origin'] = '*'
                    return response

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
            response = Response({'error': True, 'message': message}, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Return an error if too many PDFs or URLs are passed.
        if len(urls) > MAX_NUMBER_OF_FILES:
            message = f'Too many files, please limit your request to {MAX_NUMBER_OF_FILES} files at a time.'
            response = Response({'error': True, 'message': message}, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Parse COA data.
        parser = CoADoc()
        parsed_data = []

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
            response = Response({'error': True, 'message': message}, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Try to parse URLs and PDFs.
        for doc in urls + pdfs:

            # Save user's file to Firebase Storage.
            try:
                file_data = save_file(
                    uid=uid,
                    file=doc,
                    collection='coas',
                    project_id=project_id,
                )
                print('Saved file:', doc)
            except:
                print('Failed to save file:', doc)
                file_data = {}

            # Use the temporary file for parsing.
            coa_file = file_data.get('filepath', doc)
            # coa_file = file_data.get('download_url', doc)

            # Parse the document.
            try:
                # try:
                print('Parsing:', coa_file)
                data = parser.parse(coa_file, verbose=True)
                print('PARSED:', str(data))
                parsed_data.append({**data[0], **file_data})
                # except Exception as e:
                #     print('ERROR PARSING COA:', str(e))
                #     print('Parsing:', doc)
                #     data = parser.parse(doc)
                #     print('PARSED:', str(data))
                #     parsed_data.append({**data[0], **file_data})
                
            except Exception as e:
                print('ERROR PARSING COA:', str(e))
                try:

                    # Require tokens to parse with AI.
                    if current_tokens < 1:
                        continue

                    # Parse COA with AI.
                    print('Parsing with AI:', coa_file)
                    # print('SKIPPING FOR DEV')
                    # continue

                    data, prompts, cost = parser.parse_with_ai(
                        coa_file,
                        openai_api_key=openai_api_key,
                        user=uid,
                        verbose=True,
                        max_tokens=4_000,
                        max_prompt_length=1_000,
                    )
                    print('PARSED:', str(data))
                    parsed_data.append({**data, **file_data})
                    all_prompts.extend(prompts)
                    total_cost += cost
                    
                    # Debit the tokens from the user's account.
                    try:
                        current_tokens -= 1
                        increment_value(
                            ref=f'subscribers/{uid}',
                            field='tokens',
                            amount=-1,
                        )
                    except:
                        print('Failed to debit tokens from user:', uid)

                except Exception as e:
                    print('ERROR PARSING COA WITH AI:', str(e))
                    continue

        # Try to parse images.
        for doc in images:

            # Save user's file to Firebase Storage.
            try:
                print('Saving file:', doc)
                file_data = save_file(
                    uid=uid,
                    file=doc,
                    collection='coas',
                    project_id=project_id,
                )
            except:
                print('Failed to save file:', doc)
                file_data = {}

            coa_url = None
            try:
                print('Scanning:', doc)
                coa_url = parser.scan(doc)
                print('Scanned:', coa_url)
                data = parser.parse(coa_url)
                parsed_data.append({**data[0], **file_data})
            except Exception as e:
                print('ERROR SCANNING COA:', str(e))

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
                        # use_cached=True,
                        verbose=True,
                        max_tokens=4_000,
                        max_prompt_length=2_750,
                    )
                    parsed_data.append({**data, **file_data})
                    all_prompts.extend(prompts)
                    total_cost += cost

                    # Debit the tokens from the user's account.
                    try:
                        current_tokens -= 1
                        increment_value(
                            ref=f'subscribers/{uid}',
                            field='tokens',
                            amount=-1,
                        )
                    except:
                        print('Failed to debit tokens from user:', uid)
    
                except Exception as e:
                    print('Failed to parse URL:', coa_url)
                    print(str(e))
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
        try:
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
        except Exception as e:
            print('Failed to record AI usage:', str(e))

        # Update the database.
        if refs:
            print('Updating database...')
            update_documents(refs, docs)

        # Return any extracted data.
        response = Response({'success': True, 'data': parsed_data}, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    # Return the data.
    if request.method == 'DELETE':

        # Get the document ID.
        if not coa_id:
            try:
                coa_id = loads(request.body.decode('utf-8'))['id']
            except:
                message = 'Please provide an `id` in the URL or your request body.'
                response = {'success': False, 'message': message}
                response = Response(response, status=200)
                response['Access-Control-Allow-Origin'] = '*'
                return response
        
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
        response = Response(response, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@api_view(['POST', 'OPTIONS'])
@csrf_exempt
def download_coa_data(request):
    """Download posted data as a .xlsx file. Pass a `data` field in the
    body with the data, an object or an array of objects, to standardize
    and save in a workbook."""

    # Authenticate the user, throttle requests if unauthenticated.
    claims = authenticate_request(request)
    uid = claims['uid'] if claims else 'cannlytics'
    print(f'USER {uid} POSTED DATA')

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

    # Handle too many observations.
    count = len(data)
    if count > MAX_OBSERVATIONS_PER_FILE:
        message = f'Too many observations, please limit your request to {MAX_OBSERVATIONS_PER_FILE} observations at a time.'
        print(message)
        response = Response({'error': True, 'message': message}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    # Specify the filename.
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
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
    print('UPLOADING FILE:', ref)
    _, project_id = google.auth.default()
    upload_file(
        destination_blob_name=ref,
        source_file_name=temp.name,
        bucket_name=STORAGE_BUCKET
    )
    print('UPLOADED FILE:', ref)

    # Delete the temporary file.
    os.unlink(temp.name)

    # Get download URL and create a short URL.
    download_url, short_url = None, None
    try:
        download_url = get_file_url(ref, bucket_name=STORAGE_BUCKET)
        print('DOWNLOAD URL:', download_url)
        short_url = create_short_url(
            api_key=FIREBASE_API_KEY,
            long_url=download_url,
            project_name=project_id
        )
        print('SHORT URL:', short_url)
    except Exception as e:
        print('Failed to get download URL:', e)

    # Format file data.
    data = {
        'filename': filename,
        'file_ref': ref,
        'download_url': download_url,
        'short_url': short_url,
    }

    # Save the file data as a log.
    create_log(
        f'users/{uid}/downloads',
        claims=claims,
        action=f'Downloaded {count} COAs.',
        log_type='data',
        key='download_coa_data',
        changes=[data]
    )

    # Return the data.
    response = Response({'success': True, 'data': data}, status=200)
    response['Access-Control-Allow-Origin'] = '*'
    return response
