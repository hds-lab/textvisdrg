# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0010_auto_20150213_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timezone',
            name='olson_code',
            field=models.CharField(default=None, max_length=40, null=True, blank=True),
            preserve_default=True,
        ),
    ]
