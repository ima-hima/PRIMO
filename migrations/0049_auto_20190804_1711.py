# Generated by Django 2.1.1 on 2019-08-04 21:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0048_auto_20190804_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specimen',
            name='ageclass',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.Ageclass'),
        ),
    ]
