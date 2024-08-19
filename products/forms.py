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
    def clean(self):
        cleaned_data = super().clean()
        name=cleaned_data.get("name")
        price = cleaned_data.get("price")
        category = cleaned_data.get("category")
        key_specification = cleaned_data.get("key_specification")
         # Validation for the name field
        if name:
            if len(name) < 3:
                self.add_error('name', "Name must be at least 3 characters long.")
            if not name.isalnum():
                self.add_error('name', "Name should only contain alphabet or number characters only.")
            # Check for unique name in the Product model
            if Product.objects.filter(name=name).exists():
                self.add_error('name', "A product with this name already exists.")
        if price:
            if price <= 0:
                self.add_error('price', "Price must be a positive number.")
            if price >=100000:  # Example maximum price
                self.add_error('price', "Price cannot exceed 1,00,000.")
           

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
    #to avoid the unwanted file name types
    def sanitize_filename(self,filename):
        sanitized_name = re.sub(r'[^\w\.-]', '_', filename)
        return slugify(sanitized_name)
    #validate the mime type
    def validate_mime_type(self, file):
        # Initialize the magic object
        mime = magic.Magic(mime=True)
        # Get the MIME type of the file
        mime_type = mime.from_buffer(file.read())
        # Reset file pointer to beginning after reading
        file.seek(0)

        # Allow only specific MIME types (e.g., JPEG, PNG, GIF)
        allowed_mime_types = ['image/jpeg', 'image/png', 'image/gif']
        if mime_type not in allowed_mime_types:
            return False, mime_type
        return True, mime_type


    def clean(self):
        cleaned_data=super().clean()

        color = cleaned_data.get("color")
        size = cleaned_data.get('size')
        price = cleaned_data.get("size")
        image1 = cleaned_data.get("image1")
        image2 = cleaned_data.get("image2")
        image3 = cleaned_data.get("image3")

        if not color:
            self.add_error('color','Color is required.')
      
        if not size:
            self.add_error('size', "Size is required.")

        if image1:
            image1.name=self.sanitize_filename(image1.name)
            if image1.size > 2 * 1024 * 1024:  # Image size should be less than 5 MB
                self.add_error('image1', "Image 1 should not exceed 2MB.")
            if not image1.content_type.startswith('image/'):
                self.add_error('image1', "Image 1 file must be an image.")

            is_valid_mime, mime_type = self.validate_mime_type(image1)
            if not is_valid_mime:
                self.add_error('image1', f"Image 1 has an invalid file type: {mime_type}")

        if image2:
            image2.name = self.sanitize_filename(image2.name)
            if image2.size > 2 * 1024 * 1024:  # Image size should be less than 5 MB
                self.add_error('image2', "Image 2 should not exceed 2MB.")
            if not image2.content_type.startswith('image/'):
                self.add_error('image2', "Image 2 file must be an image.")

            is_valid_mime, mime_type = self.validate_mime_type(image2)
            if not is_valid_mime:
                self.add_error('image2', f"Image 2 has an invalid file type: {mime_type}")

        if image3:
            image3.name = self.sanitize_filename(image3.name)
            if image3.size > 2 * 1024 * 1024:  # Image size should be less than 5 MB
                self.add_error('image3', "Image 3 should not exceed 2MB.")
            if not image3.content_type.startswith('image/'):
                self.add_error('image3', "Image 3 file must be an image.")

            is_valid_mime, mime_type = self.validate_mime_type(image3)
            if not is_valid_mime:
                self.add_error('image3', f"Image 3 has an invalid file type: {mime_type}")

        return cleaned_data