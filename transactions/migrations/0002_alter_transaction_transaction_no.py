# Generated by Django 5.1.2 on 2024-11-11 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_no',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]
