# Generated by Django 2.1.1 on 2019-08-09 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0055_auto_20190806_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specimen',
            name='ageclass',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.Ageclass'),
        ),
    ]
