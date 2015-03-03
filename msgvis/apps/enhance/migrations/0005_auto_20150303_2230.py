# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0004_auto_20150303_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetopic',
            name='message',
            field=models.ForeignKey(related_name='topic_probabilities', to='corpus.Message'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messagetopic',
            name='topic',
            field=models.ForeignKey(related_name='message_probabilities', to='enhance.Topic'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messageword',
            name='message',
            field=models.ForeignKey(related_name='word_scores', to='corpus.Message'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='messageword',
            name='word',
            field=models.ForeignKey(related_name='message_scores', to='enhance.Word'),
            preserve_default=True,
        ),
    ]
