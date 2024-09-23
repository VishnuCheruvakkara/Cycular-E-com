from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ProductVariantOffer, ProductVariant,Brand,BrandOffer
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.

def offer_page(request):
    product_variants = ProductVariant.objects.select_related('product', 'size').all()
    # Fetch product variant offers related to those variants
    product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').filter(status=True)
    brands = Brand.objects.filter(status=True)


    
    context = {
        'product_variants': product_variants,
        'product_variant_offers': product_variant_offers,
        'brands': brands, 
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
            product_variants = ProductVariant.objects.all()
            product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').filter(status=True)
            return render(request, 'offer/offer-management.html', {
                'product_variants': product_variants,
                'errors': errors,
                'offer_name': offer_name,
                'discount_percentage': discount_percentage,
                'end_date': end_date,
                'product_variant_offers': product_variant_offers,
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
    context = {
        'product_variants': product_variants,
        'product_variant_offers': product_variant_offers,
        }

    return render(request, 'offer/offer-management.html', context)

################ product variant soft delete  ##############################

def delete_offer(request, offer_id):
    if request.method == 'POST':
        try:
            # Get the offer object
            offer = get_object_or_404(ProductVariantOffer, id=offer_id)

            # Perform soft delete by setting status to False
            offer.status = False
            offer.save()

            # Return success response as JSON
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


####################  add brand offer  ###################


def add_brand_offer(request):
    if request.method == 'POST':
        brand_id = request.POST.get('brand')
        offer_percentage = request.POST.get('offer_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        
        # Validate and create the BrandOffer
        try:
            brand = Brand.objects.get(id=brand_id)
            brand_offer = BrandOffer.objects.create(
                brand=brand,
                offer_name=f"{offer_percentage}% off on {brand.name}",
                discount_percentage=float(offer_percentage),
                start_date=start_date,
                end_date=end_date
            )
            messages.success(request, 'Brand offer added successfully!')
            return redirect('offer:offer-page')  # Replace with your redirect view
        except Exception as e:
            messages.error(request, f'Error adding offer: {str(e)}')

    brands = Brand.objects.all()
    return render(request, 'offer/offer-management.html', {'brands': brands})