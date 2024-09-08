from django.urls import path
from . import views

app_name='payment'

urlpatterns = [
    path('',views.check_out,name='check-out'),
    path('add-address-checkout/',views.add_address_checkout,name='add-address-checkout'),
]

