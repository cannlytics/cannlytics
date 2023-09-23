"""
AI Views | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/6/2023
Updated: 7/2/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: API to interface with AI.
"""
# External imports:
import google.auth
import openai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

# Internal imports:
from cannlytics.auth.auth import authenticate_request
from cannlytics.data import create_hash
from cannlytics.firebase import (
    access_secret_version,
    get_document,
    update_document,
)


# API defaults.
AUTH_ERROR = 'Authentication failed. Please login to Cannlytics\
 (https://console.cannlytics.com) or provide a valid Cannlytics API key\
 in an `Authentication: Bearer <token>` header.'

# OpenAI defaults.
CREATE_TEXT_MODEL = 'text-davinci-003'
MAX_TOKENS = 1_000 # The maximum number of OpenAI tokens per request.
TEMPERATURE = 0

# Firebase defaults.
ID_LENGTH = 16


def initialize_openai():
    """Initialize OpenAI."""
    _, project_id = google.auth.default()
    openai_api_key = access_secret_version(
        project_id=project_id,
        secret_id='OPENAI_API_KEY',
        version_id='latest',
    )
    openai.api_key = openai_api_key


def increment_usage(usage, prompt_ids, response):
    """Increment a user's OpenAI usage and record prompt IDs."""
    try:
        usage += response['usage']['total_tokens']
        prompt_ids.append(response['id'])
    except:
        pass
    return usage, prompt_ids


@api_view(['GET'])
def ai_base(request: Request):
    """Base AI endpoint to help users discover other endpoints."""
    message = "Welcome to Cannlytics AI. You can currently use:\n"
    message += "\n- `/api/ai/recipes`: A cannabis recipe generator."
    message += "\n- `/api/ai/color`: A text-to-color generator."
    message += "\n- `/api/ai/emoji`: A text-to-emoji generator."
    message += "\n\nPlease stay tuned for new AI APIs."
    response = {'success': True, 'message': message, 'data': None}
    return Response(response, status=200)


@api_view(['POST'])
def text_to_color_api(request: Request):
    """Get a hexadecimal code representing given text."""

    # Authenticate the user.
    # Requires the user to pass a `CANNLYTICS_API_KEY`.
    claims = authenticate_request(request)
    if claims is None:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    
    # FIXME: Also allow the user to "GET" a color with a ?q= query parameter.
    
    # Get the parameters.
    uid = claims.get('uid', 'cannlytics.eth')
    data = request.data.get('data', request.data)
    if isinstance(data, str):
        text = data
    else:
        text = data.get('text')

    # Try to get the color from Firestore first.
    text_hash = create_hash(text.strip().lower())
    text_ref = f'public/ai/colors/{text_hash}'
    doc = get_document(text_ref)
    if doc:
        response = {'success': True, 'data': doc['color']}
        return Response(response, status=200)

    # Initialize OpenAI.
    initialize_openai()

    # Format the prompt.
    prompt = 'Best color hex for:'
    prompt += text

    # Ask GPT for a hexadecimal color of given text.
    usage, prompt_ids = 0, []
    print(prompt)
    response = openai.Completion.create(
        model=CREATE_TEXT_MODEL,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=0.5,
        n=1,
        user=uid,
    )
    print(response)
    usage, prompt_ids = increment_usage(usage, prompt_ids, response)

    # Extract any hexadecimal color from the response.
    answer = response['choices'][0]['text'].replace('\n\n', '')
    if '#' in answer:
        code = '#' + answer.split('#')[-1][:6]

        # Save the color to Firestore for quick future retrieval.
        update_document(text_ref, {'color': code, 'text': text})

    # Otherwise no color can be determined.
    else:
        code = '#ffffff'

    # Return the color.
    response = {'success': True, 'data': code}
    return Response(response, status=200)


@api_view(['POST'])
def text_to_emoji_api(request: Request):
    """Get an emoji representing given text."""

    # Authenticate the user.
    # Requires the user to pass a `CANNLYTICS_API_KEY`.
    claims = authenticate_request(request)
    if claims is None:
        return Response({'error': True, 'message': AUTH_ERROR}, status=403)
    
    # FIXME: Also allow the user to "GET" a color with a ?q= query parameter.
    
    # Get the parameters.
    uid = claims.get('uid', 'cannlytics.eth')
    data = request.data.get('data', request.data)
    if isinstance(data, str):
        text = data
    else:
        text = data.get('text')

    # Try to get the emoji from Firestore first.
    text_hash = create_hash(text.strip().lower())
    text_ref = f'public/ai/emojies/{text_hash}'
    doc = get_document(text_ref)
    if doc:
        response = {'success': True, 'data': doc['emoji']}
        return Response(response, status=200)

    # Initialize OpenAI.
    initialize_openai()

    # Format the prompt.
    prompt = 'Best emoji HTML hex for:'
    prompt += text

    # Ask GPT for an emoji representation of given text.
    usage, prompt_ids = 0, []
    print(prompt)
    response = openai.Completion.create(
        model=CREATE_TEXT_MODEL,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=0.5,
        n=1,
        user=uid,
    )
    print(response)
    usage, prompt_ids = increment_usage(usage, prompt_ids, response)

    # Extract any emoji from the response.
    answer = response['choices'][0]['text'].replace('\n\n', '')
    if '&#' in answer:
        emoji = answer.split('&#')[-1].split(';')[0]
        emoji = f'&#{emoji};'

        # Save the emoji to Firestore for quick future retrieval.
        update_document(text_ref, {'emoji': emoji, 'text': text})

    # Otherwise no emoji can be determined.
    else:
        emoji = '&#127807;' # A herb emoji.

    # Return the color.
    response = {'success': True, 'data': emoji}
    return Response(response, status=200)
