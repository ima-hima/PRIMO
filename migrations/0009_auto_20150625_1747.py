# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0008_auto_20150625_1617'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='querywizardtable',
            name='required',
        ),
        migrations.AddField(
            model_name='querywizardtable',
            name='preselected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='querywizardtable',
            name='query_wizard_query',
            field=models.ForeignKey(related_name='tables', to='primo.QueryWizardQuery', on_delete=models.SET_NULL),
        ),
    ]
