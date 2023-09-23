"""
Strain Name Generation | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 4/12/2023
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import os
import secrets
import tempfile
from typing import List

# External imports:
import google.auth
from google.cloud.firestore import Increment
import openai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

# Internal imports:
from api.ai.api_ai import (
    initialize_openai,
    increment_usage,
    AUTH_ERROR,
    CREATE_TEXT_MODEL,
    ID_LENGTH,
    MAX_TOKENS,
    TEMPERATURE,
)
from cannlytics.auth.auth import authenticate_request
from cannlytics.firebase import (
    access_secret_version,
    create_log,
    delete_document,
    delete_file,
    download_file,
    get_document,
    get_collection,
    get_file_url,
    update_document,
    update_documents,
    upload_file,
)
from cannlytics.utils import convert_to_numeric, download_file_from_url


def create_strain_name(uid, data) -> List[str]:
    """Create AI-generated strain names."""

    # Initialize a blank strain name.
    usage, prompt_ids = 0, []
    strain_id = secrets.token_hex(ID_LENGTH)
    ref = f'users/{uid}/strain_names/{strain_id}'

    # TODO: Get user's parameters.
    temperature = data.get('creativity', TEMPERATURE)

    # TODO: Engineer prompt.
    prompt = ''

    # Ask GPT for a strain name.
    initialize_openai()
    try:
        print(prompt)
        response = openai.Completion.create(
            prompt=prompt,
            model=CREATE_TEXT_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            n=1,
            user=uid,
        )
        print(response)
        usage, prompt_ids = increment_usage(usage, prompt_ids, response)
        generation = response['choices'][0]['text']
    except:
        message = 'Failed to generate a recipe.'
        return message, None, None

    # TODO: Clean-up the generated text as needed.
    
    # Record usage and prompt IDs for administrators to review.
    try:
        doc_id = secrets.token_hex(ID_LENGTH)
        ref = f'admin/ai/strain_names/{doc_id}'
        doc = {'usage': usage, 'prompt_ids': prompt_ids}
        update_document(ref, doc)
    except:
        print("Couldn't save admin document.")

    # Return the generated text.
    return generation


@api_view(['GET', 'POST'])
def strain_names_api(request: Request, strain_id=None):
    """AI-generated strain names."""

    # Authenticate the user from a `CANNLYTICS_API_KEY`.
    claims = authenticate_request(request)
    if claims is None:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)

    # Get the parameters.
    uid = claims['uid']
    params = request.query_params
    data = request.data.get('data', request.data)

    # Get strain name(s).
    if request.method == 'GET':

        # TODO: Get random strain names.
        names = create_strain_name(uid, {})
        response = {'success': True, 'data': names}
        return Response(response, status=200)

    # Create strain name(s).
    elif request.method == 'POST':

        # TODO: Generate strain names based on user's input.
        names = create_strain_name(uid, data)

        # Create an activity log.
        try:
            create_log(
                ref='logs/ai/strain_names',
                claims=claims,
                action='create_strain_names',
                log_type='strain_names',
                key=strain_id,
                changes=names
            )
        except:
            print('Failed to log activity.')

        # Return the entered data.
        response = {'success': True, 'data': names}
        return Response(response, status=200)
