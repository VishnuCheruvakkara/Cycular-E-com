from django.urls import path
from . import views

app_name='products'

urlpatterns=[
    path('product-management/',views.ProductManagement,name='product-management'),
    path('add-product/',views.AddProduct,name='add-product'),
    path('edit-product/<int:product_id>',views.EditProduct,name='edit-product'),
    path('delete-product/<int:product_id>',views.DeleteProduct,name='delete-product'),
    path('product-variant/<int:product_id>',views.product_variant,name='product-variant'),
    path('toggle-product-status/', views.toggle_product_status, name='toggle-product-status'),
    path('product-view/<int:product_id>',views.product_view,name='product-view'),
    path('category-add/',views.category_management,name='category-add'),

    path('single-product-view/<int:product_id>',views.single_product_view,name='single-product-view'),

    path('category-delete/<int:category_id>',views.delete_category,name='category-delete'),
    path('brand-delete/<int:brand_id>',views.delete_brand,name='brand-delete'),
    path('size-delete/<int:size_id>',views.delete_size,name='size-delete'),
    path('color-delete/<int:color_id>',views.delete_color,name='color-delete'),
    
    path('add-category/',views.add_category,name='add-category'),
    path('edit-category/<int:category_id>',views.edit_category,name='edit-category'),

    path('add-brand/',views.add_brand,name='add-brand'),
    path('edit-brand/<int:brand_id>',views.edit_brand,name='edit-brand'),

    path('add-size/',views.add_size,name='add-size'),
    path('edit-size/<int:size_id>',views.edit_size,name='edit-size'),

    path('add-color/',views.add_color,name='add-color'),
    path('edit-color/<int:color_id>',views.edit_color,name='edit-color'),
  
    path('delete-product-variant/<int:variant_id>',views.delete_product_variant,name='delete-product-variant'),
    path('edit-variant/<int:variant_id>',views.edit_variant,name='edit-variant'),
    path('product-variant-data-view/<int:variant_id>',views.product_variant_data,name='product_variant_data_view'),

    path('toggle-status/<int:variant_id>/',views.toggle_status, name='toggle_status'),
]