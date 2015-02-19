from django.contrib import admin

# Register your models here.

from msgvis.apps.enhance import models
admin.site.register(models.Dictionary)
admin.site.register(models.Word)
admin.site.register(models.TopicModel)
admin.site.register(models.Topic)
admin.site.register(models.TopicWord)
admin.site.register(models.TweetWord)
admin.site.register(models.TweetTopic)