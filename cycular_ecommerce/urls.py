"""
URL Configuration for Cycular eCommerce Project.

This file maps URL paths to views for the project. 
Refer to the Django documentation for more details on URL routing:
https://docs.djangoproject.com/en/5.0/topics/http/urls/

URL Patterns:
- Admin: /admin/
- Core app: /
- User app: /user/
- Seller app: /seller/
- Products app: /products/
- Social Authentication: /social-auth/
- Cart: /cart/
- Orders: /orders/
- Payment: /payment/
- Wishlist: /wishlist/
- Wallet: /wallet/
- Captcha: /captcha/
- Coupon: /coupon/
- Offer: /offer/
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
  