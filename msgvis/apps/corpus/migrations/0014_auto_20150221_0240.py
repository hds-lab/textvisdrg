# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0013_auto_20150217_0053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='topics',
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]
