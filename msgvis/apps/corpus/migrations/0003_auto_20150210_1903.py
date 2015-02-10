# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_auto_20150210_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='full_name',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='username',
            field=models.CharField(default=None, max_length=150, null=True, blank=True),
            preserve_default=True,
        ),
    ]
