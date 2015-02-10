# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0005_auto_20150210_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentiment',
            name='value',
            field=models.SmallIntegerField(default=0, unique=True),
            preserve_default=False,
        ),
    ]
