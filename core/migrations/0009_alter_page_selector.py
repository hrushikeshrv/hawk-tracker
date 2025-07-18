# Generated by Django 5.2 on 2025-07-12 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_page_response_type_alter_page_selector"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="selector",
            field=models.CharField(
                help_text="If the response type is HTML, this is the CSS selector that selects all the job titles. If the response type is JSON, this is a comma-separated list of keys that would return the list of job titles from the JSON response.",
                max_length=128,
            ),
        ),
    ]
