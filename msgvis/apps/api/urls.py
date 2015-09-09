from django.conf.urls import url

from msgvis.apps.api import views
from django.views.decorators.csrf import csrf_exempt

api_root_urls = {
    'data-tables': url(r'^table/$', views.DataTableView.as_view(), name='data-table'),
    'example-messages': url(r'^message/$', views.ExampleMessagesView.as_view(), name='example-messages'),
    'keyword-messages': url(r'^search/$', views.KeywordMessagesView.as_view(), name='keyword-messages'),
    'keyword': url(r'^keyword/$', views.KeywordView.as_view(), name='keyword'),
    'group': url(r'^group/$', csrf_exempt(views.GroupView.as_view()), name='group'),
    'research-questions': url(r'^questions/$', views.ResearchQuestionsView.as_view(), name='research-questions'),
    'action-history': url(r'^history/$', views.ActionHistoryView.as_view(), name='action-history'),
}

urlpatterns = api_root_urls.values() + [
    url(r'^$', views.APIRoot.as_view(root_urls=api_root_urls)),
]
