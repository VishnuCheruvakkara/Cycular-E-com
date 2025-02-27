from django import forms
from .models import Product,Size,ProductVariant,Category,Brand,Color
import re

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
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Filter categories with status=True
        self.fields['category'].queryset = Category.objects.filter(status=True)
        # Filter brands with status=True
        self.fields['brand'].queryset = Brand.objects.filter(status=True)
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
            if name and not re.match(r'^[a-zA-Z0-9\-\(\)\., ](?:[a-zA-Z0-9\-\(\)]|(?<=\S) )*$', name):
                self.add_error('name', 'Name can only contain letters, numbers, hyphens, brackets, and a single space between words.')
            # Check for unique name in the Product model
            if Product.objects.filter(name=name).exclude(id=self.instance.id).exists():
                self.add_error('name', "A product with this name already exists.")
         # Description validation
        if description and not re.match(r'^[\w\-\(\)\.,;:\s]+$', description):
            self.add_error('description', 'Key specifications can only contain letters, numbers, hyphens, brackets, periods, commas, and spaces.')
        if not category:
            self.add_error('category', "Category is required.")
        if not key_specification:
            self.add_error('key_specification', "Key specification is required.")
        if len(key_specification) < 10:
            self.add_error('key_specification', "Key specification must be at least 10 characters long.")
        # Additional custom validations can go here
        if key_specification and not re.match(r'^[\w\-\(\)\.,;:\s]+$', key_specification):
            self.add_error('key_specification', 'Key specifications can only contain letters, numbers, hyphens, brackets, periods, commas, and spaces.')



        return cleaned_data
    
################### product variant form  ##########################
class ProductVariantForm(forms.ModelForm):
    product_name = forms.CharField(
        label='Product Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False,
    )
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        label='Select Size',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    color = forms.ModelChoiceField(
        queryset=Color.objects.all(),
        label='Select Color',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
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
    image4 = forms.ImageField(  # New field for image4
        label='Image 4',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    status = forms.BooleanField(
        label='Active',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form'})
    )

    class Meta:
        model = ProductVariant
        fields = [
            'product_name',  # The readonly product name field
            'size',
            'color',
            'price',
            'product',  # Include the product field
            'image1',
            'image2',
            'image3',
            'image4', 
            'status',
            'stock',
        ]
        widgets = {
            'product': forms.HiddenInput(),  # keep the product field hidden
        }

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super(ProductVariantForm, self).__init__(*args, **kwargs)
    
        # Filter the 'size' queryset to include only those with status=True
        self.fields['size'].queryset = Size.objects.filter(status=True)

        if not self.instance.pk:
            self.fields['status'].initial = True
        if self.instance and self.instance.size:
            size_instance = self.instance.size
            # to show the existing data in the product variant
         
            self.fields['size'].initial = size_instance
           
        if product:
            self.fields['product_name'].initial = product.name
            self.fields['product'].initial = product.id  # product ID is set correctly
        if self.instance.pk:
            self.fields['status'].initial = self.instance.status

    def clean(self):
        cleaned_data = super().clean()

     
        size = cleaned_data.get('size')
        price = cleaned_data.get("price")
        stock=cleaned_data.get("stock")
        images = {
            'image1': cleaned_data.get("image1"),
            'image2': cleaned_data.get("image2"),
            'image3': cleaned_data.get("image3"),
            'image4': cleaned_data.get("image4"),
        }

    
        if not size:
            self.add_error('size', "Size is required.")

        if not price or price <= 0:
            self.add_error('price', "Price is required and must be greater than zero.")
        if stock is None or stock < 0:
            self.add_error('stock',"Stock is required and positive value.")
       
        max_size_mb = 2  # Maximum size in MB

        for image_field in ['image1', 'image2', 'image3', 'image4']:
            image = cleaned_data.get(image_field)
            
            if not image:
                self.add_error(image_field, f"{image_field.replace('image', 'Image ')} is required.")
             
            else:
                if image.size > max_size_mb * 1024 * 1024:  # Convert MB to bytes
                    self.add_error(image_field, f"The size of {image_field.replace('image', 'Image ')} should not exceed {max_size_mb} MB.")
               
        return cleaned_data
    
  


            
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

        return cleaned_data  # Corrected this line\
    

###########################   color form  ###########################


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['hex_code', 'name', 'status']  # Include status here
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter color name',
                'id': 'color-name',  # Add ID for dynamic name update
                'value':'white'
            }),
            'hex_code': forms.TextInput(attrs={
                'class': 'form-control jscolor',
                'placeholder': 'Choose a color',  # Placeholder text
                'id': 'color-input',  # Add an ID for JavaScript targeting
                'value': '#ff0000', # Default color value (optional)
                'name':'color_hex',
                'data-jscolor': '{}',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form'  # Add a class for styling
            }),
        }

