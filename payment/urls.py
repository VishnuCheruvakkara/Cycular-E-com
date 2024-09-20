from django.urls import path
from . import views

app_name='payment'

urlpatterns = [
    path('',views.check_out,name='check-out'),
    path('add-address-checkout/',views.add_address_checkout,name='add-address-checkout'),
    path('order-success-page/<int:order_id>',views.order_success_page,name='order-success-page'),
    
    path('razorpay-order/<int:order_id>/',views.create_razorpay_order, name='razorpay-order'),
    path('payment-success/',views.payment_success, name='payment-success'),

    #apply coupon url here 
      path('apply-coupon/<int:order_id>/',views.apply_coupon_view, name='apply-coupon'),
]

