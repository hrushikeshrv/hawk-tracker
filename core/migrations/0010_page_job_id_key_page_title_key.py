# Generated by Django 5.2 on 2025-07-12 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_alter_page_selector"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="job_id_key",
            field=models.CharField(
                blank=True,
                help_text="If the response type is JSON, this is the key that contains the job ID in a Job object in the JSON response.",
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="title_key",
            field=models.CharField(
                blank=True,
                help_text="If the response type is JSON, this is the key that contains the job title in a Job object in the JSON response.",
                max_length=32,
                null=True,
            ),
        ),
    ]
