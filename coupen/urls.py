from django.urls import path
from . import views

app_name='coupen'

urlpatterns = [
    path('',views.coupen_page,name='coupen-page'),
]


