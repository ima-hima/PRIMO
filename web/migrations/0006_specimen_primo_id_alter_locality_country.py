import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0005_rename_name_fossil_label_rename_name_sex_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="locality",
            name="country",
            field=models.ForeignKey(
                default=900,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to="web.country",
            ),
        ),
    ]
