from django import forms
from .models import Product,Color, Size,ProductVariant,Category,Brand
import re
from django.utils.text import slugify
import magic

#####################  product form  ###################
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
        description=cleaned_data.get("description")
         # Validation for the name field
        if name:
            if len(name) < 3:
                self.add_error('name', "Name must be at least 3 characters long.")
            if not re.match(r'^[a-zA-Z]', name):
                self.add_error('name', "Name must start with a letter.")
            if name and not re.match(r'^[a-zA-Z0-9\-\(\)](?:[a-zA-Z0-9\-\(\)]|(?<=\S) )*$', name):
                self.add_error('name', 'Name can only contain letters, numbers, hyphens, brackets, and a single space between words.')
            # Check for unique name in the Product model
            if Product.objects.filter(name=name).exclude(id=self.instance.id).exists():
                self.add_error('name', "A product with this name already exists.")
        if description and not re.match(r'^[a-zA-Z0-9\-\(\)](?:[a-zA-Z0-9\-\(\)]|(?<=\S) )*$', description):
                self.add_error('description', 'Description can only contain letters, numbers, hyphens, brackets, and a single space between words.')
        if not category:
            self.add_error('category', "Category is required.")
        if not key_specification:
            self.add_error('key_specification', "Key specification is required.")
        if len(key_specification) < 10:
            self.add_error('key_specification', "Key specification must be at least 10 characters long.")
        # Additional custom validations can go here
        if key_specification and not re.match(r'^[a-zA-Z0-9\-\(\)](?:[a-zA-Z0-9\-\(\)]|(?<=\S) )*$', key_specification):
                self.add_error('key_specification', 'Key specifications can only contain letters, numbers, hyphens, brackets, and a single space between words.')

        return cleaned_data
    
################### product variant form  ##########################
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
        if self.instance and self.instance.size:
            size_instance = self.instance.size
            self.fields['color'].initial = size_instance.color
            self.fields['size'].initial = size_instance
            self.fields['stock'].initial = size_instance.stock
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
    
    def save(self, commit=True):
        # Get the cleaned data
        cleaned_data = self.cleaned_data
        color = cleaned_data.get('color')
        size = cleaned_data.get('size')
        stock = cleaned_data.get('stock')

        # Update the stock in the related Size model
        if size and stock is not None:
            size.stock = stock
            size.color=color
            size.save()

        # Save the ProductVariant with the correct color reference
        
        return super(ProductVariantForm, self).save(commit=commit)

    
#####################  Category form #######################

class CategoryForm(forms.ModelForm):
    status = forms.BooleanField(
        required=False,
        label='Check Status : ',
    )
    
    class Meta:
        model = Category
        fields = ['name', 'status']  # 'description' is not included here because it's a custom form field, not a model field.
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'status': forms.CheckboxInput(),
        }
   
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        # Check if name is too short
        if name and len(name) < 3:
            self.add_error('name', 'Name must be at least 3 characters long.')
        if not re.match(r'^[a-zA-Z]', name):
                self.add_error('name', "Name must start with a letter.")
        # Check if name contains only letters and numbers
        if name and not re.match(r'^[a-zA-Z0-9() \-]*$', name):
            self.add_error('name', 'Name can only contain letters,spaces,bracket and numbers.')

        # Check if name consists of only numbers
        if name and re.match(r'^\d+$', name):
            self.add_error('name', 'Name cannot consist of only numbers. It must include letters.')

        return cleaned_data
 

######################### Brand Form #############################

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter brand name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type description',
                'rows': 4,
                'cols': 40
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form'
            }),
        }
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        description=cleaned_data.get("description")
        
        # Non-field validation for 'name' field
        if name and len(name) < 3:
            self.add_error(None, "Brand name must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z]', name):
                self.add_error('name', "Name must start with a letter.")
        # Check if name contains only letters and numbers
        if name and not re.match(r'^[a-zA-Z0-9\s-]*$', name):
            self.add_error('name', 'Name can only contain letters, numbers, spaces, and hyphens.')

        # Check if name consists of only numbers
        if name and re.match(r'^\d+$', name):
            self.add_error('name', 'Name cannot consist of only numbers. It must include letters.')

        if description:
            # Ensure description is not too short
            if len(description) < 10:
                self.add_error('description', 'Description is too short. Please provide more details.')
        
        if re.match(r'^\d+$', description):
            self.add_error('description', 'Description cannot consist of only numbers. It must include letters.')

        return cleaned_data

######################### Color Form #############################
class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter color name'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        
        # Non-field validation for 'name' field
        if name and len(name) < 3:
            self.add_error(None, "Color name must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z]', name):
                self.add_error('name', "Name must start with a letter.")
        # Check if name contains only letters and numbers
        if name and not re.match(r'^[a-zA-Z0-9]*$', name):
            self.add_error('name', 'Name can only contain letters and numbers.')

        # Check if name consists of only numbers
        if name and re.match(r'^\d+$', name):
            self.add_error('name', 'Name cannot consist of only numbers. It must include letters.')

        return cleaned_data  

    
######################### Size Form #############################

class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter size name'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form',
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")

        
        # Non-field validation for 'name' field
        if name and len(name) < 3:
            self.add_error(None, "Color name must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z]', name):
                self.add_error('name', "Name must start with a letter.")
        # Check if name contains only letters and numbers
        if name and not re.match(r'^[a-zA-Z0-9() ]*$', name):
            self.add_error('name', 'Name can only contain letters, numbers, spaces and brackets.')

        # Check if name consists of only numbers
        if name and re.match(r'^\d+$', name):
            self.add_error('name', 'Name cannot consist of only numbers. It must include letters.')

        return cleaned_data  # Corrected this line
