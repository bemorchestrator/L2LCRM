from django.db import models
from django.forms import ValidationError
from patients.models import Patients
from inventory.models import Product
from decimal import Decimal

class Transaction(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name='transactions')
    transaction_no = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(auto_now_add=True)
    issuer = models.CharField(max_length=255, default='Sebastian Liew')
    tel = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=255, editable=False)
    email = models.EmailField(editable=False)
    address = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            last_transaction = Transaction.objects.order_by('-id').first()
            if last_transaction and last_transaction.transaction_no.startswith('TXN'):
                last_number = int(last_transaction.transaction_no[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.transaction_no = f"TXN{new_number:05d}"
            self.name = f"{self.patient.first_name} {self.patient.last_name}"
            self.email = self.patient.email
            self.address = self.patient.address
            self.tel = self.patient.phone
        super(Transaction, self).save(*args, **kwargs)

    def get_total_amount(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.price * item.quantity
        return total

    def __str__(self):
        return f"Transaction {self.transaction_no} for {self.patient}"

class TransactionItem(models.Model):
    ARTICLE = 'Article'
    COMPONENT = 'Component'
    ITEM_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (COMPONENT, 'Component'),
    ]
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.product and self.product.quantity < self.quantity:
            raise ValidationError(
                f"Not enough stock for {self.product.item_name}. "
                f"Available: {self.product.quantity}, Required: {self.quantity}."
            )
        super(TransactionItem, self).save(*args, **kwargs)
        self.update_inventory()

    def update_inventory(self):
        if self.product:
            if self.item_type == self.ARTICLE and self.product.product_type == Product.ARTICLE:
                self.product.quantity -= self.quantity
                if self.product.quantity < 0:
                    raise ValidationError(
                        f"Not enough stock for {self.product.item_name}. "
                        f"Available: {self.product.quantity + self.quantity}, Required: {self.quantity}."
                    )
                self.product.save()
                self.product.update_component_quantities(self.quantity)
            elif self.item_type == self.COMPONENT and self.product.product_type == Product.COMPONENT:
                self.product.quantity -= self.quantity
                if self.product.quantity < 0:
                    raise ValidationError(
                        f"Not enough stock for {self.product.item_name}. "
                        f"Available: {self.product.quantity + self.quantity}, Required: {self.quantity}."
                    )
                self.product.save()

    def delete(self, *args, **kwargs):
        if self.product:
            self.product.quantity += self.quantity
            self.product.save()
        super(TransactionItem, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.item_type} - {self.product.item_name if self.product else 'N/A'} (x{self.quantity})"
