from django.urls import path
from . import views

app_name='cart'

urlpatterns=[
    path('',views.cart,name='cart-page'),
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
    path('cart-count/',views.get_cart_count, name='cart-count'),
    path('remove-from-cart/<int:cart_item_id>',views.remove_from_cart, name='remove-from-cart'),

    path('update-cart-item-quantity/<int:cart_item_id>/',views.update_cart_item_quantity, name='update-cart-item-quantity'),
]