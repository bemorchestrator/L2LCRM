from django import forms
from .models import Product, Container
from suppliers.models import Supplier

class ProductForm(forms.ModelForm):
    uom = forms.ChoiceField(choices=[], required=False)
    containers = forms.IntegerField(
        required=False,
        min_value=0,
        help_text="For Articles: Number of containers. For Components: leave blank or ignore."
    )

    class Meta:
        model = Product
        fields = [
            'item_name',
            'supplier',
            'container',
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
            'content_type',
            'custom_content_type',
            'units_per_article',
            'pieces_per_container',
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={'placeholder': 'Item Name','class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'container': forms.Select(attrs={'class': 'form-control'}),
            'currency_code': forms.TextInput(attrs={'placeholder': 'Currency Code','class': 'form-control'}),
            'retail_price': forms.NumberInput(attrs={'placeholder': 'Retail Price','class': 'form-control'}),
            'uom': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'discountable_all': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discountable_members': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'For Articles: # of containers, For Components: # of pieces','class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'linked_article': forms.Select(attrs={'class': 'form-control'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'custom_content_type': forms.TextInput(attrs={'placeholder': 'Specify Custom Content Type','class': 'form-control'}),
            'units_per_article': forms.NumberInput(attrs={'placeholder': 'Units per Article (Components only)','class': 'form-control'}),
            'pieces_per_container': forms.NumberInput(attrs={'placeholder': 'Pieces per Container (Articles only)','class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(active=True)
        self.fields['container'].queryset = Container.objects.all()
        self.fields['linked_article'].queryset = Product.objects.filter(product_type=Product.ARTICLE)

        if self.instance and self.instance.product_type == Product.ARTICLE:
            self.fields['linked_article'].widget.attrs['disabled'] = True

        container = self.instance.container if self.instance else None
        content_type = self.instance.content_type if self.instance else None

        if 'container' in self.data:
            try:
                container = Container.objects.get(pk=self.data['container'])
            except Container.DoesNotExist:
                container = None

        if 'content_type' in self.data:
            content_type = self.data.get('content_type')

        if container and content_type:
            allowed_uoms = container.allowed_uoms.get(content_type, [])
            self.fields['uom'].choices = [(uom, uom) for uom in allowed_uoms]
        else:
            self.fields['uom'].choices = []

    def clean(self):
        cleaned_data = super().clean()
        container = cleaned_data.get('container')
        content_type = cleaned_data.get('content_type')
        custom_content_type = cleaned_data.get('custom_content_type')
        uom = cleaned_data.get('uom')

        if container and content_type not in container.content_types:
            self.add_error('content_type', f"Content type '{content_type}' is not valid for the selected container '{container.name}'.")

        if container and content_type:
            allowed_uoms = container.allowed_uoms.get(content_type, [])
            if uom and uom not in allowed_uoms:
                self.add_error('uom', f"UOM '{uom}' is not valid for content type '{content_type}' in the container '{container.name}'.")

        if content_type == 'Other' and not custom_content_type:
            self.add_error('custom_content_type', "This field is required when 'Other' is selected as content type.")

        return cleaned_data
