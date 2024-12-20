# Generated by Django 5.1.2 on 2024-12-09 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_alter_container_allowed_uoms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='allowed_uoms',
            field=models.JSONField(default=dict, help_text='A dictionary mapping content types to their allowed UOMs.'),
        ),
    ]
