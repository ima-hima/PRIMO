# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0006_auto_20150625_1553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='querywizardquery',
            name='query_wizard',
        ),
        migrations.RemoveField(
            model_name='querywizardtable',
            name='query_wizard',
        ),
        migrations.AddField(
            model_name='querywizardtable',
            name='query_wizard_query',
            field=models.ForeignKey(default=1, to='primo.QueryWizardQuery', on_delete=models.SET_NULL),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='QueryWizard',
        ),
    ]
