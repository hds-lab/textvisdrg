import re

from django import template
register = template.Library()

@register.simple_tag
def active(request, pattern):
    """
    Checks the current request to see if it matches a pattern.
    If so, it returns 'active'.

    To use, add this to your Django template:

    .. code-block:: html

        {% load tags %}
        <li class="{% active request home %}"><a href="/">Home</a></li>

    """
    if re.search(pattern, request.path):
        return 'active'
    return ''
