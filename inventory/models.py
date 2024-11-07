# inventory/models.py

from django.db import models
from suppliers.models import Supplier  # Import Supplier from the suppliers app
from django.core.exceptions import ValidationError

class Product(models.Model):
    ARTICLE = 'Article'
    COMPONENT = 'Component'
    PRODUCT_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (COMPONENT, 'Component'),
    ]

    CATEGORY_TABLET = 'Tablet'
    CATEGORY_CAPSULE = 'Capsule'
    CATEGORY_POWDER = 'Powder'
    CATEGORY_LIQUID = 'Liquid'
    CATEGORY_OTHER = 'Other'
    PRODUCT_CATEGORY_CHOICES = [
        (CATEGORY_TABLET, 'Tablet'),
        (CATEGORY_CAPSULE, 'Capsule'),
        (CATEGORY_POWDER, 'Powder'),
        (CATEGORY_LIQUID, 'Liquid'),
        (CATEGORY_OTHER, 'Other'),
    ]

    item_name = models.CharField(max_length=255, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    currency_code = models.CharField(max_length=3, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    uom = models.CharField(max_length=20, null=True, blank=True)  # Increased max_length for longer UOMs
    discountable_all = models.BooleanField(null=True, blank=True, default=False)
    discountable_members = models.BooleanField(null=True, blank=True, default=True)
    active = models.BooleanField(null=True, blank=True, default=False)
    photo = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True, default=0)
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        default=ARTICLE,
        null=True, blank=True
    )
    linked_article = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'product_type': ARTICLE},
        related_name='components',
        help_text="Link this component to an article product."
    )
    product_category = models.CharField(
        max_length=20,
        choices=PRODUCT_CATEGORY_CHOICES,
        default=CATEGORY_OTHER,
        null=True, blank=True
    )
    custom_product_category = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Specify custom product category if 'Other' is selected."
    )

    def clean(self):
        # Custom validation logic
        if self.product_type == self.ARTICLE and self.linked_article:
            raise ValidationError("An Article cannot be linked to another Article.")
        if self.product_type == self.COMPONENT and not self.linked_article:
            raise ValidationError("A Component must be linked to an Article.")

        # Ensure custom_product_category is provided if product_category is 'Other'
        if self.product_category == self.CATEGORY_OTHER and not self.custom_product_category:
            raise ValidationError({
                'custom_product_category': "This field is required when 'Other' is selected for product category."
            })

        # Define UOM options based on product_category
        uom_mappings = {
            self.CATEGORY_CAPSULE: ['Pieces', 'Bottles'],
            self.CATEGORY_TABLET: ['Pieces', 'Bottles'],
            self.CATEGORY_POWDER: ['Grams', 'Kilograms'],
            self.CATEGORY_LIQUID: ['ml', 'Liters'],
        }

        if self.product_category in uom_mappings:
            allowed_uoms = uom_mappings[self.product_category]
            if self.uom not in allowed_uoms:
                raise ValidationError({
                    'uom': f"For {self.product_category}, UOM must be one of the following: {', '.join(allowed_uoms)}."
                })
        elif self.product_category == self.CATEGORY_OTHER:
            # Optionally, define allowed UOMs for 'Other' or allow any UOM
            if not self.uom:
                raise ValidationError({
                    'uom': "UOM is required for custom product categories."
                })

        # Validate quantity based on product_category
        if self.product_category in [self.CATEGORY_CAPSULE, self.CATEGORY_TABLET]:
            if not isinstance(self.quantity, int):
                raise ValidationError({
                    'quantity': "Quantity must be an integer for Capsules and Tablets."
                })

        super().clean()

    def get_total_component_stock(self):
        if self.product_type == self.ARTICLE:
            # Sum the quantity of all components linked to this article
            return self.components.aggregate(total_stock=models.Sum('quantity'))['total_stock'] or 0
        return None

    def __str__(self):
        return f"{self.item_name} ({self.get_product_type_display()})"
