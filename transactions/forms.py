# transactions/forms.py
from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['patient', 'issuer', 'tel']  # 'tel' is included but made read-only
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),
            'issuer': forms.TextInput(attrs={
                'placeholder': 'Issuer',
                'class': 'form-control'
            }),
            'tel': forms.TextInput(attrs={
                'placeholder': 'Telephone Number',
                'class': 'form-control',
                'readonly': 'readonly',  # Make tel field read-only
                'style': 'background-color: #f0f0f0;',  # Optional: visually indicate read-only
            }),
        }
