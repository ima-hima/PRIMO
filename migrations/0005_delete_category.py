# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primo', '0004_auto_20150617_1604'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
    ]
