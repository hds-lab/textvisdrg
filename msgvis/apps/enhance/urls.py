from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.TopicModelIndexView.as_view(), name='topics_models'),
    url(r'^model/(?P<model_id>\d+)/$', views.TopicModelDetailView.as_view(), name='topics_model'),
    url(r'^model/(?P<model_id>\d+)/topic/(?P<topic_id>\d+)/$', views.TopicDetailView.as_view(), name='topics_topic'),
    url(r'^model/(?P<model_id>\d+)/topic/(?P<topic_id>\d+)/word/(?P<word_id>\d+)/$', views.TopicWordDetailView.as_view(),
        name='topics_topic_word'),
)
