# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetopic',
            name='source',
            field=models.ForeignKey(to='corpus.Message'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messagetopic',
            name='topic_model',
            field=models.ForeignKey(to='enhance.TopicModel'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messageword',
            name='dictionary',
            field=models.ForeignKey(to='enhance.Dictionary'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messageword',
            name='source',
            field=models.ForeignKey(to='corpus.Message'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topicword',
            name='topic',
            field=models.ForeignKey(to='enhance.Topic'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='messagetopic',
            index_together=set([]),
        ),
        migrations.AlterIndexTogether(
            name='messageword',
            index_together=set([]),
        ),
    ]
