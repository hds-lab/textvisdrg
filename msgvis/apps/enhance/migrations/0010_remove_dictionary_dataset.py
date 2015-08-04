# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enhance', '0009_auto_20150331_2307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dictionary',
            name='dataset',
        ),
    ]
