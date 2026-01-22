from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by arg"""
    return float(value) * float(arg)
