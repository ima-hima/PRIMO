# Generated by Django 2.1.1 on 2019-08-04 20:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0045_auto_20190804_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specimen',
            name='ageclass',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.Ageclass'),
        ),
        migrations.AlterModelTable(
            name='ageclass',
            table='ageclass',
        ),
    ]
