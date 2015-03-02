# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dimensions', '0005_auto_20150227_2303'),
        ('questions', '0003_auto_20150216_1958'),
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
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='question',
            name='dimensions',
            field=models.ManyToManyField(to='dimensions.DimensionKey', through='questions.QuestionDimensionConnection'),
            preserve_default=True,
        ),
    ]
