# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dimensions', '0005_auto_20150227_2303'),
        ('questions', '0005_auto_20150302_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='dimensions',
            field=models.ManyToManyField(to='dimensions.DimensionKey', through='questions.QuestionDimensionConnection'),
            preserve_default=True,
        ),
    ]
