# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0007_auto_20150308_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetopic',
            name='message',
            field=models.ForeignKey(related_name='topic_probabilities', to='corpus.Message', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='messagetopic',
            index_together=set([('topic_model', 'message'), ('message', 'topic')]),
        ),
    ]
