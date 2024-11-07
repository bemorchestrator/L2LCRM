# inventory/forms.py

from django import forms
from .models import Product
from suppliers.models import Supplier  
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    """
    Form to create or update a product with supplier selection as a dropdown, 
    product category selection, and an option to specify a custom category.
    """
    uom = forms.ChoiceField(choices=[], required=False)  # Initialize with empty choices

    class Meta:
        model = Product
        fields = [
            'item_name', 
            'supplier', 
            'currency_code', 
            'retail_price', 
            'uom', 
            'discountable_all', 
            'discountable_members', 
            'active', 
            'photo',
            'quantity',
            'product_type',  
            'linked_article',
            'product_category',
            'custom_product_category',
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={
                'placeholder': 'Item Name',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'supplier': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'currency_code': forms.TextInput(attrs={
                'placeholder': 'Currency Code',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'retail_price': forms.NumberInput(attrs={
                'placeholder': 'Retail Price',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'uom': forms.Select(attrs={  # Changed to Select widget
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            }),
            'discountable_all': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary-600'
            }),
            'discountable_members': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary-600'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary-600'
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'product_type': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'linked_article': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'product_category': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
            'custom_product_category': forms.TextInput(attrs={
                'placeholder': 'Specify Custom Category',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Populate the supplier dropdown with only active suppliers
        self.fields['supplier'].queryset = Supplier.objects.filter(active=True)

        # Filter linked_article to only show Articles
        self.fields['linked_article'].queryset = Product.objects.filter(product_type=Product.ARTICLE)

        # Hide linked_article field when product_type is Article
        if self.instance and self.instance.product_type == Product.ARTICLE:
            self.fields['linked_article'].widget.attrs['disabled'] = True

        # Initially hide custom_product_category
        self.fields['custom_product_category'].widget.attrs['style'] = 'display:none;'

        # Define UOM mappings
        self.uom_mappings = {
            'Capsule': ['Pieces', 'Bottles'],
            'Tablet': ['Pieces', 'Bottles'],
            'Powder': ['Grams', 'Kilograms'],
            'Liquid': ['ml', 'Liters'],
        }

        # Set initial UOM choices based on product_category
        if 'product_category' in self.data:
            product_category = self.data.get('product_category')
        elif self.instance.pk:
            product_category = self.instance.product_category
        else:
            product_category = None

        if product_category in self.uom_mappings:
            self.fields['uom'].choices = [(uom, uom) for uom in self.uom_mappings[product_category]]
            self.fields['uom'].required = True
        elif product_category == Product.CATEGORY_OTHER:
            # Optionally, allow any UOM or set to a default
            self.fields['uom'].choices = []
            self.fields['uom'].required = False
        else:
            self.fields['uom'].choices = []
            self.fields['uom'].required = False

    def clean(self):
        cleaned_data = super().clean()
        product_category = cleaned_data.get('product_category')
        custom_product_category = cleaned_data.get('custom_product_category')
        product_type = cleaned_data.get('product_type')
        quantity = cleaned_data.get('quantity')
        uom = cleaned_data.get('uom')

        # If product_category is 'Other', ensure custom_product_category is provided
        if product_category == Product.CATEGORY_OTHER and not custom_product_category:
            self.add_error('custom_product_category', "This field is required when 'Other' is selected for product category.")

        # Validate quantity based on product_category
        if product_category in [Product.CATEGORY_POWDER]:
            allowed_uoms = ['Grams', 'Kilograms']
            if uom not in allowed_uoms:
                self.add_error('uom', f"For Powder, UOM must be one of the following: {', '.join(allowed_uoms)}.")
        elif product_category in [Product.CATEGORY_CAPSULE, Product.CATEGORY_TABLET]:
            if not isinstance(quantity, int):
                self.add_error('quantity', "Quantity must be an integer for Capsules and Tablets.")
            allowed_uoms = ['Pieces', 'Bottles']
            if uom not in allowed_uoms:
                self.add_error('uom', f"For {product_category}, UOM must be one of the following: {', '.join(allowed_uoms)}.")
        elif product_category == Product.CATEGORY_LIQUID:
            allowed_uoms = ['ml', 'Liters']
            if uom not in allowed_uoms:
                self.add_error('uom', f"For Liquid, UOM must be one of the following: {', '.join(allowed_uoms)}.")
        elif product_category == Product.CATEGORY_OTHER:
            if not uom:
                self.add_error('uom', "UOM is required for custom product categories.")

        return cleaned_data
