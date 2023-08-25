"""
Strain Data Endpoints | Cannlytics API
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 8/22/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with strain data.
"""
# Standard imports:
from datetime import datetime
from json import loads
import os
import tempfile

# External imports:
from django.views.decorators.csrf import csrf_exempt
import google.auth
from google.auth import compute_engine
import google.auth.transport.requests as g_requests
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports:
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.strains.strains_ai import (
    generate_strain_art,
    generate_strain_description,
    identify_strains,
)
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    create_short_url,
    get_collection,
    get_document,
    get_file_url,
    update_document,
    upload_file,
)
from website.settings import FIREBASE_API_KEY, STORAGE_BUCKET


# Default instructions for generating strain art.
DEFAULT_ART_INSTRUCTIONS = ' in the style of a high-quality scientific image'

# Default instructions for generating strain descriptions.
DEFAULT_DESCRIPTION_INSTRUCTIONS = 'Please be as scientific as possible and avoid references to purported effects and medical uses.'

# Default temperature for generating strain descriptions.
DEFAULT_TEMPERATURE = 0.42

# Default word count for generating strain descriptions.
DEFAULT_WORD_COUNT = 100


@api_view(['GET', 'POST', 'OPTIONS'])
@csrf_exempt
def api_data_strains(request, strain_id=None):
    """Manage strain data (public API endpoint)."""

    # Authenticate the user.
    throttle = False
    claims = authenticate_request(request)
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
    # Also allow subscribers access to better models.
    base_model = 'gpt-3.5-turbo'
    if support_level in ['enterprise', 'pro', 'premium']:
        throttle = False
        base_model = 'gpt-4'

    # Get previously parsed strains.
    if request.method == 'GET':

        # TODO: Allow the user to get descriptions
        # and art for a strain.

        # Get a specific strain.
        if strain_id:
            ref = f'users/{uid}/strains/{strain_id}'
            data = get_document(ref)
            response = Response({'success': True, 'data': data}, status=200)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Query strains.
        data, filters = [], []
        available_queries = [
            {
                'key': 'name',
                'operation': '==',
                'param': 'name',
            },
            {
                'key': 'keywords',
                'operation': 'array_contains_any',
                'param': 'keyword',
            },
            # Add more filters based on strain data fields...
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
        order_by = params.get('order_by', 'strain_name')
        desc = params.get('desc', False)

        # Query documents.
        ref = 'public/data/strains'
        data = get_collection(
            ref,
            desc=desc,
            filters=filters,
            limit=limit,
            order_by=order_by,
        )

        # Return the data.
        response = Response({'success': True, 'data': data}, status=200)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    # Create or update strain data.
    elif request.method == 'POST':

        # Get the posted data.
        body = request.data

        # Initialize OpenAI if text is posted.
        text = body.get('text')
        openai_api_key = None
        if text:
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
        if not openai_api_key and text:
            message = 'OpenAI API key not found.'
            response = Response({'error': True, 'message': message}, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response

        # Create a unique ID for the generation.
        content_id = datetime.now().strftime('%Y%m%d%H%M%S')
        doc_id = body.get('id', content_id)
        print('Edit to:', doc_id)

        # Generate a description.
        if strain_id == 'description':

            # Get parameters.
            model = body.get('model', base_model)
            temperature = body.get('temperature', DEFAULT_TEMPERATURE)
            word_count = body.get('word_count', DEFAULT_WORD_COUNT)
            stats = body.get('stats', {})
            instructions = body.get('instructions', DEFAULT_DESCRIPTION_INSTRUCTIONS)
            try:
                stats = loads(stats)
            except:
                pass
            action = f'Generated strain description for {doc_id}.'

            # If the strain already has a description, then
            # require the user to have a subscription to generate a new one.
            doc = get_document(f'public/data/strains/{doc_id}')
            if doc.get('description'):
                support_level = claims.get('support_level', 'free')
                print('USER:', uid)
                print('SUPPORT LEVEL:', support_level)
                if support_level in ['enterprise', 'pro', 'premium']:
                    message = 'A Cannlytics subscription is required to re-generate a description. You can get a subscription at https://cannlytics.com/account/subscriptions.'
                    response = Response({'error': True, 'message': message}, status=402)
                    response['Access-Control-Allow-Origin'] = '*'
                    return response

            # Generate the description.
            content = generate_strain_description(
                text,
                instructions=instructions,
                model=model,
                openai_api_key=openai_api_key,
                temperature=temperature,
                word_count=word_count,
                stats=stats,
                verbose=True,
                user=uid,
            )

        # Generate art.
        elif strain_id == 'art':
            # Get parameters.
            action = f'Generated strain art for {doc_id}.'
            art_style = body.get('style', DEFAULT_ART_INSTRUCTIONS)
            size = body.get('size', '1024x1024')

            # If the strain already has an image, then
            # require the user to have a subscription to generate a new one.
            doc = get_document(f'public/data/strains/{doc_id}')
            if doc.get('image_url'):
                support_level = claims.get('support_level', 'free')
                print('USER:', uid)
                print('SUPPORT LEVEL:', support_level)
                if support_level in ['enterprise', 'pro', 'premium']:
                    message = 'A Cannlytics subscription is required to re-generate strain art. You can get a subscription at https://cannlytics.com/account/subscriptions.'
                    response = Response({'error': True, 'message': message}, status=402)
                    response['Access-Control-Allow-Origin'] = '*'
                    return response

            # Generate art.
            content = generate_strain_art(
                text,
                openai_api_key=openai_api_key,
                art_style=art_style,
                n=1,
                size=size,
                user=uid,
            )

            # Save the image to a temporary file.
            response = requests.get(content, stream=True)
            response.raise_for_status()
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            for chunk in response.iter_content(chunk_size=8192): 
                if chunk: 
                    temp_file.write(chunk)
            temp_file.close()

            # Upload the file to Firebase Storage.
            destination_blob_name = f'public/data/strains/{doc_id}/images/{content_id}.jpg'
            upload_file(
                destination_blob_name=destination_blob_name,
                source_file_name=temp_file.name,
                bucket_name=STORAGE_BUCKET,
            )

            # Generate a download URL.
            download_url, short_url = None, None
            _, project_id = google.auth.default()
            try:
                download_url = get_file_url(
                    ref=destination_blob_name,
                    bucket_name=STORAGE_BUCKET,
                )
                short_url = create_short_url(
                    api_key=FIREBASE_API_KEY,
                    long_url=download_url,
                    project_name=project_id
                )
            except Exception as e:
                print('Failed to create URLs:', e)

            # Format image data.
            content = data = {
                'filename': temp_file.name,
                'file_ref': destination_blob_name,
                'download_url': download_url,
                'short_url': short_url,
            }

        # Identify strain names.
        elif strain_id == 'name':
            action = 'Identified strain names.'
            content = identify_strains(text)

        # Allow users with subscriptions to save edits to strains.
        elif uid != 'cannlytics':

            # Require the user to have a subscription to edit strains.
            support_level = claims.get('support_level', 'free')
            print('USER:', uid)
            print('SUPPORT LEVEL:', support_level)
            if support_level in ['enterprise', 'pro', 'premium']:
                message = 'A Cannlytics subscription is required to edit strains. You can get a subscription at https://cannlytics.com/account/subscriptions.'
                response = Response({'error': True, 'message': message}, status=402)
                response['Access-Control-Allow-Origin'] = '*'
                return response

            # Prepare data to be saved to Firestore
            content = {
                'updated_by': uid,
                'updated_at': datetime.now().isoformat(),
                'description': body.get('description'),
                'aliases': body.get('aliases'),
                'origin': body.get('origin'),
                'chemotype': body.get('chemotype'),
                'folklore': body.get('folklore'),
                'etymology': body.get('etymology'),
                'history': body.get('history'),
                'references': body.get('references'),
                'awards': body.get('awards'),
            }

            # Remove keys with None values
            content = {k: v for k, v in content.items() if v is not None}

            # Define the action.
            fields = [k.replace('_', ' ') for k, v in content.items() if k not in ['updated_at', 'updated_by']]
            if not fields:
                message = 'Invalid data, no fields were provided.'
                response = Response({'error': True, 'message': message}, status=400)
                response['Access-Control-Allow-Origin'] = '*'
                return response
            elif len(fields) == 1:
                action = f'Edited {doc_id} {fields[0]}.'
            else:
                # Join the fields with commas and 'and' before the last one
                action = f"Edited {doc_id} {', '.join(fields[:-1])} and {fields[-1]}."

            # Save the data to Firestore.
            strain_id = body.get('id', strain_id)
            ref = f'public/data/strains/{strain_id}'
            update_document(ref, content)

        # Return an error if the strain ID is invalid.
        else:
            message = 'Invalid action, expecting: art, description, or name.'
            response = Response({'error': True, 'message': message}, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Record the image and description for known strains.
        # Also save the images and descriptions to galleries.
        if doc_id != content_id:
            ref = f'public/data/strains/{doc_id}'
            if strain_id == 'art':
                image_ref = f'{ref}/images/{content_id}'
                update_document(ref, {'image_url': download_url})
                update_document(image_ref, {
                    'strain_id': doc_id,
                    'image_caption': text + art_style,
                    'image_url': download_url,
                    'updated_at': datetime.now(),
                    'user': uid,
                })
            elif strain_id == 'description':
                description_ref = f'{ref}/descriptions/{content_id}'
                update_document(ref, {'description': content})
                update_document(description_ref, {
                    'strain_id': doc_id,
                    'description': content,
                    'updated_at': datetime.now(),
                    'user': uid,
                })

        # Create a strain log.
        create_log(
            f'public/logs/strain_logs',
            claims=claims,
            action=action,
            log_type='data',
            key=doc_id,
            changes=[content]
        )

        # Create a redundant user log.
        # TODO: Figure out how to make this not necessary?
        create_log(
            f'users/{uid}/public_logs',
            claims=claims,
            action=action,
            log_type='data',
            key='api_data_strains',
            changes=[content]
        )

        # Return the response.
        response = Response({'success': True, 'data': content}, status=200)
        response["Access-Control-Allow-Origin"] = '*'
        return response


# Future work: Allow user's to download all of the lab results
# for a given strain.
