# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0019_auto_20150331_2129'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='messages',
            field=models.ManyToManyField(default=None, related_name='groups', null=True, to='corpus.Message', blank=True),
            preserve_default=True,
        ),
    ]
