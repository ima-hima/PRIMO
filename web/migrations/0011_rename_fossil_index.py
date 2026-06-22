from django.db import migrations


def rename_index_if_exists(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.statistics"
            " WHERE table_schema = DATABASE()"
            " AND table_name = 'fossil'"
            " AND index_name = 'fossil_fossil_or_extant_1b36a877_uniq'"
        )
        if cursor.fetchone()[0] > 0:
            cursor.execute(
                "ALTER TABLE fossil RENAME INDEX"
                " fossil_fossil_or_extant_1b36a877_uniq"
                " TO fossil_label_1b36a877_uniq"
            )


def rename_index_reverse(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.statistics"
            " WHERE table_schema = DATABASE()"
            " AND table_name = 'fossil'"
            " AND index_name = 'fossil_label_1b36a877_uniq'"
        )
        if cursor.fetchone()[0] > 0:
            cursor.execute(
                "ALTER TABLE fossil RENAME INDEX"
                " fossil_label_1b36a877_uniq"
                " TO fossil_fossil_or_extant_1b36a877_uniq"
            )


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0010_specimen_primo_id"),
    ]

    operations = [
        migrations.RunPython(rename_index_if_exists, rename_index_reverse),
    ]
