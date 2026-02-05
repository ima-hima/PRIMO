# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0015_bodypart_expand_in_tree'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bodypart',
            name='expand_in_tree',
        ),
    ]
