from django.urls import path
from . import views

app_name='wallet'

urlpatterns=[
   path('',views.wallet_page,name='wallet-page'),
   path('cancell-order-item/<int:order_item_id>',views.cancell_order_item,name='cancell-order-item'),
]