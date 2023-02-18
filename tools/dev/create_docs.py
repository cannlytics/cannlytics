"""
Create Documentation Tool | Cannlytics
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/12/2022
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Command-line usage:

    python tools/material/cartoonize_image.py img.png cartoon.png

"""
# Standard imports:
import inspect
import re

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.utils.utils import *


def is_relevant(obj):
    """Filter out non user defined functions/classes."""
    if hasattr(obj, '__name__') and obj.__name__ == 'type':
        return False
    if inspect.isfunction(obj) or inspect.isclass(obj) or inspect.ismethod(obj):
        return True


def get_docstring_data(name, doc):
    """Get docstring data and return it in a dictionary."""
    docstring = {'function': f'`{name}`'}
    regex = r'^(.*?)(?:Args:(.*?))?(Returns:(.*))?$'
    parts = re.search(regex, doc, re.DOTALL).groups()
    description, args, returns = parts[:3]
    docstring['description'] = description.replace('\n', ' ').strip()
    docstring['args'] = args.replace('\n', '').strip() if args else ''
    docstring['returns'] = returns.replace('Returns:\n', '').strip() if returns else ''
    return docstring


def get_docstrings(module, default=''):
    """Get docstrings from a given Python module."""

    def get_doc(obj):
        doc = inspect.getdoc(obj)
        return default if doc is None else doc
    
    docstrings = []
    for name, obj in inspect.getmembers(module, is_relevant):
        docstring = get_docstring_data(name, get_doc(obj))
        docstrings.append(docstring)
        if inspect.isclass(obj):
            docstrings.extend(
                get_docstring_data(name, get_doc(sub_obj))
                for name, sub_obj in inspect.getmembers(obj, is_relevant)
            )
    return docstrings


def format_documentation(module):
    """Format documentation for a given module."""
    rows = get_docstrings(module)
    data = pd.DataFrame(rows)
    data.rename(columns=lambda x: x.title(), inplace=True)
    return data.to_html(index=False, render_links=True, escape=False)


def save_documentation_table(table, outfile):
    """Save SDK documentation."""
    f = open(outfile, 'r')
    text = f.read()
    beginning = text.split('<table')[0]
    end = text.split('</table>')[-1]
    updated_doc = ''.join([beginning, table, end])
    f.close()
    f = open(outfile, 'w+')
    f.write(updated_doc)
    f.close()


# === Test ===
if __name__ == '__main__':

    # Save Firebase SDK references.
    from cannlytics import firebase
    table = format_documentation(firebase)
    save_documentation_table(table, './docs/sdk/firebase.md')

    # Save Metrc SDK references.
    from cannlytics.metrc.client import Metrc
    table = format_documentation(Metrc)
    save_documentation_table(table, './docs/sdk/metrc.md')

    # Save utility SDK references.
    from cannlytics import utils
    table = format_documentation(utils)
    save_documentation_table(table, './docs/sdk/utils.md')
