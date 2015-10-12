# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0020_person_profile_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='has_prefetched_images',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
