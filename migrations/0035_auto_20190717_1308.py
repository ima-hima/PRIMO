# Generated by Django 2.1.1 on 2019-07-17 17:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0034_auto_20190717_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specimen',
            name='locality',
            field=models.ForeignKey(default=10000, on_delete=django.db.models.deletion.PROTECT, to='primo.Locality'),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='sex',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.Sex'),
        ),
        migrations.AlterField(
            model_name='specimentype',
            name='name',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='ageclass',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.AgeClass'),
        ),

    ]
