# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0003_auto_20150210_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='code',
            field=models.SlugField(unique=True, max_length=10),
            preserve_default=True,
        ),
    ]
