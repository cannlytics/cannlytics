"""
Utility Functions | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/5/2021
Updated: 1/5/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# Standard imports.
from random import randint
import traceback
from typing import Optional

# External imports.
import requests
from markdown import markdown
from pymdownx import emoji

# Internal imports.
from website.settings import DEBUG

# Optional: Style blockquotes
# https://facelessuser.github.io/pymdown-extensions/extensions/emoji/

EXTENSIONS = [
    'admonition',
    'attr_list',
    'def_list',
    'codehilite',
    'fenced_code',
    'nl2br',
    'smarty',
    'tables',
    'mdx_math',
    'pymdownx.arithmatex',
    'pymdownx.emoji',
]

EXTENSION_CONFIGS = {
    'pymdownx.emoji': {
        'emoji_index': emoji.gemoji,
        'emoji_generator': emoji.to_png,
        'alt': 'html_entity',
        'options': {
            'image_path': 'https://github.com/images/icons/emoji/unicode/',
            'non_standard_image_path': 'https://github.com/images/icons/emoji/unicode/'
        }
    }
}


def get_markdown(
        request,
        context,
        app,
        page=None,
        extensions=None,
        name='markdown',
):
    """Try loading markdown material into a given context.
    Args:
        request (HttpRequest): An HTTP request.
        context (dict): A dictionary of page context.
        app (str): The project name.
        page (str): The page name for locating page-specific markdown.
        extensions (list): A list of extensions, a pre-selected list
            of useful extensions is used by default.
        name (str): The context namespace, `markdown` by default.
    Returns
        (dict): Returns the context updated with any markdown.    
    """
    if extensions is None:
        extensions = EXTENSIONS
    if page is None:
        page = context['page']
    try:
        # Optional: Open markdown file directly instead of with a request.
        try:
            base = request.META.get('HTTP_REFERER').split('/')[2]
        except AttributeError:
            base = 'cannlytics.com'
        protocol = 'http' if DEBUG else 'https'
        url = f'{protocol}://{base}/static/{app}/docs/{page}.md'
        text = requests.get(url).text
        context[name] = markdown(
            text,
            extensions=extensions,
            extension_config=EXTENSION_CONFIGS
        )
        # Optional: Add copy code button
        # text = add_code_copy(text)
    except:
        traceback.print_exc()
        context[name] = "<h1>Error loading page material.</h1> \
        <p>Our apologies, our server encountered a yet-to-be-fixed bug. \
        Please notify <a href='mailto:contact@cannlytics.com'>contact@cannlytics.com</a> \
        and we will be quick to provide you with support.</p>"
    return context



# Optional: Add a copy button to code blocks | https://programmersought.com/article/48614916658/
# def add_code_copy(text):
#     """Add copy button to code blocks.
#     Args:
#         text (str): A block of HTML text.
#     Returns
#         (str): Returns the HTML text with copy buttons inserted.
#     """
#     n = text.count('<div class="codehilite">', 0, len(text))
#     print('Codeblocks:', n)
#     for i in range(n):
#         text = re.sub(r'<div class="codehilite">',
#         '&nbsp;&nbsp;<button id="codecopy-{}" style="float: right;z-index:10" class="copybtn" '
#         'data-clipboard-action="copy" '
#         'data-clipboard-target="#code{}">Copy</button> '
#         '<div class="codehilite" id="code{}">'.format(i, i, i), text, 1)
#     return text


def get_promo_code(num_chars: Optional[int] = 7) -> str:
    """Generate a random promotion code.
    Args:
        num_chars (int): The number of digits for the promotion code, 7 by default.
    Returns:
        (str): A random code that can be use for promotions.
    """
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for _ in range(num_chars):
        slice_start = randint(0, len(code_chars) - 1)
        code += code_chars[slice_start: slice_start + 1]
    return code.lower()
