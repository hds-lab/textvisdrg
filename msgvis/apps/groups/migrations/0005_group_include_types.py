# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0020_person_profile_image_url'),
        ('groups', '0004_auto_20150908_0231'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='include_types',
            field=models.ManyToManyField(default=None, to='corpus.MessageType', null=True, blank=True),
            preserve_default=True,
        ),
    ]
