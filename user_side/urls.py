from django.urls import path
from . import views

app_name='user_side'

urlpatterns=[
    path('sign-up/',views.register_view,name='sign-up'),
    path('sign-in/',views.login_view,name='sign-in'),
    path('sign-out/',views.logout_view,name='sign-out'),
    path('otp/',views.otp_view,name='otp'),
    path('resend-otp/',views.resend_otp,name='resend-otp'),
    path('toggle-user-status/',views.toggle_user_status,name='toggle-user-status'),
    path('user-dash-board/',views.user_dash_board,name='user-dash-board'),
    path('change-username/',views.change_username,name='change-username'),
  
    path('add-address/',views.add_address,name='add-address'),
    path('edit-address/<int:address_id>/',views.edit_address, name='edit-address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete-address'),


    #chage email of user
    path('email-change-view',views.email_change_view,name='email-change-view'),
    path('email-change-otp-view',views.email_change_otp_view,name='email-change-otp-view'),
    path('email-change-resend-otp-view',views.email_change_resend_otp_view,name='email-change-resend-otp-view'),

    #change password of the loged in user
    path('password-change-view/',views.password_change_view,name='password-change-view'),
    path('password-change-otp-view/',views.password_change_otp_view,name='password-change-otp-view'),
    path('password-change-resend-otp-view/',views.password_change_resend_otp_view,name='password-change-resend-otp-view'),

    #forget password section
    path('forget-password/',views.forget_password,name='forget-password'),
    path('forget-password-otp/',views.forget_password_otp,name='forget-password-otp'),
    path('forget-password-set/',views.forget_password_set,name='forget-password-set'),
  
    path('forget-password-resend-otp/',views.forget_password_resend_otp,name='forget-password-resend-otp'),
    #to show order item in the order history of user.
    path('order-item-details/',views.order_item_details,name='order-item-details'),
    #cancell order of orderitems 
    path('order-item-cancell/<int:order_item_id>',views.order_item_cancell,name='order-item-cancell'),
    path('canell-order/<int:order_id>',views.order_cancell,name='order-cancell'),
]

