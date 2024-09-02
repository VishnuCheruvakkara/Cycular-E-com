from django.urls import path
from . import views

app_name='cart'

urlpatterns=[
    path('',views.cart,name='cart-page'),
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
]