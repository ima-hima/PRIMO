# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0002_session_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='authgroup',
            name='description',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
