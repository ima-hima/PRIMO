# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgeClass',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('age_class', models.CharField(null=True, max_length=50, blank=True, verbose_name='Age class')),
                ('ageclass_abbr', models.CharField(null=True, max_length=50, blank=True, verbose_name='Class abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'ageclass',
                'managed': True,
                'verbose_name_plural': 'age classes',
            },
        ),
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=80)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('group', models.ForeignKey(to='primo.AuthGroup', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(null=True, blank=True)),
                ('is_superuser', models.IntegerField()),
                ('username', models.CharField(unique=True, max_length=30)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.IntegerField()),
                ('is_active', models.IntegerField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('group', models.ForeignKey(to='primo.AuthGroup', on_delete=models.SET_NULL)),
                ('user', models.ForeignKey(to='primo.AuthUser', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('permission', models.ForeignKey(to='primo.AuthPermission', on_delete=models.SET_NULL)),
                ('user', models.ForeignKey(to='primo.AuthUser', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Bodypart',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('partname', models.CharField(null=True, unique=True, max_length=255, blank=True, verbose_name='Bodypart name')),
                ('comments', models.TextField(null=True, blank=True)),
                ('parent_bodypart', models.ForeignKey(null=True, to='primo.Bodypart', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'bodypart',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='BodypartVariable',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('bodypart', models.ForeignKey(to='primo.Bodypart', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'bodypart_variable',
                'managed': True,
                'verbose_name': 'Bodypart-variable link',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Captive',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('captive', models.CharField(null=True, choices=[('captive', 'captive'), ('wild-caught', 'wild-caught'), ('probably captive', 'probably captive')], max_length=16, blank=True, verbose_name='Captive')),
                ('captive_abbr', models.CharField(null=True, max_length=2, blank=True, verbose_name='Captive abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'captive',
                'managed': True,
                'verbose_name_plural': 'captive',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('category_name', models.CharField(null=True, max_length=80, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'category',
                'managed': True,
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('continent_name', models.CharField(null=True, unique=True, max_length=32, blank=True, verbose_name='Continent name')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'continent',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('country_name', models.CharField(null=True, unique=True, max_length=255, blank=True, verbose_name='Country name')),
                ('country_abbr', models.CharField(null=True, unique=True, max_length=8, blank=True, verbose_name='Country abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'country',
                'managed': True,
                'verbose_name_plural': 'countries',
                'ordering': ['country_name'],
            },
        ),
        migrations.CreateModel(
            name='Data3D',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('datindex', models.IntegerField(null=True, blank=True)),
                ('x', models.FloatField(null=True, blank=True)),
                ('y', models.FloatField(null=True, blank=True)),
                ('z', models.FloatField(null=True, blank=True)),
            ],
            options={
                'db_table': 'data3d',
                'managed': True,
                'verbose_name': '3D data',
                'verbose_name_plural': '3D data',
            },
        ),
        migrations.CreateModel(
            name='Datatype',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('label', models.CharField(null=True, max_length=255, blank=True)),
                ('data_table', models.CharField(null=True, choices=[('scalar', 'scalar'), ('data3d', '3D data'), ('external', 'external')], max_length=32, blank=True, verbose_name='Data table')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'datatype',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('device_name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'device',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(null=True, blank=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.SmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(primary_key=True, serialize=False, max_length=40)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Fossil',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('fossil', models.CharField(null=True, max_length=16, blank=True, verbose_name='Fossil')),
                ('fossil_abbr', models.CharField(null=True, max_length=2, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'fossil',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('institute_abbr', models.CharField(null=True, max_length=8, blank=True, verbose_name='Institute abbreviation')),
                ('institute_name', models.CharField(null=True, max_length=255, blank=True, verbose_name='Institute name')),
                ('institute_dept', models.CharField(null=True, max_length=255, blank=True, verbose_name='Institute department')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'institute',
                'managed': True,
                'ordering': ['institute_name'],
            },
        ),
        migrations.CreateModel(
            name='IslandRegion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(null=True, max_length=255, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'island_region',
                'managed': True,
                'verbose_name': 'Island region',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Laterality',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('laterality', models.CharField(null=True, choices=[('none', 'none'), ('transverse', 'transverse'), ('median', 'median'), ('right', 'right'), ('left', 'left')], max_length=255, blank=True)),
                ('laterality_abbr', models.CharField(null=True, max_length=1, blank=True, verbose_name='Laterality abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'laterality',
                'managed': True,
                'verbose_name_plural': 'laterality',
            },
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('locality_name', models.CharField(null=True, max_length=255, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('site_unit', models.CharField(null=True, max_length=255, blank=True)),
                ('plus_minus', models.FloatField(null=True, blank=True)),
                ('age', models.FloatField(null=True, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('continent', models.ForeignKey(to='primo.Continent', on_delete=models.SET_NULL)),
                ('island_region', models.ForeignKey(to='primo.IslandRegion', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'locality',
                'managed': True,
                'verbose_name_plural': 'localities',
            },
        ),
        migrations.CreateModel(
            name='Observer',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(null=True, unique=True, max_length=255, blank=True)),
                ('initials', models.CharField(null=True, unique=True, max_length=4, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'observer',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Original',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('original', models.CharField(null=True, choices=[('original', 'original'), ('cast', 'cast')], max_length=16, blank=True)),
                ('original_abbr', models.CharField(null=True, max_length=2, blank=True, verbose_name='original abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'original',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Paired',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('paired', models.CharField(null=True, choices=[('Paired', 'Paired'), ('Unpaired', 'Unpaired')], max_length=64, blank=True)),
                ('paired_abbr', models.CharField(null=True, max_length=1, blank=True, verbose_name='Paired abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'paired',
                'managed': True,
                'verbose_name_plural': 'paired',
            },
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('label', models.CharField(null=True, max_length=255, blank=True, verbose_name='Protocol label')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'protocol',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ProtocolVariable',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('protocol', models.ForeignKey(to='primo.Protocol', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'protocol_variable',
                'managed': True,
                'verbose_name': 'Protocol-variable link',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='QueryWizard',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('query_name', models.CharField(null=True, max_length=100, blank=True)),
                ('query_friendly_name', models.CharField(null=True, max_length=255, blank=True)),
                ('query_description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'query_wizard',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='QueryWizardQuery',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('query_id', models.IntegerField(null=True, blank=True)),
                ('data_table', models.CharField(null=True, max_length=20, blank=True)),
                ('query', models.TextField(null=True, blank=True)),
                ('query_suffix', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'query_wizard_query',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='QueryWizardTable',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('query_wizard_id', models.IntegerField(null=True, blank=True)),
                ('display_name', models.CharField(null=True, max_length=100, blank=True)),
                ('filter_table_name', models.CharField(null=True, max_length=50, blank=True)),
                ('display_order', models.IntegerField(null=True, blank=True)),
                ('required', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'query_wizard_table',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('rankname', models.CharField(null=True, max_length=255, blank=True, verbose_name='Rank name')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'rank',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Scalar',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('value', models.CharField(null=True, max_length=10, blank=True)),
            ],
            options={
                'db_table': 'scalar',
                'managed': True,
                'verbose_name_plural': 'scalar',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('filename', models.CharField(null=True, max_length=255, blank=True)),
                ('observer', models.ForeignKey(to='primo.Observer', on_delete=models.SET_NULL)),
                ('original', models.ForeignKey(to='primo.Original', on_delete=models.SET_NULL)),
                ('protocol', models.ForeignKey(to='primo.Protocol', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'session',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Sex',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('sex', models.CharField(null=True, choices=[('male', 'male'), ('female', 'female'), ('male?', 'male?'), ('female?', 'female?'), ('possibly male', 'possibly male'), ('possibly female', 'possibly female'), ('unknown', 'unknown')], max_length=16, blank=True, verbose_name='Sex')),
                ('sex_abbr', models.CharField(null=True, max_length=2, blank=True, verbose_name='Sex abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'sex',
                'managed': True,
                'verbose_name_plural': 'sexes',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('hypocode', models.CharField(null=True, max_length=20, blank=True)),
                ('catalog_number', models.CharField(null=True, max_length=64, blank=True)),
                ('mass', models.IntegerField(null=True, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('ageclass', models.ForeignKey(to='primo.AgeClass', on_delete=models.SET_NULL)),
                ('captive', models.ForeignKey(to='primo.Captive', on_delete=models.SET_NULL)),
                ('fossil', models.ForeignKey(to='primo.Fossil', on_delete=models.SET_NULL)),
                ('institute', models.ForeignKey(to='primo.Institute', on_delete=models.SET_NULL)),
                ('locality', models.ForeignKey(to='primo.Locality', on_delete=models.SET_NULL)),
                ('sex', models.ForeignKey(to='primo.Sex', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'specimen',
                'managed': True,
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='StateProvince',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('state_name', models.CharField(null=True, max_length=255, blank=True, verbose_name='State name')),
                ('state_abbr', models.CharField(null=True, max_length=8, blank=True, verbose_name='State abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
                ('country', models.ForeignKey(to='primo.Country', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'state_province',
                'managed': True,
                'verbose_name': 'State/province',
                'ordering': ['state_name'],
                'verbose_name_plural': 'States/provinces',
            },
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('taxoname', models.CharField(null=True, max_length=255, blank=True, verbose_name='Taxon name')),
                ('ef', models.CharField(null=True, max_length=1, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('parent_taxon', models.ForeignKey(null=True, to='primo.Taxon', on_delete=models.SET_NULL)),
                ('rank', models.ForeignKey(to='primo.Rank', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'taxon',
                'managed': True,
                'verbose_name_plural': 'taxa',
                'ordering': ['taxoname'],
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('type_name', models.CharField(null=True, max_length=16, blank=True, verbose_name='Type name')),
                ('type_abbr', models.CharField(null=True, max_length=2, blank=True, verbose_name='Type abbreviation')),
                ('comments', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'type',
                'managed': True,
                'verbose_name': 'type',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('label', models.CharField(null=True, max_length=32, blank=True)),
                ('name', models.CharField(null=True, max_length=255, blank=True, verbose_name='Variable name')),
                ('comments', models.TextField(null=True, blank=True)),
                ('datatype', models.ForeignKey(to='primo.Datatype', on_delete=models.SET_NULL)),
                ('laterality', models.ForeignKey(to='primo.Laterality', on_delete=models.SET_NULL)),
                ('pairing', models.ForeignKey(null=True, to='primo.Variable', on_delete=models.SET_NULL)),
            ],
            options={
                'db_table': 'variable',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='specimen',
            name='taxon',
            field=models.ForeignKey(to='primo.Taxon', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='specimen',
            name='type',
            field=models.ForeignKey(to='primo.Type', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='session',
            name='specimen',
            field=models.ForeignKey(to='primo.Specimen', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='scalar',
            name='session',
            field=models.ForeignKey(to='primo.Session', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='scalar',
            name='variable',
            field=models.ForeignKey(to='primo.Variable', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='protocolvariable',
            name='variable',
            field=models.ForeignKey(to='primo.Variable', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='locality',
            name='state_province',
            field=models.ForeignKey(to='primo.StateProvince', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='institute',
            name='locality',
            field=models.ForeignKey(to='primo.Locality', on_delete=models.SET_NULL),
        ),
        migrations.AlterUniqueTogether(
            name='djangocontenttype',
            unique_together=set([('app_label', 'model')]),
        ),
        migrations.AddField(
            model_name='djangoadminlog',
            name='content_type',
            field=models.ForeignKey(null=True, blank=True, to='primo.DjangoContentType', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='djangoadminlog',
            name='user',
            field=models.ForeignKey(to='primo.AuthUser', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='data3d',
            name='session',
            field=models.ForeignKey(to='primo.Session', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='data3d',
            name='variable',
            field=models.ForeignKey(to='primo.Variable', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='bodypartvariable',
            name='variable',
            field=models.ForeignKey(to='primo.Variable', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='authpermission',
            name='content_type',
            field=models.ForeignKey(to='primo.DjangoContentType', on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='authgrouppermissions',
            name='permission',
            field=models.ForeignKey(to='primo.AuthPermission', on_delete=models.SET_NULL),
        ),
        migrations.AlterUniqueTogether(
            name='authuseruserpermissions',
            unique_together=set([('user', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='authusergroups',
            unique_together=set([('user', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='authpermission',
            unique_together=set([('content_type', 'codename')]),
        ),
        migrations.AlterUniqueTogether(
            name='authgrouppermissions',
            unique_together=set([('group', 'permission')]),
        ),
    ]
