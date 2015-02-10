from django.conf import settings


def google_analytics(request):
    """
    Adds a ``GOOGLE_ANALYTICS_ID`` variable to the template
    context.

    Add this to your Django settings:

    ::

        GOOGLE_ANALYTICS_ID = 'UA-XXXXXX-X'

        TEMPLATE_CONTEXT_PROCESSORS += (
            'msgvis.apps.base.context_processors.google_analytics',
        )

    """
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', False)
    if not settings.DEBUG and ga_prop_id:
        return {
            'GOOGLE_ANALYTICS_ID': ga_prop_id,
        }
    return {}
