from django.urls import path
from . import views

app_name='payment'

urlpatterns = [
    path('',views.check_out,name='check-out'),
    path('add-address-checkout/',views.add_address_checkout,name='add-address-checkout'),
    path('order-success-page/<int:order_id>',views.order_success_page,name='order-success-page'),
    
    path('razorpay-order/<int:order_id>/',views.create_razorpay_order, name='razorpay-order'),
    path('razorpay-order-item/<int:order_item_id>/', views.create_razorpay_order_item, name='razorpay-order-item'),
    
    path('payment-success/',views.payment_success, name='payment-success'),
    
    path('verify-payment/', views.verify_razorpay_payment, name='verify-razorpay-payment'),
    path('verify-razorpay-payment-item/', views.verify_razorpay_payment_item, name='verify-razorpay-payment-item'),

    path('payment-cancel/',views.payment_cancel, name='payment-cancel'),
    path('payment-cancel-item/', views.payment_cancel_item, name='payment-cancel-item'),
    #apply coupon url here 
    path('apply-coupon/',views.apply_coupon_view, name='apply-coupon'),
    path('remove-coupon/', views.remove_coupon_view, name='remove-coupon'),

]

