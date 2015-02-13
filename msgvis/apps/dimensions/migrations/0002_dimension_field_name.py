# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def map_field_names(apps, schema_editor):
    Dimension = apps.get_model("dimensions", "Dimension")
    for dim in Dimension.objects.filter(field_name=None):
        dim.field_name = dim.slug
        dim.save()


class Migration(migrations.Migration):
    dependencies = [
        ('dimensions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dimension',
            name='field_name',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.RunPython(map_field_names),
    ]
