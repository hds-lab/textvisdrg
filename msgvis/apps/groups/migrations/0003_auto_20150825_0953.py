# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_group_messages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='messages',
        ),
        migrations.AlterField(
            model_name='group',
            name='dataset',
            field=models.ForeignKey(related_name='groups', to='corpus.Dataset'),
            preserve_default=True,
        ),
    ]
