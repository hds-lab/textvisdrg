from django.contrib import admin

from msgvis.apps.corpus import models
admin.site.register(models.Dataset)
admin.site.register(models.Language)
admin.site.register(models.MessageType)
admin.site.register(models.Sentiment)
admin.site.register(models.Timezone)
