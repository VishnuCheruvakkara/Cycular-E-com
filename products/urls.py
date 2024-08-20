from django.urls import path
from . import views

app_name='products'

urlpatterns=[
    path('product-management/',views.ProductManagement,name='product-management'),
    path('add-product/',views.AddProduct,name='add-product'),
    path('edit-product/<int:product_id>',views.EditProduct,name='edit-product'),
    path('delete-product/<int:product_id>',views.DeleteProduct,name='delete-product'),
    path('product-variant/<int:product_id>',views.ProductVariant,name='product-variant'),
    path('toggle-product-status/', views.toggle_product_status, name='toggle-product-status'),
    path('product-view/<int:product_id>',views.product_view,name='product-view'),
    path('category-add/',views.category_management,name='category-add'),
    path('category-delete/<int:category_id>',views.delete_category,name='category-delete'),
    path('brand-delete/<int:brand_id>',views.delete_brand,name='brand-delete'),
    path('size-delete/<int:size_id>',views.delete_size,name='size-delete'),
    path('color-delete/<int:color_id>',views.delete_color,name='color-delete'),

   
  
]