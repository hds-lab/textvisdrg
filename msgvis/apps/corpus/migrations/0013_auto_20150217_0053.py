# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0012_auto_20150214_0422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='sentiment',
            field=models.SmallIntegerField(default=None, null=True, blank=True, choices=[(1, b'positive'), (0, b'neutral'), (-1, b'negative')]),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='Sentiment',
        ),
    ]
