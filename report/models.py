from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from transactions.models import Transaction, TransactionItem
from inventory.models import Product


class ItemSalesReport(models.Model):
    item_name = models.CharField(max_length=255)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_list_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity_sold = models.PositiveIntegerField(default=0)
    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return f"Report for {self.item_name} ({self.date_from} - {self.date_to})"


@receiver(post_save, sender=TransactionItem)
@receiver(post_delete, sender=TransactionItem)
def update_sales_report(sender, instance, **kwargs):
    product = instance.product
    if product:
        # Get or create the report for this product
        report, created = ItemSalesReport.objects.get_or_create(
            item_name=product.item_name,
            date_from=instance.transaction.date,  # Example grouping by transaction date
            date_to=instance.transaction.date,  # Adjust date range as needed
        )

        # Recalculate report details
        items = TransactionItem.objects.filter(
            product=product, transaction__date=report.date_from
        )
        total_sales = sum(item.price * item.quantity for item in items)
        total_cost = sum(
            item.product.retail_price * item.quantity for item in items if item.product
        )
        quantity_sold = sum(item.quantity for item in items)

        report.total_sales = total_sales
        report.total_cost = total_cost
        report.total_discount = Decimal("0.00")  # Add calculation for discount if applicable
        report.total_tax = Decimal("0.00")  # Add calculation for tax if applicable
        report.average_list_price = (
            total_sales / quantity_sold if quantity_sold > 0 else 0
        )
        report.average_cost_price = (
            total_cost / quantity_sold if quantity_sold > 0 else 0
        )
        report.quantity_sold = quantity_sold

        report.save()
