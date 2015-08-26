# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0019_auto_20150331_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='profile_image_url',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
    ]
