from django import forms
from django.forms import inlineformset_factory
from .models import Transaction, TransactionItem

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['patient', 'issuer', 'tel']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'issuer': forms.TextInput(attrs={
                'placeholder': 'Issuer',
                'class': 'form-control'
            }),
            'tel': forms.TextInput(attrs={
                'placeholder': 'Telephone Number',
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0;'
            }),
        }

class TransactionItemForm(forms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ['item_type', 'product', 'quantity']
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'class': 'form-control',
                'min': 1
            }),
        }

TransactionItemFormSet = inlineformset_factory(
    Transaction,
    TransactionItem,
    form=TransactionItemForm,
    extra=1,
    can_delete=True
)
