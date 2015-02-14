# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0010_auto_20150213_0850'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='replied_to_count',
            field=models.PositiveIntegerField(default=0, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='shared_count',
            field=models.PositiveIntegerField(default=0, blank=True),
            preserve_default=True,
        ),
    ]
