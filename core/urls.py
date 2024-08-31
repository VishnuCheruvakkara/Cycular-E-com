from django.urls import path
from . import views

app_name='core'

urlpatterns = [
    path('',views.Index,name='index'),
    path('category-filter',views.category_filter,name='category-filter')
]


