from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0015_add_updated_at_to_session"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="specimen",
            name="primo_id",
        ),
    ]
