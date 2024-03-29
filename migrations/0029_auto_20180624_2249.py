# Generated by Django 2.0.5 on 2018-06-25 02:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0028_auto_20180607_1209'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuthGroupPermissions',
            new_name='AuthGroupPermission',
        ),
        migrations.AlterModelOptions(
            name='specimentype',
            options={'managed': True, 'ordering': ['id'], 'verbose_name': 'specimen type'},
        ),
        migrations.AlterField(
            model_name='captive',
            name='name',
            field=models.CharField(blank=True, choices=[('captive', 'captive'), ('wild-caught', 'wild-caught'), ('probably captive', 'probably captive')], max_length=16, null=True, verbose_name='Captive or wild-caught'),
        ),
        migrations.AlterField(
            model_name='fossil',
            name='name',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Fossil or Extant'),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='captive',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='primo.Captive'),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='fossil',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='primo.Fossil'),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Taxon name'),
        ),
    ]
