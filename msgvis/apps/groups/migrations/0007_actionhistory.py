# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0006_auto_20150908_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2015, 9, 9, 8, 35, 20, 593700, tzinfo=utc), db_index=True)),
                ('from_server', models.BooleanField(default=False)),
                ('type', models.CharField(default=b'', max_length=100, db_index=True, blank=True)),
                ('contents', models.TextField(default=b'', blank=True)),
                ('owner', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
