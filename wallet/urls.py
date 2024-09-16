from django.urls import path
from . import views
from captcha.helpers import captcha_image_url
from django.http import JsonResponse
from captcha.models import CaptchaStore    

app_name='wallet'

urlpatterns=[
   path('',views.wallet_page,name='wallet-page'),
   path('cancell-order-item/<int:order_item_id>',views.cancell_order_item,name='cancell-order-item'),
   path('captcha-image-url/', lambda request: JsonResponse({
        'captcha_image_url': captcha_image_url(CaptchaStore.generate_key())
    }), name='captcha-image-url'),
]