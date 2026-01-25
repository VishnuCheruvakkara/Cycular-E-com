from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Safely get an item from a dict.
    If input is not a dict or key does not exist, return empty dict.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})  # Return empty dict if key not found
    return {}  # Return empty dict if input is not a dict
