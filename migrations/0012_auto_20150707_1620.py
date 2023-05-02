# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0011_auto_20150707_1517'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fossil',
            old_name='fossil',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='sex',
            old_name='sex',
            new_name='name',
        ),
    ]
