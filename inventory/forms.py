from django import forms
from .models import Product, Container
from suppliers.models import Supplier
from django.core.exceptions import ValidationError


class ProductForm(forms.ModelForm):
    """
    Form to create or update a product with supplier selection,
    container selection, and validation for content type and UOM.
    """
    uom = forms.ChoiceField(choices=[], required=False)  # Initialize with empty choices

    class Meta:
        model = Product
        fields = [
            'item_name',
            'supplier',
            'container',  # Added field
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
            'content_type',  # Updated field
            'custom_content_type',  # Updated field
            'units_per_article',  # Existing field
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={
                'placeholder': 'Item Name',
                'class': 'form-control'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-control'
            }),
            'container': forms.Select(attrs={
                'class': 'form-control'
            }),
            'currency_code': forms.TextInput(attrs={
                'placeholder': 'Currency Code',
                'class': 'form-control'
            }),
            'retail_price': forms.NumberInput(attrs={
                'placeholder': 'Retail Price',
                'class': 'form-control'
            }),
            'uom': forms.Select(attrs={
                'class': 'form-control'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'discountable_all': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'discountable_members': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'class': 'form-control'
            }),
            'product_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'linked_article': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'custom_content_type': forms.TextInput(attrs={
                'placeholder': 'Specify Custom Content Type',
                'class': 'form-control'
            }),
            'units_per_article': forms.NumberInput(attrs={
                'placeholder': 'Units per Article',
                'class': 'form-control'
            }),
            'container': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        # Populate the supplier dropdown with only active suppliers
        self.fields['supplier'].queryset = Supplier.objects.filter(active=True)

        # Populate the container dropdown with all containers
        self.fields['container'].queryset = Container.objects.all()

        # Filter linked_article to only show Articles
        self.fields['linked_article'].queryset = Product.objects.filter(product_type=Product.ARTICLE)

        # Hide linked_article field when product_type is Article
        if self.instance and self.instance.product_type == Product.ARTICLE:
            self.fields['linked_article'].widget.attrs['disabled'] = True

        # Define UOM choices based on container and content_type
        self.uom_mappings = {}
        if self.instance and self.instance.container:
            container = self.instance.container
            self.uom_mappings = container.allowed_uoms
        elif 'container' in self.data:
            try:
                container = Container.objects.get(pk=self.data['container'])
                self.uom_mappings = container.allowed_uoms
            except Container.DoesNotExist:
                pass

        # Set initial UOM choices based on content_type and container
        content_type = self.data.get('content_type', self.instance.content_type if self.instance.pk else None)
        if content_type in self.uom_mappings:
            self.fields['uom'].choices = [(uom, uom) for uom in self.uom_mappings.get(content_type, [])]
            self.fields['uom'].required = True
        else:
            self.fields['uom'].choices = []
            self.fields['uom'].required = False

    def clean(self):
        cleaned_data = super().clean()
        container = cleaned_data.get('container')
        content_type = cleaned_data.get('content_type')
        custom_content_type = cleaned_data.get('custom_content_type')
        product_type = cleaned_data.get('product_type')
        quantity = cleaned_data.get('quantity')
        uom = cleaned_data.get('uom')

        # Ensure content_type validation
        if content_type == 'Other' and not custom_content_type:
            self.add_error('custom_content_type', "This field is required when 'Other' is selected as content type.")

        # Validate content_type and UOM against the selected container
        if container:
            if content_type not in container.content_types:
                self.add_error('content_type', f"Content type '{content_type}' is not valid for the selected container.")
            allowed_uoms = container.allowed_uoms.get(content_type, [])
            if uom and uom not in allowed_uoms:
                self.add_error('uom', f"UOM '{uom}' is not valid for content type '{content_type}' in the selected container.")

        # Additional validation for Tablets and Capsules
        if content_type in ['Tablet', 'Capsule']:
            if not isinstance(quantity, int):
                self.add_error('quantity', "Quantity must be an integer for Tablets and Capsules.")

        return cleaned_data
