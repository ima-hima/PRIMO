# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0007_auto_20150625_1603'),
    ]

    operations = [
        migrations.RenameField(
            model_name='querywizardquery',
            old_name='data_table',
            new_name='query_type',
        ),
    ]
