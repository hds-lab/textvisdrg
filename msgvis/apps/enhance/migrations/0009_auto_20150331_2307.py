# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0008_auto_20150331_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageword',
            name='message',
            field=models.ForeignKey(related_name='word_scores', to='corpus.Message', db_index=False),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='messageword',
            index_together=set([('dictionary', 'message'), ('message', 'word')]),
        ),
    ]
