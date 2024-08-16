from django.urls import path
from . import views

app_name='products'

urlpatterns=[
    path('category-management/',views.CategoryManagement,name='category-management'),
    path('add-product/',views.AddProduct,name='add-product'),
    path('edit-product/<int:product_id>',views.EditProduct,name='edit-product'),
    path('delete-product/<int:product_id>',views.DeleteProduct,name='delete-product'),
    path('product-variant/<int:product_id>',views.ProductVariantViews,name='product-variant'),
    path('single-product/<int:variant_id>',views.SingleProduct,name='single-product'),
    path('get_stock/<int:size_id>/', views.get_stock, name='get_stock'),
]
