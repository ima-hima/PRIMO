# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0009_auto_20150625_1747'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taxon',
            options={'ordering': ['name'], 'verbose_name_plural': 'taxa', 'managed': True},
        ),
        migrations.RenameField(
            model_name='bodypart',
            old_name='partname',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='bodypart',
            old_name='parent_bodypart',
            new_name='parent',
        ),
        migrations.RenameField(
            model_name='taxon',
            old_name='taxoname',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='taxon',
            old_name='parent_taxon',
            new_name='parent',
        ),
    ]
