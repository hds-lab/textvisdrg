# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dimensions', '0004_dimensionkey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dimensionkey',
            name='key',
            field=models.CharField(unique=True, max_length=32),
            preserve_default=True,
        ),
    ]
