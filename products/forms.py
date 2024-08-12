from django import forms
from .models import Product,Color, Size,ProductVariant

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'category',
            'brand',
            'key_specification',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'key_specification': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ProductVariantForm(forms.ModelForm):
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
    image1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Image 1'
    )
    image2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Image 2'
    )
    image3 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Image 3'
    )

    class Meta:
        model = ProductVariant
        fields = [
            'product',  # Automatically set in the view or admin interface
            'color',
            'size',
            'image1',
            'image2',
            'image3',
        ]
        widgets = {
            'product': forms.HiddenInput(),  # Assuming the product is set elsewhere
        }







