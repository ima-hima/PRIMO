# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0017_bodypart_expand_in_tree'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='tree_root',
            field=models.BooleanField(default=False),
        ),
    ]
