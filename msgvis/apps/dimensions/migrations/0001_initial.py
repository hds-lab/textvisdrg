# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dimension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('scope', models.CharField(max_length=1, choices=[(b'O', b'Open-ended'), (b'C', b'Closed-ended')])),
                ('type', models.CharField(max_length=1, choices=[(b'Q', b'Quantitative'), (b'C', b'Categorical')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
