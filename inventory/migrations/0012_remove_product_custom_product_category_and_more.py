# Generated by Django 5.1.2 on 2024-12-02 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_product_uom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='custom_product_category',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_category',
        ),
        migrations.AddField(
            model_name='product',
            name='content_type',
            field=models.CharField(blank=True, choices=[('Tablet', 'Tablet'), ('Capsule', 'Capsule'), ('Powder', 'Powder'), ('Liquid', 'Liquid'), ('Syrup', 'Syrup'), ('Cream', 'Cream'), ('Leaves', 'Leaves'), ('Other', 'Other')], default='Other', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='custom_content_type',
            field=models.CharField(blank=True, help_text="Specify custom content type if 'Other' is selected.", max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='units_per_article',
            field=models.PositiveIntegerField(blank=True, default=1, help_text='Number of units of this component required to create one article.', null=True),
        ),
    ]