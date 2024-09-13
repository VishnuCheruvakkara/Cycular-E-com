from django.urls import path
from . import views

app_name='wishlist'

urlpatterns=[
   path('',views.wishlist_page,name='wishlist-page'),
   
   path('add-to-wishlist/',views.add_to_wishlist,name='add-to-wishlist'),
]