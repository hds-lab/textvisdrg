from django.contrib import admin

from msgvis.apps.corpus import models
admin.site.register(models.Dataset)
admin.site.register(models.Language)
admin.site.register(models.MessageType)
admin.site.register(models.Timezone)

admin.site.register(models.Person)
admin.site.register(models.Message)
admin.site.register(models.Hashtag)
admin.site.register(models.Media)
admin.site.register(models.Url)
admin.site.register(models.Topic)
