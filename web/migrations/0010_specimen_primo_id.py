from django.db import migrations, models


def copy_id_to_primo_id(apps, schema_editor):
    schema_editor.execute("UPDATE specimen SET primo_id = id")


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("web", "0009_remove_specimen_primo_id"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="specimen",
                    name="primo_id",
                    field=models.IntegerField(null=True),
                ),
            ],
        ),
        migrations.RunPython(copy_id_to_primo_id, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="specimen",
            name="primo_id",
            field=models.IntegerField(unique=True),
        ),
    ]
