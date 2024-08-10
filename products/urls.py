from django.urls import path
from . import views

app_name='products'

urlpatterns=[
    path('category-management/',views.CategoryManagement,name='category-management'),
    path('add-product/',views.AddProduct,name='add-product'),
    path('edit-product/',views.EditProduct,name='edit-product'),
]
