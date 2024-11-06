from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Splits the value by the argument
    """
    return value.split(arg)