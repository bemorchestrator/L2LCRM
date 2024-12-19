from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from transactions.models import TransactionItem
from .models import ItemSalesReport

@receiver(post_save, sender=TransactionItem)
@receiver(post_delete, sender=TransactionItem)
def update_sales_report(sender, instance, **kwargs):
    product = instance.product
    if product:
        report, created = ItemSalesReport.objects.get_or_create(
            item_name=product.item_name,
            date_from=instance.transaction.date,
            date_to=instance.transaction.date,
        )

        items = TransactionItem.objects.filter(
            product=product, transaction__date=report.date_from
        )
        total_sales = sum(item.price * item.quantity for item in items)
        total_cost = sum(
            (item.product.retail_price if item.product.retail_price else Decimal("0.00")) * item.quantity for item in items if item.product
        )
        quantity_sold = sum(item.quantity for item in items)

        report.total_sales = total_sales
        report.total_cost = total_cost
        report.total_discount = Decimal("0.00")  # Placeholder for discount calculation
        report.total_tax = Decimal("0.00")  # Placeholder for tax calculation
        report.average_list_price = (total_sales / quantity_sold) if quantity_sold > 0 else Decimal("0.00")
        report.average_cost_price = (total_cost / quantity_sold) if quantity_sold > 0 else Decimal("0.00")
        report.quantity_sold = quantity_sold

        report.save()
