from django.conf.urls import url

from msgvis.apps.api import views

api_root_urls = {
    'data-tables': url(r'^table/$', views.DataTableView.as_view(), name='data-table'),
    'example-messages': url(r'^message/$', views.ExampleMessagesView.as_view(), name='example-messages'),
    'research-questions': url(r'^questions/$', views.ResearchQuestionsView.as_view(), name='research-questions'),
    'dimension-distributions': url(r'^dimension/$', views.DimensionDistributionView.as_view(),
                                   name='dimension-distribution'),
    'filter-summaries': url(r'^filter/$', views.FilterSummaryView.as_view(), name='filter-summary'),
}

urlpatterns = api_root_urls.values() + [
    url(r'^$', views.APIRoot.as_view(root_urls=api_root_urls)),
]
