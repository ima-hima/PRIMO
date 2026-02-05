# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0010_auto_20150707_1456'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fossil',
            options={'managed': True, 'verbose_name': 'Fossil or Extant', 'verbose_name_plural': 'Fossil or Extant', 'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='taxon',
            name='ef',
        ),
        migrations.AddField(
            model_name='taxon',
            name='fossil',
            field=models.ForeignKey(to='primo.Fossil', default=1, on_delete=models.SET_NULL),
            preserve_default=False,
        ),
    ]
