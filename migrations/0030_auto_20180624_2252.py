# Generated by Django 2.0.5 on 2018-06-25 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0029_auto_20180624_2249'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuthGroupPermission',
            new_name='AuthGroupPermissions',
        ),
    ]