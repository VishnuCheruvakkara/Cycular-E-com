from django.urls import path
from . import views

app_name='coupon'

urlpatterns = [
    path('',views.coupon_management,name='coupon-management'),
    path('edit/<int:coupon_id>/', views.edit_coupon, name='edit-coupon'),
    path('delete/<int:coupon_id>/', views.delete_coupon, name='delete-coupon'),
]


