from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get a value from a dictionary by key"""
    return d.get(key)
