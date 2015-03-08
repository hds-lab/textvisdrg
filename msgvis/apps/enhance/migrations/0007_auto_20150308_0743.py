# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0006_auto_20150305_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicword',
            name='topic',
            field=models.ForeignKey(related_name='word_scores', to='enhance.Topic'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='topicword',
            name='word',
            field=models.ForeignKey(related_name='topic_scores', to='enhance.Word'),
            preserve_default=True,
        ),
    ]
