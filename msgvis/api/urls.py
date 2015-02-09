from django.conf.urls import url
from django.core.urlresolvers import NoReverseMatch
from rest_framework.reverse import reverse

from rest_framework.routers import Response
from rest_framework.compat import get_resolver_match, OrderedDict

from msgvis.api import views


api_root_urls = {
    'data-tables': url(r'^table/$', views.DataTableView.as_view(), name='data-table'),
    'example-messages': url(r'^message/$', views.ExampleMessagesView.as_view(), name='example-messages'),
    'research-questions': url(r'^questions/$', views.ResearchQuestionsView.as_view(), name='research-questions'),
    'dimension-distributions': url(r'^dimension/$', views.DimensionDistributionView.as_view(),
                                   name='dimension-distribution'),
    'filter-summaries': url(r'^filter/$', views.FilterSummaryView.as_view(), name='filter-summary'),
}


class APIRoot(views.APIView):
    """
    The Text Visualization DRG API.

    Refer to the full documentation [here](https://github.com/hds-lab/textvisdrg/blob/master/docs/API.md).
    """

    def get(self, request, *args, **kwargs):
        ret = OrderedDict()
        namespace = get_resolver_match(request).namespace
        for key, urlconf in api_root_urls.iteritems():
            url_name = urlconf.name
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                ret[key] = reverse(
                    url_name,
                    request=request,
                    format=kwargs.get('format', None)
                )
                print ret[key]
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue

        return Response(ret)


urlpatterns = api_root_urls.values() + [
    url(r'^$', APIRoot.as_view()),
]
