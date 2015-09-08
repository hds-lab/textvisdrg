# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0014_auto_20150902_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetword',
            name='original_text',
            field=msgvis.apps.base.models.Utf8CharField(default=b'', max_length=100, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tweetword',
            name='pos',
            field=models.CharField(default=b'', max_length=4, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tweetword',
            name='text',
            field=msgvis.apps.base.models.Utf8CharField(default=b'', max_length=100, db_index=True, blank=True),
            preserve_default=True,
        ),
    ]
