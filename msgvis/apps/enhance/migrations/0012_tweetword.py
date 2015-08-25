# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.base.models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0019_auto_20150331_2129'),
        ('enhance', '0011_dictionary_dataset'),
    ]

    operations = [
        migrations.CreateModel(
            name='TweetWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', msgvis.apps.base.models.Utf8CharField(max_length=100)),
                ('dataset', models.ForeignKey(related_name='tweet_words', default=None, blank=True, to='corpus.Dataset', null=True)),
                ('messages', models.ManyToManyField(related_name='tweet_words', to='corpus.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
