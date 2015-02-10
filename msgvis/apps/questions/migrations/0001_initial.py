# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dimensions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('authors', models.CharField(default=None, max_length=250, blank=True)),
                ('link', models.CharField(default=None, max_length=250, blank=True)),
                ('title', models.CharField(default=None, max_length=250, blank=True)),
                ('venue', models.CharField(default=None, max_length=250, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('dimensions', models.ManyToManyField(to='dimensions.Dimension')),
                ('source', models.ForeignKey(default=None, to='questions.Article', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
