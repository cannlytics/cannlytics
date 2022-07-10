"""
Render an article.

URL: <https://github.com/cbernet/jupyter_web>
"""
# Standard imports.
import os

# External imports.
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter


# TODO: This should be dynamic.
# Specify the input and output files.
input_file = 'main.html'
output_file = 'index.html'

# Create a formatter.
html_formatter = HtmlFormatter()

# Specify where jinja2 should look for templates.
env = Environment(loader=FileSystemLoader('templates'))

# Read and render the template.
template = env.get_template(input_file)
rendered = template.render()

# Replace the pre tags with highlighted code.
soup = BeautifulSoup(rendered, 'html.parser')
for pre in soup.find_all('pre'):
    if pre.parent.name == 'div': 
        class_name = pre.parent.get('class')
        condition = ('highlight' in class_name or 'output_text' in class_name)
        if class_name and condition:
            continue

    # Highlight with pygments and replace the tag with formatted code.
    lexer = guess_lexer(pre.string)
    code = highlight(pre.string.rstrip(), lexer, html_formatter)
    new_tag = pre.replace_with(code)
    
# Format the final html string, preserving the syntax.
rendered = soup.prettify(formatter=None)

# Save the rendered HTML file.
with open(output_file, 'w') as outfile:
    outfile.write(rendered)
