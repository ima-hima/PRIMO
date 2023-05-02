# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0012_auto_20150707_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bodypart',
            name='name',
            field=models.CharField(verbose_name='Bodypart name', null=True, unique=True, blank=True, max_length=191),
        ),
        migrations.AlterField(
            model_name='country',
            name='country_name',
            field=models.CharField(verbose_name='Country name', null=True, unique=True, blank=True, max_length=191),
        ),
        migrations.AlterField(
            model_name='locality',
            name='locality_name',
            field=models.CharField(null=True, blank=True, max_length=191),
        ),
        migrations.AlterField(
            model_name='observer',
            name='name',
            field=models.CharField(null=True, unique=True, blank=True, max_length=191),
        ),
    ]
