from django.urls import path
from . import views

app_name='offer'

urlpatterns=[
    path('',views.offer_page,name='offer-page'),
    path('add-product-variant-offer/', views.add_product_variant_offer, name='add-product-variant-offer'),
     path('offer/soft-delete/product/', views.soft_delete_product_offer, name='soft-delete-product-offer'),
    path('add-brand-offer/',views.add_brand_offer, name='add-brand-offer'),
    path('offer/soft-delete/',views.soft_delete_brand_offer, name='soft-delete-brand-offer')
]