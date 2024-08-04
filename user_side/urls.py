from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views

app_name='user_side'

urlpatterns=[
    path('sign-up/',views.register_view,name='sign-up'),
    path('sign-in/',views.login_view,name='sign-in'),
    path('sign-out/',views.logout_view,name='sign-out'),
    path('otp/<int:user_id>/',views.otp_view,name='otp'),
]

