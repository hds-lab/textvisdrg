# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0013_precalccategoricaldistribution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='precalccategoricaldistribution',
            name='dimension_key',
            field=models.CharField(default=b'', max_length=64, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='precalccategoricaldistribution',
            name='level',
            field=msgvis.apps.base.models.Utf8CharField(default=b'', max_length=128, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='precalccategoricaldistribution',
            index_together=set([('dimension_key', 'level')]),
        ),
    ]
