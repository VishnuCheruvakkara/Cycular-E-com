from django.urls import path
from . import views

app_name='admin_side'

urlpatterns=[
    path('',views.SellerHome,name='seller-home'),
    path('seller-login/',views.SellerLogin,name='seller-login'),
    path('seller-logout/',views.SellerLogout,name='seller-logout'),
    path('user-management/',views.UserManagement,name='user-management'),
    path('user-view/<int:user_id>',views.UserView,name='user-view'),
    path('order-management/',views.OrderManagement,name='order-management'),
    path('sales-report/',views.sales_report, name='sales-report'),
]
