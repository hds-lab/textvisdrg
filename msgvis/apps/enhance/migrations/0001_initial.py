# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import msgvis.apps.enhance.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0013_auto_20150217_0053'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('dataset', models.CharField(max_length=100)),
                ('settings', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('num_docs', msgvis.apps.enhance.fields.PositiveBigIntegerField(default=0)),
                ('num_pos', msgvis.apps.enhance.fields.PositiveBigIntegerField(default=0)),
                ('num_nnz', msgvis.apps.enhance.fields.PositiveBigIntegerField(default=0)),
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
                ('description', models.CharField(max_length=200)),
                ('index', models.IntegerField()),
                ('alpha', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('perplexity', models.FloatField(default=0)),
                ('dictionary', models.ForeignKey(to='enhance.Dictionary')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word_index', models.IntegerField()),
                ('probability', models.FloatField()),
                ('topic', models.ForeignKey(related_name='words', to='enhance.Topic')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TweetTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('probability', models.FloatField()),
                ('source', models.ForeignKey(to='corpus.Message')),
                ('topic', models.ForeignKey(to='enhance.Topic')),
                ('topic_model', models.ForeignKey(to='enhance.TopicModel', db_index=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TweetWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word_index', models.IntegerField()),
                ('count', models.FloatField()),
                ('tfidf', models.FloatField()),
                ('dictionary', models.ForeignKey(to='enhance.Dictionary', db_index=False)),
                ('source', models.ForeignKey(related_name='words', to='corpus.Message')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField()),
                ('text', models.CharField(max_length=100)),
                ('document_frequency', models.IntegerField()),
                ('dictionary', models.ForeignKey(related_name='words', to='enhance.Dictionary')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tweetword',
            name='word',
            field=models.ForeignKey(to='enhance.Word'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='tweetword',
            index_together=set([('dictionary', 'source')]),
        ),
        migrations.AlterIndexTogether(
            name='tweettopic',
            index_together=set([('topic_model', 'source')]),
        ),
        migrations.AddField(
            model_name='topicword',
            name='word',
            field=models.ForeignKey(to='enhance.Word'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='model',
            field=models.ForeignKey(related_name='topics', to='enhance.TopicModel'),
            preserve_default=True,
        ),
    ]
