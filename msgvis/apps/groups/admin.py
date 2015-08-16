from django.contrib import admin

# Register your models here.
from msgvis.apps.groups import models
admin.site.register(models.Group)
