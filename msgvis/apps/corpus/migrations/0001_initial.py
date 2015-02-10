# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50)),
                ('media_url', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original_id', models.BigIntegerField(default=None, null=True)),
                ('time', models.DateTimeField(default=None, null=True, blank=True)),
                ('contains_hashtag', models.BooleanField(default=False)),
                ('contains_url', models.BooleanField(default=False)),
                ('contains_media', models.BooleanField(default=False)),
                ('contains_mention', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('dataset', models.ForeignKey(to='corpus.Dataset')),
                ('hashtags', models.ManyToManyField(to='corpus.Hashtag')),
                ('language', models.ForeignKey(default=None, blank=True, to='corpus.Language', null=True)),
                ('media', models.ManyToManyField(to='corpus.Media')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original_id', models.BigIntegerField(default=None, null=True, blank=True)),
                ('username', models.CharField(default=None, max_length=150, blank=True)),
                ('full_name', models.CharField(default=None, max_length=250, blank=True)),
                ('replied_to_count', models.PositiveIntegerField(default=0, blank=True)),
                ('shared_count', models.PositiveIntegerField(default=0, blank=True)),
                ('mentioned_count', models.PositiveIntegerField(default=0, blank=True)),
                ('friend_count', models.PositiveIntegerField(default=0, blank=True)),
                ('follower_count', models.PositiveIntegerField(default=0, blank=True)),
                ('dataset_id', models.ForeignKey(to='corpus.Dataset')),
                ('language', models.ForeignKey(default=None, blank=True, to='corpus.Language', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sentiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('olson_code', models.CharField(max_length=40)),
                ('name', models.CharField(max_length=150)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, db_index=True)),
                ('short_url', models.CharField(max_length=250, blank=True)),
                ('full_url', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='message',
            name='mentions',
            field=models.ManyToManyField(related_name='mentioned_in', to='corpus.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(default=None, blank=True, to='corpus.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='sentiment',
            field=models.ForeignKey(default=None, blank=True, to='corpus.Sentiment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='topics',
            field=models.ManyToManyField(default=None, to='corpus.Topic', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='type',
            field=models.ForeignKey(default=None, to='corpus.MessageType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='urls',
            field=models.ManyToManyField(to='corpus.Url'),
            preserve_default=True,
        ),
    ]
