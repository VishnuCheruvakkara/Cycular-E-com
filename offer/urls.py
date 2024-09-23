from django.urls import path
from . import views

app_name='offer'

urlpatterns=[
    path('',views.offer_page,name='offer-page'),
    path('add-product-variant-offer/', views.add_product_variant_offer, name='add-product-variant-offer'),
]