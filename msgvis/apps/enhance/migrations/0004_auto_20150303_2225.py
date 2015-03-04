# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0015_auto_20150303_0343'),
        ('enhance', '0003_auto_20150303_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='messages',
            field=models.ManyToManyField(related_name='topics', through='enhance.MessageTopic', to='corpus.Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='words',
            field=models.ManyToManyField(related_name='topics', through='enhance.TopicWord', to='enhance.Word'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='word',
            name='messages',
            field=models.ManyToManyField(related_name='words', through='enhance.MessageWord', to='corpus.Message'),
            preserve_default=True,
        ),
    ]
