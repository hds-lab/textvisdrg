# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0019_auto_20150331_2129'),
        ('enhance', '0010_remove_dictionary_dataset'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictionary',
            name='dataset',
            field=models.ForeignKey(related_name='dictionary', default=None, blank=True, to='corpus.Dataset', null=True),
            preserve_default=True,
        ),
    ]
