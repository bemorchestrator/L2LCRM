from django import forms
from django.forms import inlineformset_factory
from .models import Transaction, TransactionItem

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['patient', 'issuer', 'tel']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control dark:bg-gray-700 dark:text-white',
                'placeholder': 'Select a patient'
            }),
            'issuer': forms.TextInput(attrs={
                'placeholder': 'Issuer',
                'class': 'form-control dark:bg-gray-700 dark:text-white'
            }),
            'tel': forms.TextInput(attrs={
                'placeholder': 'Telephone Number',
                'class': 'form-control dark:bg-gray-700 dark:text-white',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0;'
            }),
        }

class TransactionItemForm(forms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ['item_type', 'product', 'quantity', 'price']
        widgets = {
            'item_type': forms.Select(attrs={
                'class': 'form-control dark:bg-gray-700 dark:text-white',
                'placeholder': 'Select item type'
            }),
            'product': forms.Select(attrs={
                'class': 'form-control product-select dark:bg-gray-700 dark:text-white',
                'placeholder': 'Select a product'
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'class': 'form-control quantity-field dark:bg-gray-700 dark:text-white',
                'min': 1
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Price',
                'class': 'form-control price-input dark:bg-gray-700 dark:text-white',
                'step': 0.01
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].initial = self.instance.price or 0.00

TransactionItemFormSet = inlineformset_factory(
    Transaction,
    TransactionItem,
    form=TransactionItemForm,
    extra=0,
    can_delete=True
)
