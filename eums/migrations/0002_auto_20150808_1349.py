# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eums', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='run',
            name='phone',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
