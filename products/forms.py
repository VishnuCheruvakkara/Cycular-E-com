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
    color = forms.ModelChoiceField(queryset=Color.objects.all(), label='Select Color')
    size = forms.ModelChoiceField(queryset=Size.objects.all(), label='Select Size')
    image1 = forms.ImageField(required=False, widget=forms.ClearableFileInput(), label='Image 1')
    image2 = forms.ImageField(required=False, widget=forms.ClearableFileInput(), label='Image 2')
    image3 = forms.ImageField(required=False, widget=forms.ClearableFileInput(), label='Image 3')

    class Meta:
        model = ProductVariant
        fields = [
          
            'color',
            'size',
            'image1',
            'image2',
            'image3',
        ]

    widgets = {
            'product': forms.HiddenInput(),  # Assuming the product is set elsewhere
            'color': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a color'
            }),
            'size': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a size'
            }),
            'image1': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
            'image2': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
            'image3': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
        }