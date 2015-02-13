# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0008_message_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='message_count',
            field=models.PositiveIntegerField(default=0, blank=True),
            preserve_default=True,
        ),
    ]
