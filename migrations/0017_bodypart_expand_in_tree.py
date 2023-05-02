# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0016_remove_bodypart_expand_in_tree'),
    ]

    operations = [
        migrations.AddField(
            model_name='bodypart',
            name='expand_in_tree',
            field=models.BooleanField(default=False),
        ),
    ]
