import os
from django import template

register = template.Library()

@register.filter
def get_env(key):
    """Get a variable from the .env file."""
    return os.environ.get(key, None)
