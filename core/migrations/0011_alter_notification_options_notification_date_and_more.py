# Generated by Django 5.2 on 2025-07-13 02:02

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_page_job_id_key_page_title_key"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notification",
            options={"ordering": ["-date"]},
        ),
        migrations.AddField(
            model_name="notification",
            name="date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="notification",
            name="jobs",
            field=models.ManyToManyField(
                blank=True, related_name="notifications", to="core.job"
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="n_new_jobs",
            field=models.IntegerField(default=0),
        ),
    ]
