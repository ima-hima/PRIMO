# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='group',
            field=models.ForeignKey(to='primo.AuthGroup', default=3, on_delete=models.SET_NULL),
        ),
    ]
