# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0003_authgroup_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locality',
            name='island_region',
            field=models.ForeignKey(null=True, to='primo.IslandRegion', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='locality',
            name='state_province',
            field=models.ForeignKey(null=True, to='primo.StateProvince', on_delete=models.CASCADE),
        ),
    ]
