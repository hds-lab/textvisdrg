from django.conf.urls import url

from msgvis.apps.api import views

api_root_urls = {
    'data-tables': url(r'^table/$', views.DataTableView.as_view(), name='data-table'),
    'example-messages': url(r'^message/$', views.ExampleMessagesView.as_view(), name='example-messages'),
    'research-questions': url(r'^questions/$', views.ResearchQuestionsView.as_view(), name='research-questions'),
}

urlpatterns = api_root_urls.values() + [
    url(r'^$', views.APIRoot.as_view(root_urls=api_root_urls)),
]
