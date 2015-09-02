# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0020_person_profile_image_url'),
        ('enhance', '0012_tweetword'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrecalcCategoricalDistribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dimension_key', models.CharField(default=b'', max_length=64, blank=True)),
                ('level', msgvis.apps.base.models.Utf8CharField(default=b'', max_length=256, blank=True)),
                ('count', models.IntegerField()),
                ('dataset', models.ForeignKey(related_name='distributions', default=None, blank=True, to='corpus.Dataset', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
