from django.urls import path
from . import views

app_name='products'

urlpatterns=[
    path('category-management/',views.CategoryManagement,name='category-management'),
    path('add-product/',views.AddProduct,name='add-product'),
    path('edit-product/<int:product_id>',views.EditProduct,name='edit-product'),
    path('delete-product/<int:product_id>',views.DeleteProduct,name='delete-product'),
    path('product-variant/<int:product_id>',views.ProductVariant,name='product-variant')
]
