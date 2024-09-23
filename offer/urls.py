from django.urls import path
from . import views

app_name='offer'

urlpatterns=[
    path('',views.offer_page,name='offer-page'),
]