# Generated by Django 5.1.2 on 2024-12-16 03:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_alter_container_content_types_and_more'),
        ('transactions', '0002_alter_transaction_transaction_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('Article', 'Article'), ('Component', 'Component')], max_length=10)),
                ('quantity', models.PositiveIntegerField()),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.product')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='transactions.transaction')),
            ],
        ),
    ]