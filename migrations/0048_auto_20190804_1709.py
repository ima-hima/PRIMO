# Generated by Django 2.1.1 on 2019-08-04 21:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0047_auto_20190804_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locality',
            name='island_region',
            field=models.ForeignKey(default=10000, null=True, on_delete=django.db.models.deletion.PROTECT, to='primo.IslandRegion'),
        ),
        migrations.AlterField(
            model_name='locality',
            name='state_province',
            field=models.ForeignKey(default=10000, null=True, on_delete=django.db.models.deletion.PROTECT, to='primo.StateProvince'),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='ageclass',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.Ageclass'),
        ),
    ]
