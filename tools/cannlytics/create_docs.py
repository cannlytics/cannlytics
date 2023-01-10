"""
Create Documentation Tool | Cannlytics
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/12/2022
Updated: 1/10/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
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
    docstring['description'] = description.strip()
    docstring['args'] = args.strip() if args else ''
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


# Save Metrc API reference.
from cannlytics.metrc.client import Metrc
rows = get_docstrings(Metrc)
data = pd.DataFrame(rows)
data.rename(columns=lambda x: x.title(), inplace=True)
table = data.to_html(index=False, render_links=True, escape=False)

outfile = './docs/sdk/metrc.md'
with open(outfile, 'r') as f:
    text = f.readlines()
    readme = ''.join([line for line in text])
    beginning = readme.split('<table')[0]
    end = readme.split('</table>')[-1]
    updated_doc = ''.join([beginning, table, end])
    f.close()


# Create table of `utils` functions.
# filename = '../../cannlytics/utils/utils.py'

# # FIXME: Read all doc strings and arguments.
# rows = []


# # Create the title.
# title = '# Cannlytics Utility Functions'

# from cannlytics.metrc import client

# # Get the heading.
# heading = client.__doc__

# Create the markdown table.


# Save the markdown table.
# with open(doc, 'r') as f:
    # text = f.readlines()
    # readme = ''.join([line for line in text])
    # beginning = readme.split('<table')[0]
    # end = readme.split('</table>')[-1]
    # updated_doc = ''.join([beginning, table, end])

# Save the documentation.
# doc = '../../cannlytics/utils/readme.md'
# with open(doc, 'w') as f:
#     markdown = '\n'.join([title, heading, table])
#     f.write(markdown)
