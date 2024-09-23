from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ProductVariantOffer, ProductVariant
from django.utils import timezone

# Create your views here.

def offer_page(request):
    product_variants = ProductVariant.objects.select_related('product', 'size').all()
    # Fetch product variant offers related to those variants
    product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').all()
    
    context = {
        'product_variants': product_variants,
        'product_variant_offers': product_variant_offers,
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
            product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').all()
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
    product_variant_offers = ProductVariantOffer.objects.select_related('product_variant').all()
    context = {
        'product_variants': product_variants,
        'product_variant_offers': product_variant_offers,
        }

    return render(request, 'offer/offer-management.html', context)