from django.db import models
from decimal import Decimal

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
