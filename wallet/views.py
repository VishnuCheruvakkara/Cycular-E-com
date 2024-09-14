from django.shortcuts import render

# Create your views here.

def wallet_page(request):
    return render(request,'wallet/wallet-page.html')
