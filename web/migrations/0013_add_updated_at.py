import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0012_add_user_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="data3d",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="datascalar",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="specimen",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
