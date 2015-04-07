# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0018_auto_20150311_1927'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='message',
            index_together=set([('dataset', 'original_id'), ('dataset', 'time')]),
        ),
    ]
