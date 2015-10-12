# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0009_auto_20150912_0727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionhistory',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
            preserve_default=True,
        ),
    ]
