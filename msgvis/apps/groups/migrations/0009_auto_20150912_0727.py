# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0008_auto_20150909_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_search_record',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='actionhistory',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 12, 7, 27, 51, 592626, tzinfo=utc), db_index=True),
            preserve_default=True,
        ),
    ]
