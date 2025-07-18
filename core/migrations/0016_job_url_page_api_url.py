# Generated by Django 5.2 on 2025-07-18 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_alter_job_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="url",
            field=models.URLField(
                blank=True, help_text="URL of the job posting, if available", null=True
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="api_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
