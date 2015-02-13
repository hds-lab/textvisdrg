# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_auto_20150210_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='timezone',
            field=models.ForeignKey(default=None, blank=True, to='corpus.Timezone', null=True),
            preserve_default=True,
        ),
    ]
