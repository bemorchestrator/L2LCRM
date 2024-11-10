from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'supplier', 'currency_code', 'retail_price', 'uom', 'discountable_all', 'discountable_members', 'active', 'product_type', 'get_total_component_stock', 'calculate_sellable_sets')  # Added 'get_total_component_stock' and 'calculate_sellable_sets'
    search_fields = ('item_name', 'supplier')
    list_filter = ('currency_code', 'discountable_all', 'discountable_members', 'active', 'product_type')
