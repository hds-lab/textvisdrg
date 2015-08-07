# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0019_auto_20150331_2129'),
        ('enhance', '0011_dictionary_dataset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=250, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dataset', models.ForeignKey(to='corpus.Dataset')),
                ('exclusive_keywords', models.ManyToManyField(default=None, related_name='exclusive_keywords', null=True, to='enhance.Word', blank=True)),
                ('inclusive_keywords', models.ManyToManyField(default=None, related_name='inclusive_keywords', null=True, to='enhance.Word', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
