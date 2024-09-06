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
    


]

