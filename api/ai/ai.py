"""
AI Views | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/6/2023
Updated: 2/6/2023
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
from cannlytics.firebase import (
    access_secret_version,
)

# API defaults.
AUTH_ERROR = 'Authentication failed. Please login to Cannlytics\
 (https://console.cannlytics.com) or provide a valid Cannlytics API key\
 in an `Authentication: Bearer <token>` header.'

# OpenAI defaults.
CREATE_TEXT_MODEL = 'text-davinci-003'
MAX_TOKENS = 1_000 # The maximum number of OpenAI tokens per request.
TEMPERATURE = 0


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

    message = """Welcome to Cannlytics AI. You can currently use:
   
        - `/api/ai/recipes`: A cannabis recipes generator.
        - `/api/ai/color`: A text-to-color generator.
        - `/api/ai/emoji`: A text-to-emoji generator.
    
    Please stay tuned for new AI APIs.
    """
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
    
    # Get the parameters.
    uid = claims['uid']
    data = request.data.get('data', request.data)
    if isinstance(data, str):
        text = data
    else:
        text = data.get('text')

    # Initialize OpenAI.
    initialize_openai()

    # Format the prompt.
    prompt = 'Color hex:'
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
    
    # Get the parameters.
    uid = claims['uid']
    data = request.data.get('data', request.data)
    if isinstance(data, str):
        text = data
    else:
        text = data.get('text')

    # Initialize OpenAI.
    initialize_openai()

    # Format the prompt.
    prompt = 'Emoji HTML hex for:'
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
    else:
        emoji = '&#127807;' # A herb emoji.

    # Optional: Handle other emoji formats.
    # answer = response['choices'][0]['text'].replace('\n\n', '')
    # try:
    #     emoji = answer.encode('unicode-escape').split(b'\\')[-1].decode('unicode-escape')
    # except:
    #     emoji = answer.encode('unicode-escape')
    # print(emoji)

    # Return the color.
    response = {'success': True, 'data': emoji}
    return Response(response, status=200)
