# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0013_auto_20150709_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='expand_in_tree',
            field=models.BooleanField(default=False),
        ),
    ]
