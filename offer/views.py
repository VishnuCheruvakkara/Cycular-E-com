from django.shortcuts import render

# Create your views here.

def offer_page(request):
    
    return render(request,'offer/offer-management.html')
