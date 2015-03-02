# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dimensions', '0004_dimensionkey'),
        ('questions', '0003_auto_20150216_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='dimensions',
            field=models.ManyToManyField(to='dimensions.DimensionKey'),
            preserve_default=True,
        ),
    ]
