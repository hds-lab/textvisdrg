# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0007_actionhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionhistory',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 9, 8, 35, 23, 817509, tzinfo=utc), db_index=True),
            preserve_default=True,
        ),
    ]
