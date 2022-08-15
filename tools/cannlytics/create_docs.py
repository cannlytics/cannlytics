"""
Repository Management Tools | Cannabis Data Science
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/12/2022
Updated: 7/12/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# External imports.
import pandas as pd

# Internal imports.
from cannlytics.utils.utils import *

# Create table of `utils` functions.
filename = '../../cannlytics/utils/utils.py'
doc = '../../cannlytics/utils/readme.md'

# TODO: Read all doc strings and arguments.
rows = []

rows.append({
    'Function': '',
    'Description': '',
    'Arguments': '',
    'Returns': '',
})

# Create the title.
title = '# Cannlytics Utility Functions'

from cannlytics.metrc import client

# Get the heading.
heading = client.__doc__

# Create the markdown table.
data = pd.DataFrame(rows)
table = data.to_html(index=False, render_links=True, escape=False)

# Save the markdown table.
# with open(doc, 'r') as f:
    # text = f.readlines()
    # readme = ''.join([line for line in text])
    # beginning = readme.split('<table')[0]
    # end = readme.split('</table>')[-1]
    # updated_doc = ''.join([beginning, table, end])
with open(doc, 'w') as f:
    markdown = '\n'.join([title, heading, table])
    f.write(markdown)
