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

]

