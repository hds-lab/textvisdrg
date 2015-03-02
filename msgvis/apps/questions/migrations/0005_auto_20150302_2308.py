# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dimensions', '0005_auto_20150227_2303'),
        ('questions', '0004_question_dimensions'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionDimensionConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('dimension', models.ForeignKey(to='dimensions.DimensionKey')),
                ('question', models.ForeignKey(to='questions.Question')),
            ],
            options={
                'ordering': ['count'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='question',
            name='dimensions',
        ),
    ]
