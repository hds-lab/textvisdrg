"""
Getting Django Rest Framework to parse docstrings as reStructuredText

http://vxlabs.com/2014/11/12/getting-django-rest-framework-to-parse-docstrings-as-restructuredtext/
"""
from django.utils.safestring import mark_safe
from docutils import core
from rest_framework.compat import force_bytes_or_smart_bytes
from rest_framework.utils import formatting

def get_view_description(view_cls, html=False):
    """
    Alternative view description function to be used as the DRF
    ``VIEW_DESCRIPTION_FUNCTION`` so that RestructuredText can be used
    instead of the DRF-default MarkDown.
 
    Except for the RST parts, derived by cpbotha@vxlabs.com from the
    DRF default get_view_description function.
    """

    description = view_cls.__doc__ or ''
    description = formatting.dedent(force_bytes_or_smart_bytes(description))
    if html:
        # from https://wiki.python.org/moin/ReStructuredText -- we use the
        # third recipe to get just the HTML parts corresponding to the ReST
        # docstring:
        parts = core.publish_parts(source=description, writer_name='html')
        html = parts['body_pre_docinfo']+parts['fragment']
        # have to use mark_safe so our HTML will get explicitly marked as
        # safe and will be correctly rendered
        return mark_safe(html)

    return description
