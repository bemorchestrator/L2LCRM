from django import forms
from .models import Transaction

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
