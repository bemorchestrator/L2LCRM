from django import forms
from .models import ItemSalesReport

class ItemSalesReportForm(forms.ModelForm):
    class Meta:
        model = ItemSalesReport
        fields = [
            'item_name',
            'total_sales',
            'total_cost',
            'total_discount',
            'total_tax',
            'average_list_price',
            'average_cost_price',
            'quantity_sold',
            'date_from',
            'date_to',
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Item Name'
            }),
            'total_sales': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Sales',
                'step': 0.01
            }),
            'total_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Cost',
                'step': 0.01
            }),
            'total_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Discount',
                'step': 0.01
            }),
            'total_tax': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Tax',
                'step': 0.01
            }),
            'average_list_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Average List Price',
                'step': 0.01
            }),
            'average_cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Average Cost Price',
                'step': 0.01
            }),
            'quantity_sold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity Sold'
            }),
            'date_from': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Start Date',
                'type': 'date'
            }),
            'date_to': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'End Date',
                'type': 'date'
            }),
        }
