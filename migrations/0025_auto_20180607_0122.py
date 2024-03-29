# Generated by Django 2.0.5 on 2018-06-07 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0024_auto_20180607_0113'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ageclass',
            old_name='ageclass_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='country',
            old_name='country_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='fossil',
            old_name='fossil_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='institute',
            old_name='institute_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='laterality',
            old_name='laterality_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='original',
            old_name='original_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='paired',
            old_name='paired_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='sex',
            old_name='sex_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='stateprovince',
            old_name='state_abbr',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='type',
            old_name='type_abbr',
            new_name='abbr',
        ),
        migrations.AlterField(
            model_name='captive',
            name='abbr',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Abbreviation'),
        ),
        migrations.AlterField(
            model_name='original',
            name='name',
            field=models.CharField(blank=True, choices=[('original', 'original'), ('cast', 'cast')], max_length=16, null=True, verbose_name='Name'),
        ),
    ]
