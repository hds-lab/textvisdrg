# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0002_auto_20150303_2223'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagetopic',
            old_name='source',
            new_name='message',
        ),
        migrations.RenameField(
            model_name='messageword',
            old_name='source',
            new_name='message',
        ),
        migrations.AlterField(
            model_name='messagetopic',
            name='topic_model',
            field=models.ForeignKey(to='enhance.TopicModel', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messageword',
            name='dictionary',
            field=models.ForeignKey(to='enhance.Dictionary', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='messagetopic',
            index_together=set([('topic_model', 'message')]),
        ),
        migrations.AlterIndexTogether(
            name='messageword',
            index_together=set([('dictionary', 'message')]),
        ),
    ]
