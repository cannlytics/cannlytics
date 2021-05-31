from django.template.defaultfilters import register

@register.filter(name='dict_key')
def dict_key(d, k):
    """Returns the given key from a dictionary."""
    value = d.get(k, "")
    if value is None:
        value = ""
    return value
