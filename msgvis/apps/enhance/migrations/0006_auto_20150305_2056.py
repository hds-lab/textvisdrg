# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0005_auto_20150303_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=msgvis.apps.base.models.Utf8CharField(max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=msgvis.apps.base.models.Utf8CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='word',
            name='text',
            field=msgvis.apps.base.models.Utf8CharField(max_length=100),
            preserve_default=True,
        ),
    ]
