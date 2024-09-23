"""
URL configuration for cycular_ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('core.urls')),
    path('user/',include('user_side.urls')),
    path('seller/',include('admin_side.urls')),
    path('products/',include('products.urls')),
    path('social-auth/',include('social_django.urls',namespace='social')),  # Social authentication URLs
    path('cart/',include('cart.urls')),
    path('orders/',include('orders.urls')),
    path('inventory/',include('inventory.urls')),
    path('payment/',include('payment.urls')),
    path('wishlist/',include('wishlist.urls')),
    path('wallet/',include('wallet.urls')),
    path('captcha/', include('captcha.urls')),
    path('coupon/', include('coupon.urls')),
    path('offer/',include('offer.urls')),
]

if settings.DEBUG:
    urlpatterns +=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
  


# {{ product.image.url }} use this to load the images in the template.

