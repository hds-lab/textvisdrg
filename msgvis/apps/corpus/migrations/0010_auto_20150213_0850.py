# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0009_person_message_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='hashtags',
            field=models.ManyToManyField(default=None, to='corpus.Hashtag', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='media',
            field=models.ManyToManyField(default=None, to='corpus.Media', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='mentions',
            field=models.ManyToManyField(default=None, related_name='mentioned_in', null=True, to='corpus.Person', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='original_id',
            field=models.BigIntegerField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.ForeignKey(default=None, blank=True, to='corpus.MessageType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='message',
            name='urls',
            field=models.ManyToManyField(default=None, to='corpus.Url', null=True, blank=True),
            preserve_default=True,
        ),
    ]
