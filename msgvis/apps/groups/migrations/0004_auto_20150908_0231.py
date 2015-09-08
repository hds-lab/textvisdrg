# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_auto_20150825_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='exclusive_keywords',
        ),
        migrations.RemoveField(
            model_name='group',
            name='inclusive_keywords',
        ),
        migrations.AddField(
            model_name='group',
            name='deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='keywords',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
