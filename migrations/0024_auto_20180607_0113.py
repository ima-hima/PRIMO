# Generated by Django 2.0.5 on 2018-06-07 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0023_auto_20180607_0050'),
    ]

    operations = [
        migrations.RenameField(
            model_name='captive',
            old_name='captive_abbr',
            new_name='abbr',
        ),

    ]
