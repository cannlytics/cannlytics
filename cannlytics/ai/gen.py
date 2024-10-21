"""
AI Generation
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/20/2024
Updated: 10/20/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# External imports:
from openai import OpenAI

# Internal imports:
from cannlytics.data import create_hash
from cannlytics.firebase import (
    initialize_firebase,
    get_document,
    update_document,
)


def text_to_color_ai(
        text,
        client=None,
        db=None,
        model='gpt-4o-mini',
        default_color='#aaa',
        verbose=True,
        user_prompt=None,
        system_prompt=None,
        max_tokens=None,
        temperature=None,
    ) -> str:
    """Get a hexadecimal code representing given text."""

    # Try to get the color from Firestore first.
    if db is None:
        db = initialize_firebase()
    text_hash = create_hash(text.strip().lower())
    text_ref = f'public/ai/colors/{text_hash}'
    doc = get_document(text_ref, database=db)
    if doc:
        return doc['color']

    # Format the prompt.
    if system_prompt is None:
        system_prompt = 'Given text, return only an HTML hex color code that best represents the text.'
    if user_prompt is None:
        user_prompt = 'Best color hex for: '
    user_prompt += text

    # Ask GPT for a hexadecimal color of given text.
    if client is None:
        client = OpenAI()
    if verbose:
        print('PROMPT:', user_prompt)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    generated_text = completion.choices[0].message.content
    usage = completion.usage.to_dict()
    if verbose:
        print('RESPONSE:', generated_text)
        print('USAGE:', usage)

    # Extract and save any hexadecimal color from the response.
    answer = generated_text.replace('\n\n', '')
    if '#' in answer:
        code = '#' + answer.split('#')[-1][:6]
        update_document(text_ref, {'color': code, 'text': text}, database=db)
    else:
        code = default_color
    return code, usage
