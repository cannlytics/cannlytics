"""
Strain Data Endpoints | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2023
Updated: 7/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API endpoints to interface with strain data.
"""
# Standard imports.
from datetime import datetime
from json import loads
import os
import tempfile

# External imports
import google.auth
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Internal imports
from cannlytics.auth.auth import authenticate_request
from cannlytics.data.strains.strains_ai import (
    generate_strain_art,
    generate_strain_description,
    identify_strains,
)
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    get_document,
    get_file_url,
    update_document,
    upload_file,
)
from website.settings import STORAGE_BUCKET


@api_view(['GET', 'POST'])
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
            response = {'success': True, 'data': data}
            return Response(response, status=200)

        # TODO: Query strains.
        print('Throttle queries:', throttle)

    # Create or update strain data.
    elif request.method == 'POST':
        # Get strain data from request
        body = request.data
        text = body.get('text')
        if not text:
            message = 'No text provided.'
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
        
        # Create a unique ID for the generation.
        content_id = datetime.now().strftime('%Y%m%d%H%M%S')
        doc_id = body.get('id', content_id)
        print('Edit to:', doc_id)

        # Generate a description.
        model = body.get('model', base_model)
        temperature = body.get('temperature', 0.042)
        word_count = body.get('word_count', 60)
        stats = body.get('stats', {})
        try:
            stats = loads(stats)
        except:
            pass
        if strain_id == 'description':
            content = generate_strain_description(
                text,
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
            art_style = body.get('style', ' in the style of pixel art')
            size = body.get('size', '1024x1024')
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
            content = get_file_url(
                ref=destination_blob_name,
                bucket_name=STORAGE_BUCKET,
            )

        # Identify strain names.
        elif strain_id == 'name':
            content = identify_strains(text)

        # Return an error if the strain ID is invalid.
        else:
            message = 'Invalid action, expecting: art, description, or name.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)
        
        # TODO: Allow the user to save edits to strains.

        # Record the image and description for known strains.
        # Also save the images and descriptions to galleries.
        if doc_id != content_id:
            ref = f'public/data/strains/{doc_id}'
            if strain_id == 'art':
                image_ref = f'{ref}/images/{content_id}'
                update_document(ref, {'image_url': content})
                update_document(image_ref, {
                    'strain_id': doc_id,
                    'image_url': content,
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
            f'public/data/strains/{doc_id}/strain_logs',
            claims=claims,
            action='Edited strain %s' % doc_id,
            log_type='data',
            key='api_data_strains',
            changes=[content]
        )

        response = {'success': True, 'data': content}
        return Response(response, status=200)


# Future work: Allow user's to download all of the lab results
# for a given strain.
