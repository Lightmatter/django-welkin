# Generated by Django 4.1.9 on 2023-06-06 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_welkin", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuration",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="webhookmessage",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
