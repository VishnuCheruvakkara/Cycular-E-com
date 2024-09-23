from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ProductVariantOffer, ProductVariant,Brand,BrandOffer
from django.utils import timezone
from django.http import JsonResponse
import json

# Create your views here.

def offer_page(request):
    product_variants = ProductVariant.objects.select_related('product', 'size').filter(status=True) 
    # Fetch product variant offers related to those variants
    product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').filter(status=True)
    brands = Brand.objects.filter(status=True)
    brand_offers = BrandOffer.objects.filter(status=True)


    
    context = {
        'product_variants': product_variants,
        'product_variant_offers': product_variant_offers,
        'brands': brands, 
        'brand_offers': brand_offers,
    }
    
    return render(request, 'offer/offer-management.html', context)

############### add procut offer to the model  #################3


def add_product_variant_offer(request):
    if request.method == 'POST':
        product_variant_id = request.POST.get('product_variant_id')
        offer_name = request.POST.get('offer_name')
        discount_percentage = request.POST.get('offer_percentage')
        end_date = request.POST.get('end_date')

        errors = {}

        # Validation
        if not product_variant_id:
            errors['product_variant_id'] = "Product variant is required."
        if not offer_name:
            errors['offer_name'] = "Offer name is required."
        if not discount_percentage or not (1 <= int(discount_percentage) <= 100):
            errors['offer_percentage'] = "Offer percentage must be between 1 and 100."
        if not end_date:
            errors['end_date'] = "End date is required."
        elif timezone.datetime.strptime(end_date, '%Y-%m-%d').date() <= timezone.now().date():
            errors['end_date'] = "End date must be later than the current date."

        # If there are errors, return to the modal with errors
        if errors:
            messages.error(request, 'Please correct the error, Add product offer again.')
            product_variants = ProductVariant.objects.filter(status=True)
            product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').filter(status=True)
            brand_offers = BrandOffer.objects.filter(status=True)
            brands = Brand.objects.filter(status=True)
            return render(request, 'offer/offer-management.html', {
                'product_variants': product_variants,
                'brand_offers': brand_offers,
                'errors': errors,
                'form_data': {
                    'offer_name': offer_name,
                    'discount_percentage': discount_percentage,
                    'end_date': end_date,
                },
                'product_variant_offers': product_variant_offers,
                'brands': brands, 
                
            })

        try:
            product_variant = get_object_or_404(ProductVariant, id=product_variant_id)

            # Create the offer for the selected product variant
            ProductVariantOffer.objects.create(
                product_variant=product_variant,
                offer_name=offer_name,
                discount_percentage=float(discount_percentage),
                end_date=end_date
            )
            messages.success(request, 'Offer added successfully!')
            return redirect('offer:offer-page')  # Redirect to the offer page or list

        except Exception as e:
            messages.error(request, f'Error adding offer: {str(e)}')
            return redirect('offer:offer-page')

    # If not POST, render the form (could be modal-triggered, etc.)
    product_variants = ProductVariant.objects.all()  # Assuming you have a list of variants
    product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').filter(status=True)
    brand_offers = BrandOffer.objects.filter(status=True)
    context = {
        'product_variants': product_variants,
        'product_variant_offers': product_variant_offers,
        'brand_offers': brand_offers, 
        }

    return render(request, 'offer/offer-management.html', context)

################ product variant offer  soft delete  ##############################


def soft_delete_product_offer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        offer_id = data.get('offer_id')
        product_offer = get_object_or_404(ProductVariantOffer, id=offer_id)

        # Soft delete by setting the status to False
        product_offer.status = False
        product_offer.save()

        return JsonResponse({'success': True, 'message': 'Product offer deleted successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

####################  add brand offer  ###################
def add_brand_offer(request):
    if request.method == 'POST':
        brand_id = request.POST.get('brand')
        offer_percentage = request.POST.get('offer_percentage')
        end_date = request.POST.get('end_date')

        errors = {}

        # Validate the brand selection
        if not brand_id:
            errors['brand'] = 'Brand is required.'
        else:
            brand = Brand.objects.filter(id=brand_id).first()
            if not brand:
                errors['brand'] = 'Invalid brand selected.'

        # Validate the offer percentage
        if not offer_percentage:
            errors['offer_percentage'] = 'Offer percentage is required.'
        else:
            if offer_percentage.isdigit():
                discount = float(offer_percentage)
                if discount <= 0 or discount > 100:
                    errors['offer_percentage'] = 'Offer percentage must be between 1 and 100.'
            else:
                errors['offer_percentage'] = 'Offer percentage must be a valid number.'

        # Validate the end date
        if not end_date:
            errors['end_date'] = 'End date is required.'
        else:
            # Convert to timezone-aware datetime
            try:
                end_date_obj = timezone.make_aware(timezone.datetime.fromisoformat(end_date))
                if end_date_obj < timezone.now():
                    errors['end_date'] = 'End date must be in the future.'
            except ValueError:
                errors['end_date'] = 'End date is invalid.'

        # If there are errors, re-render the form with errors and existing data
        if errors:
            messages.error(request, 'Please correct the error. Add Brand offer again.')
            brands = Brand.objects.filter(status=True)
            brand_offers = BrandOffer.objects.filter(status=True)
            product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').filter(status=True)
            product_variants = ProductVariant.objects.select_related('product', 'size').filter(status=True) 
            
            # Re-render the form with the existing data
            return render(request, 'offer/offer-management.html', {
                'brands': brands,
                'errors': errors,
                'brand_offers': brand_offers, 
                'product_variant_offers': product_variant_offers,
                'product_variants': product_variants,
                'form_data': {
                    'brand_id': brand_id,
                    'offer_percentage': offer_percentage,
                    'end_date': end_date,
                    
                }
            })

        # Create the BrandOffer if there are no errors
        brand_offer = BrandOffer.objects.create(
            brand=brand,
            offer_name=f"{offer_percentage}% off on {brand.name}",
            discount_percentage=discount,
            end_date=end_date_obj
        )
        messages.success(request, 'Brand offer added successfully!')
        return redirect('offer:offer-page')

    # On GET request, render the form with an empty form
    brands = Brand.objects.all()
    brand_offers = BrandOffer.objects.filter(status=True)
    return render(request, 'offer/offer-management.html', {'brands': brands,'brand_offers': brand_offers})

#####################  soft delete of  #########################


def soft_delete_brand_offer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        offer_id = data.get('offer_id')
        brand_offer = get_object_or_404(BrandOffer, id=offer_id)
        
        # Soft delete by setting the status to False
        brand_offer.status = False
        brand_offer.save()

        return JsonResponse({'success': True, 'message': 'Brand offer deleted successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})
