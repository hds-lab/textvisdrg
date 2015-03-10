# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0016_auto_20150305_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='text',
            field=msgvis.apps.base.models.Utf8CharField(max_length=100, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timezone',
            name='name',
            field=models.CharField(max_length=150, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='message',
            index_together=set([('dataset', 'original_id')]),
        ),
        migrations.AlterIndexTogether(
            name='person',
            index_together=set([('dataset', 'original_id')]),
        ),
    ]
