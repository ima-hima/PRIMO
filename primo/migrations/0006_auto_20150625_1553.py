# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0005_delete_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='querywizardquery',
            name='query_id',
        ),
        migrations.RemoveField(
            model_name='querywizardtable',
            name='query_wizard_id',
        ),
        migrations.AddField(
            model_name='querywizardquery',
            name='query_wizard',
            field=models.ForeignKey(to='primo.QueryWizard', default=1, on_delete=models.SET_NULL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='querywizardtable',
            name='query_wizard',
            field=models.ForeignKey(to='primo.QueryWizard', default=1, on_delete=models.SET_NULL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='datatype',
            name='data_table',
            field=models.CharField(blank=True, null=True, verbose_name='Data type', choices=[('scalar', 'scalar'), ('data3d', '3D data'), ('external', 'external')], max_length=32),
        ),
    ]
