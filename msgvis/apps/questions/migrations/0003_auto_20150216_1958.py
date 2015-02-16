# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_auto_20150214_2139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='dimensions',
        ),
        migrations.DeleteModel(
            name='Dimension',
        ),
    ]
