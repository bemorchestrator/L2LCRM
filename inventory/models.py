from django.db import models
from suppliers.models import Supplier  # Import Supplier from the suppliers app
from django.core.exceptions import ValidationError

class Container(models.Model):
    BOTTLE = 'Bottle'
    PACK = 'Pack'
    BOX = 'Box'
    BAG = 'Bag'

    CONTAINER_CHOICES = [
        (BOTTLE, 'Bottle'),
        (PACK, 'Pack'),
        (BOX, 'Box'),
        (BAG, 'Bag'),
    ]

    name = models.CharField(
        max_length=50,
        unique=True,
        choices=CONTAINER_CHOICES,
        help_text="Select a container type."
    )
    content_types = models.JSONField(
        default=list,
        help_text="A list of content types this container can hold (e.g., ['Liquid', 'Cream'])."
    )
    allowed_uoms = models.JSONField(
    default=lambda: {
        # Bottle mappings
        "Liquid": ["ml", "liters"],
        "Cream": ["gram"],
        "Syrup": ["gram", "ml"],
        "Tablet": ["pieces"],
        "Capsule": ["pieces"],
        "Oil": ["ml", "drops"],

        # Pack mappings
        "Powder": ["gram"],
        "Leaves": ["gram"],
    },
    help_text="A dictionary mapping content types to their allowed UOMs (e.g., {'Liquid': ['ml', 'liters']})."
)



    def __str__(self):
        return self.name



class Product(models.Model):
    ARTICLE = 'Article'
    COMPONENT = 'Component'
    PRODUCT_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (COMPONENT, 'Component'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Powder', 'Powder'),
        ('Liquid', 'Liquid'),
        ('Syrup', 'Syrup'),
        ('Cream', 'Cream'),
        ('Leaves', 'Leaves'),
        ('Other', 'Other'),
    ]

    item_name = models.CharField(max_length=255, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    container = models.ForeignKey(
        Container,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The container used to hold this product."
    )
    currency_code = models.CharField(max_length=3, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    uom = models.CharField(max_length=20, null=True, blank=True)  # Unit of Measurement
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
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='Other',
        null=True, blank=True
    )
    custom_content_type = models.CharField(
        max_length=50,
        null=True, blank=True,
        help_text="Specify custom content type if 'Other' is selected."
    )
    units_per_article = models.PositiveIntegerField(
        null=True, blank=True, default=1,
        help_text="Number of units of this component required to create one article."
    )

    def clean(self):
        # Validate the container compatibility
        if self.container:
            # Check if content type is allowed in the container
            if self.content_type not in self.container.content_types:
                raise ValidationError({
                    'content_type': f"Content type '{self.content_type}' is not allowed in the container '{self.container.name}'."
                })
            # Check if the UOM is allowed for the content type in the container
            allowed_uoms = self.container.allowed_uoms.get(self.content_type, [])
            if self.uom not in allowed_uoms:
                raise ValidationError({
                    'uom': f"UOM '{self.uom}' is not valid for content type '{self.content_type}' in container '{self.container.name}'. Allowed UOMs: {', '.join(allowed_uoms)}."
                })

        # Custom content type validation
        if self.content_type == 'Other' and not self.custom_content_type:
            raise ValidationError({
                'custom_content_type': "This field is required when 'Other' is selected as content type."
            })

        # Component-Article relationship validation
        if self.product_type == self.COMPONENT and not self.linked_article:
            raise ValidationError("A Component must be linked to an Article.")
        if self.product_type == self.ARTICLE and self.linked_article:
            raise ValidationError("An Article cannot be linked to another Article.")

        # Validate integer quantities for specific content types
        if self.content_type in ['Tablet', 'Capsule'] and not isinstance(self.quantity, int):
            raise ValidationError({'quantity': "Quantity must be an integer for Capsules and Tablets."})

        super().clean()

    def get_total_component_stock(self):
        if self.product_type == self.ARTICLE:
            return self.components.aggregate(total_stock=models.Sum('quantity'))['total_stock'] or 0
        return None

    def calculate_sellable_sets(self):
        """Calculate sellable sets for Articles based on available component quantities."""
        if self.product_type == self.ARTICLE:
            components = self.components.all()
            if not components.exists():
                return self.quantity
            sellable_sets = float('inf')
            for component in components:
                if component.quantity and component.units_per_article > 0:
                    possible_sets = component.quantity // component.units_per_article
                    sellable_sets = min(sellable_sets, possible_sets)
                else:
                    sellable_sets = 0
                    break
            return int(sellable_sets) if sellable_sets != float('inf') else 0
        return None

    def update_component_quantities(self, sold_articles):
        """Update component quantities when articles are sold."""
        if self.product_type == self.ARTICLE:
            components = self.components.all()
            for component in components:
                if component.units_per_article > 0:
                    required_units = sold_articles * component.units_per_article
                    if component.quantity >= required_units:
                        component.quantity -= required_units
                        component.save()
                    else:
                        raise ValidationError(
                            f"Not enough stock for component: {component.item_name}. "
                            f"Required: {required_units}, Available: {component.quantity}."
                        )

    def __str__(self):
        return f"{self.item_name} ({self.get_product_type_display()})"
