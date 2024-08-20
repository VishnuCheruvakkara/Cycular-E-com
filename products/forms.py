from django import forms
from .models import Product,Color, Size,ProductVariant
import re
from django.utils.text import slugify
import magic
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'category',
            'brand',
            'key_specification',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'key_specification': forms.Textarea(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        name=cleaned_data.get("name")
        category = cleaned_data.get("category")
        key_specification = cleaned_data.get("key_specification")
         # Validation for the name field
        if name:
            if len(name) < 3:
                self.add_error('name', "Name must be at least 3 characters long.")
            if not name.isalnum():
                self.add_error('name', "Name should only contain alphabet or number characters only.")
            # Check for unique name in the Product model
            if Product.objects.filter(name=name).exclude(id=self.instance.id).exists():
                self.add_error('name', "A product with this name already exists.")

        if not category:
            self.add_error('category', "Category is required.")
        if not key_specification:
            self.add_error('key_specification', "Key specification is required.")
        if len(key_specification) < 10:
            self.add_error('key_specification', "Key specification must be at least 10 characters long.")
        # Additional custom validations can go here

        return cleaned_data

class ProductVariantForm(forms.ModelForm):
    product_name = forms.CharField(
        label='Product Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False,
    )
    color = forms.ModelChoiceField(
        queryset=Color.objects.all(),
        label='Select Color',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        label='Select Size',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        label='Price',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True,
    )
    stock = forms.IntegerField(
        label='Stock',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False,
        min_value=0
    )
    image1 = forms.ImageField(
        label='Image 1',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image2 = forms.ImageField(
        label='Image 2',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image3 = forms.ImageField(
        label='Image 3',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ProductVariant
        fields = [
            'product_name',  # The readonly product name field
            'color',
            'size',
            'price',
            'product',  # Include the product field
            'image1',
            'image2',
            'image3',
        ]
        widgets = {
            'product': forms.HiddenInput(),  # keep the product field hidden
        }

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super(ProductVariantForm, self).__init__(*args, **kwargs)
        if product:
            self.fields['product_name'].initial = product.name
            self.fields['product'].initial = product.id  # product ID is set correctly

    def clean(self):
        cleaned_data = super().clean()

        color = cleaned_data.get("color")
        size = cleaned_data.get('size')
        price = cleaned_data.get("price")
        images = {
            'image1': cleaned_data.get("image1"),
            'image2': cleaned_data.get("image2"),
            'image3': cleaned_data.get("image3"),
        }

        if not color:
            self.add_error('color', 'Color is required.')

        if not size:
            self.add_error('size', "Size is required.")

        if not price or price <= 0:
            self.add_error('price', "Price is required and must be greater than zero.")

       

        return cleaned_data