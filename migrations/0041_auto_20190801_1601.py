# Generated by Django 2.1.1 on 2019-08-01 20:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0040_auto_20190801_1509'),
    ]

    operations = [
        # migrations.AlterUniqueTogether(
        #     name='authuseruserpermissions',
        #     unique_together=set(),
        # ),
        # migrations.RemoveField(
        #     model_name='authuseruserpermissions',
        #     name='permission',
        # ),
        # migrations.RemoveField(
        #     model_name='authuseruserpermissions',
        #     name='user',
        # ),
        # migrations.RenameField(
        #     model_name='ageclass',
        #     old_name='age_class',
        #     new_name='name',
        # ),
        # migrations.RenameField(
        #     model_name='variable',
        #     old_name='pairing',
        #     new_name='paired_with',
        # ),
        # migrations.RemoveField(
        #     model_name='specimen',
        #     name='specimen_type',
        # ),
        # migrations.AddField(
        #     model_name='specimen',
        #     name='specimen_type',
        #     field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.PROTECT, to='primo.SpecimenType'),
        # ),
        # migrations.RenameField(
        #     model_name='specimen',
        #     old_name='age_class',
        #     new_name='ageclass',
        # ),
        # migrations.AlterField(
        #     model_name='specimen',
        #     name='ageclass',
        #     field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.PROTECT, to='primo.Ageclass'),
        # ),
        # migrations.AlterField(
        #     model_name='specimen',
        #     name='captive',
        #     field=models.ForeignKey(default=9, null=False, on_delete=django.db.models.deletion.PROTECT, to='primo.Captive'),
        # ),
        # migrations.AlterField(
        #     model_name='specimen',
        #     name='fossil',
        #     field=models.ForeignKey(default=9, null=False, on_delete=django.db.models.deletion.PROTECT, to='primo.Fossil'),
        # ),
        # migrations.AlterModelTable(
        #     name='ageclass',
        #     table='age_class',
        # ),
        # migrations.AlterModelTable(
        #     name='specimentype',
        #     table='specimen_type',
        # ),
        # migrations.DeleteModel(
        #     name='AuthUserUserPermissions',
        # ),
    ]