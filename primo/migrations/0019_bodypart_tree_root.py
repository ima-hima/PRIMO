# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0018_taxon_tree_root'),
    ]

    operations = [
        migrations.AddField(
            model_name='bodypart',
            name='tree_root',
            field=models.BooleanField(default=False),
        ),
    ]
