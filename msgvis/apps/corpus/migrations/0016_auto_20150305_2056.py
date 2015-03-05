# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0015_auto_20150303_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='text',
            field=msgvis.apps.base.models.Utf8CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=msgvis.apps.base.models.Utf8TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='full_name',
            field=msgvis.apps.base.models.Utf8CharField(default=None, max_length=250, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='username',
            field=msgvis.apps.base.models.Utf8CharField(default=None, max_length=150, null=True, blank=True),
            preserve_default=True,
        ),
    ]
