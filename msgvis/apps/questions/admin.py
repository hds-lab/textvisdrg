from django.contrib import admin

# Register your models here.
from msgvis.apps.questions import models
admin.site.register(models.Article)
admin.site.register(models.Question)
