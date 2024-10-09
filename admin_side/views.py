from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from orders.models import OrderItem,Order
from django.db.models import F
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from django.utils import timezone
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from wallet.models import Wallet,Transaction
from products.models import Brand,Category,ProductVariant
from django.db.models import Sum

from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
import json
from django.db.models.functions import TruncHour
from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

#############################   seller home    ########################################################


@login_required(login_url='admin_side:seller-login')
@never_cache
def SellerHome(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('core:index')
    # User statistics
    user_count = User.objects.filter(is_superuser=False).count()
    active_user_count = User.objects.filter(is_superuser=False, is_active=True).count()
    inactive_user_count = User.objects.filter(is_superuser=False, is_active=False).count()

    # Product statistics
    product_variant_count = ProductVariant.objects.count()  # Count product variants
    brand_count = Brand.objects.count()  # Count brands
    category_count = Category.objects.count()  # Count categories

    # Query the top 10 best-selling products
    top_selling_products = (
        OrderItem.objects.filter(order_item_status='Delivered')
        .values('product_variant')
        .annotate(total_quantity_sold=Sum('quantity'),total_revenue=Sum(F('quantity') * F('price')))
        .order_by('-total_quantity_sold')[:10]
    )
     # Print the total_quantity_sold for debugging
    for item in top_selling_products:
        print(f"Product Variant ID: {item['product_variant']}, Total Quantity Sold: {item['total_quantity_sold']}")
    
     # Prepare a list of product variants with their total quantity sold
    product_variants = []
    for item in top_selling_products:
        variant = ProductVariant.objects.get(id=item['product_variant'])
        product_variants.append({
            'variant': variant,
            'total_quantity_sold': item['total_quantity_sold'],
            'total_revenue': item['total_revenue'],
            'color': variant.color,  # Add color
            'size': variant.size,     # Add size
        })
    print(product_variants)
    # Prepare context for rendering

    # Query the top 10 best-selling categories
    top_selling_categories = (
        OrderItem.objects.filter(order_item_status='Delivered')
        .values('product_variant__product__category')  # Group by category
        .annotate(total_quantity_sold=Sum('quantity'))  # Sum up the quantity sold
        .order_by('-total_quantity_sold')[:10]  # Order by total sold, limit to top 10
    )

    # Prepare a list of categories with their total quantity sold
    categories = []
    for item in top_selling_categories:
        category = Category.objects.get(id=item['product_variant__product__category'])
        categories.append({
            'category': category,
            'total_quantity_sold': item['total_quantity_sold'],
        })
    
    # Query the top 10 best-selling brands
    top_selling_brands = (
        OrderItem.objects.filter(order_item_status='Delivered')  # Filter delivered orders
        .values('product_variant__product__brand')  # Group by brand
        .annotate(total_quantity_sold=Sum('quantity'))  # Sum the quantities sold
        .order_by('-total_quantity_sold')[:10]  # Order by total sold and limit to top 10
    )

    # Prepare a list of brands with their total quantity sold
    brands = []
    for item in top_selling_brands:
        brand = Brand.objects.get(id=item['product_variant__product__brand'])
        brands.append({
            'brand': brand,
            'total_quantity_sold': item['total_quantity_sold'],
            'description': brand.description,
        })


    

    # Get filter option (default is 'month')
    filter_option = request.GET.get('filter', 'month')
    now = timezone.now()

    # Initialize labels and data
    labels = []
    data = []

    # Apply the filter based on the selected time period
    if filter_option == 'day':
        # Get today's date range
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Query today's orders
        order_data = (
            OrderItem.objects.filter(order__order_date__range=(start_of_day, end_of_day))
            .annotate(time_period=TruncHour('order__order_date'))
            .values('time_period')
            .annotate(total_price=Sum('price'))
            .order_by('time_period')
        )

        # Generate labels for the current day (hourly)
        labels = [f"{now.strftime('%Y-%m-%d')} {hour}:00" for hour in range(24)]
        
        # Prepare data for the chart
        data_dict = {label: 0 for label in labels}  # Initialize all hourly data to zero
        for item in order_data:
            time_label = item['time_period'].strftime('%Y-%m-%d %H:00')
            if time_label in data_dict:
                data_dict[time_label] = float(item['total_price'])

        data = [data_dict[label] for label in labels]

    elif filter_option == 'week':
        # Get the start and end of the current week
        start_of_week = now - timezone.timedelta(days=now.weekday())  # Monday
        end_of_week = start_of_week + timezone.timedelta(days=6)  # Sunday

        # Query this week's orders
        order_data = (
            OrderItem.objects.filter(order__order_date__range=(start_of_week, end_of_week))
            .annotate(time_period=TruncDay('order__order_date'))
            .values('time_period')
            .annotate(total_price=Sum('price'))
            .order_by('time_period')
        )

        # Generate labels for the days of the week (Monday to Sunday)
        labels = [(start_of_week + timezone.timedelta(days=i)).strftime('%A') for i in range(7)]

        # Prepare data for the chart
        data_dict = {label: 0 for label in labels}
        for item in order_data:
            time_label = item['time_period'].strftime('%A')
            if time_label in data_dict:
                data_dict[time_label] = float(item['total_price'])

        data = [data_dict[label] for label in labels]

    elif filter_option == 'month':
        # Get the current month's range
        start_of_month = now.replace(day=1)
        end_of_month = (start_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        # Query this month's orders
        order_data = (
            OrderItem.objects.filter(order__order_date__range=(start_of_month, end_of_month))
            .annotate(time_period=TruncDay('order__order_date'))
            .values('time_period')
            .annotate(total_price=Sum('price'))
            .order_by('time_period')
        )

        # Generate labels for all days in the current month
        days_in_month = (end_of_month - start_of_month).days + 1
        labels = [(start_of_month + timezone.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_in_month)]

        # Prepare data for the chart
        data_dict = {label: 0 for label in labels}
        for item in order_data:
            time_label = item['time_period'].strftime('%Y-%m-%d')
            if time_label in data_dict:
                data_dict[time_label] = float(item['total_price'])

        data = [data_dict[label] for label in labels]

    elif filter_option == 'year':
        # Get the current year's range
        start_of_year = now.replace(month=1, day=1)
        end_of_year = now.replace(month=12, day=31)

        # Query this year's orders
        order_data = (
            OrderItem.objects.filter(order__order_date__range=(start_of_year, end_of_year))
            .annotate(time_period=TruncMonth('order__order_date'))
            .values('time_period')
            .annotate(total_price=Sum('price'))
            .order_by('time_period')
        )

        # Generate labels for all months in a year (January to December)
        labels = [datetime(now.year, month, 1).strftime('%Y-%m') for month in range(1, 13)]

        # Prepare data for the chart
        data_dict = {label: 0 for label in labels}
        for item in order_data:
            time_label = item['time_period'].strftime('%Y-%m')
            if time_label in data_dict:
                data_dict[time_label] = float(item['total_price'])

        data = [data_dict[label] for label in labels]

    # Debugging: Print order_data to check results
    print(f"Filter Option: {filter_option}")
    print(f"Order Data: {list(order_data)}")  # Print actual data for debugging
    print(f"Labels: {labels}")
    print(f"Data: {data}")
        
   
    context = {
        'user_count': user_count,
        'product_variant_count': product_variant_count,
        'brand_count': brand_count,
        'category_count': category_count,
        'active_user_count': active_user_count,
        'inactive_user_count': inactive_user_count,
        'product_variants': product_variants,
        'top_selling_categories': categories,
        'top_selling_brands': brands,
        
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'filter_option': filter_option, 
    }
    # Render the template with the context
    return render(request, 'admin_side/admin_dashboard.html', context)

#############################   seller login  ########################################################

@never_cache
def SellerLogin(request):
    if request.user.is_authenticated:
        return redirect('admin_side:seller-home')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.info(request,"Please fill the following...",extra_tags='admin')
            return render(request,'admin_side/admin_login.html')
        admin_user = authenticate(request, email=email, password=password)
        if admin_user is not None:
            if admin_user.is_superuser:
                login(request, admin_user)
                messages.success(request, "You have logged in successfully.", extra_tags='admin')
                return redirect('admin_side:seller-home')
            else:
                messages.error(request, "You don't have permission to access the admin panel.",extra_tags='admin')
        else:
            messages.error(request, "Invalid email or password.",extra_tags='admin')
    return render(request, 'admin_side/admin_login.html')

#############################   seller logout  ########################################################

def SellerLogout(request):
    logout(request)
    messages.success(request, 'You have logged out successfully',extra_tags='admin')
    return redirect('admin_side:seller-login')

#############################   user management  ########################################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def UserManagement(request):
    if not request.user.is_superuser:
        return redirect('core:index')

    # Get the search query
    query = request.GET.get('q', '')

    customers=User.objects.filter(is_superuser=False)

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |Q(email__icontains=query)
        )
    # Set up pagination.
    paginator = Paginator(customers, 5)  
    page = request.GET.get('page')
    try:
        customers_paginated = paginator.page(page)
    except PageNotAnInteger:
        customers_paginated = paginator.page(1)
    except EmptyPage:
        customers_paginated = paginator.page(paginator.num_pages)
    context={
        'customers':customers_paginated ,
        
    }
    return render(request,'admin_side/user_management.html',context)

#############################   category management  ########################################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def UserView(request,user_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    user = get_object_or_404(User, id=user_id)
    context={
        'user':user
    }
    return render(request,'admin_side/user-view.html',context)

############################  order management  ###################

@login_required(login_url='admin_side:seller-login')
@never_cache
def OrderManagement(request):
    order_items = OrderItem.objects.all().order_by('-order__order_date')
    # Check if there is a search term
    search_term = request.GET.get('search', '')
    if search_term:
        order_items = order_items.filter(product_variant__product__name__icontains=search_term)

    paginator= Paginator(order_items,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        order_item_id=request.POST.get('order_item_id')
        new_status=request.POST.get('status')
        page_number=request.GET.get('page')
        page_obj=paginator.get_page(page_number)
        #update status of sepecific order item
        order_item = OrderItem.objects.get(id=order_item_id)
        order = order_item.order  
        
        #if the status is cancell at that time we need to resotore the product count of the cancelled products.
        if new_status == 'Cancelled' and order_item.order_item_status != 'Cancelled':
            #restore logic...
            order_item.product_variant.stock=F('stock')+order_item.quantity
            order_item.product_variant.save()

            # Fetch or create the user's wallet
            wallet, created = Wallet.objects.get_or_create(user=order.user)

            # Check if the payment method was not 'cash_on_delivery'
            if order.payment_method != 'cash_on_delivery':
              

                # Add the order item price to the wallet balance
                wallet.balance += Decimal(order_item.price)
                wallet.save()

                # Log the transaction in the wallet
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='credit',
                    transaction_purpose='refund',
                    transaction_amount=Decimal(order_item.effective_price()),
                    description=f"{order_item.product_variant.product.name} (Qty.{order_item.quantity})was cancelled by Cycular-Admin",
                )
                
                # Add a success message for refund
                messages.success(request, f"Order item {order_item.product_variant.product.name} cancelled and refunded to the User wallet.")

            else:
                # Log a 'null' transaction if it's Cash on Delivery
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='null',  # Null transaction type to record but not affect balance
                    transaction_purpose='refund',
                    transaction_amount=Decimal(0),
                    description=f"{order_item.product_variant.product.name} (Qty.{order_item.quantity}) was cancelled by Cycular-Admin. COD order - no refund to wallet.",
                )
                # Add a message if payment was cash on delivery (no refund)
                messages.info(request, f"Order item {order_item.product_variant.product.name} cancelled. No refund issued (Cash on Delivery) to the User.")
        
         # If status is 'Returned', always refund the amount
        elif new_status == 'Returned' and order_item.order_item_status != 'Returned':
            # Restore stock for returned products
            order_item.product_variant.stock = F('stock') + order_item.quantity
            order_item.product_variant.save()

            # Fetch or create the user's wallet
            wallet, created = Wallet.objects.get_or_create(user=order.user)

            # Refund the amount to the wallet
            wallet.balance += Decimal(order_item.price)
            wallet.save()

            # Log the return transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='credit',
                transaction_purpose='returned',
                transaction_amount=Decimal(order_item.effective_price()),
                description=f"{order_item.product_variant.product.name} (Qty.{order_item.quantity}) was returned by Cycular-Admin.",
            )

            # Add a success message for refund on return
            messages.success(request, f"Order item {order_item.product_variant.product.name} returned and refunded to the User wallet.")

        order_item.order_item_status = new_status
        order_item.save()
        return redirect('admin_side:order-management')
     # Define status choices directly from the model field
    status_choices = OrderItem._meta.get_field('order_item_status').choices

    context={
        'order_items':page_obj,
        'status_choices': status_choices,
    }
    return render(request,'admin_side/order_management.html',context)

########################## Views for handle the sales report  ####################

@login_required(login_url='admin_side:seller-login')
@never_cache
def sales_report(request):
    # Fetching orders
    orders = Order.objects.all()
    # Get the search query
    query = request.GET.get('q', '')

    customers=User.objects.filter(is_superuser=False)

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |Q(email__icontains=query)
        )
        # Filter orders by the customers matching the search query
        if customers.exists():
            orders = orders.filter(user__in=customers)
            
    # Apply filtering based on query parameters
    date_range = request.GET.get('date_range')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter based on date range selection
    if date_range == 'custom' and start_date and end_date:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        orders = orders.filter(order_date__range=[start_date, end_date])
    elif date_range == 'last_1_day':
        orders = orders.filter(order_date__gte=timezone.now() - timezone.timedelta(days=1))
    elif date_range == 'last_1_week':
        orders = orders.filter(order_date__gte=timezone.now() - timezone.timedelta(weeks=1))
    elif date_range == 'last_1_month':
        orders = orders.filter(order_date__gte=timezone.now() - timezone.timedelta(days=30))
    elif date_range == 'last_1_year':
        orders = orders.filter(order_date__gte=timezone.now() - timezone.timedelta(days=365))
    
    # Calculate totals
    total_orders = orders.count()
    total_sales = sum(order.total_price for order in orders)
    total_discounts = sum(order.coupon_discount_total for order in orders)
    
    # Paginate the orders (based on Order model)
    page_number = request.GET.get('page')
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    paginated_orders = paginator.get_page(page_number)  # Change order_items to paginated_orders

    # Check if the user requested a PDF download
    if 'download_pdf' in request.GET:
        return generate_sales_report_pdf(orders, total_orders, total_sales, total_discounts, date_range, start_date, end_date)
  
    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_discounts': total_discounts,
        'orders': paginated_orders,
    }
    return render(request, 'admin_side/admin_sales_report.html', context)


########################  view for download sales reoprt   ##########################


def generate_sales_report_pdf(orders, total_orders, total_sales, total_discounts, date_range=None, start_date=None, end_date=None):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    
    # Set the filename to include the current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="Cycular_sales_report_{current_date}.pdf"'

    # Buffer to hold PDF data
    buffer = BytesIO()

    # Create a PDF document using ReportLab's SimpleDocTemplate
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []  # List to hold the PDF elements

    # Define styles for the PDF
    styles = getSampleStyleSheet()

    # Add a logo (image), using your specified path
    logo_path = 'static/assets/images/cycular/cycular_black.png'  # Update to your logo path
    try:
        logo = Image(logo_path, width=100, height=100)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except:
        pass  # If no logo found, skip adding the image

    # Title: Cycular Sales Report
    title = Paragraph("<strong>Cycular Sales Report</strong>", styles['Title'])
    elements.append(title)

    # Display the report period
    if date_range == 'custom' and start_date and end_date:
        period_text = f"Report Period: Custom Date Range ({start_date} to {end_date})"
    elif date_range == 'last_1_day':
        period_text = "Report Period: Last 1 Day"
    elif date_range == 'last_1_week':
        period_text = "Report Period: Last 1 Week"
    elif date_range == 'last_1_month':
        period_text = "Report Period: Last 1 Month"
    elif date_range == 'last_1_year':
        period_text = "Report Period: Last 1 Year"
    else:
        period_text = "Report Period: All Orders"

    period = Paragraph(period_text, styles['Normal'])
    elements.append(period)

    # Space before the total orders/sales/discounts summary
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Total Orders, Sales, Discounts
    summary_text = f"""
        <strong>Total Orders:</strong> {total_orders}<br/>
        <strong>Total Sales:</strong> Rs. {total_sales}<br/>
        <strong>Total Discounts:</strong> Rs. {total_discounts}<br/>
    """
    summary = Paragraph(summary_text, styles['Normal'])
    elements.append(summary)

    # Space before the table
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Create a table with order details
    data = [['Order ID', 'Order Date', 'Total Price (Rs.)', 'Discounts (Rs.)']]  # Header row

    # Add the orders data to the table
    for order in orders:
        data.append([str(order.id), str(order.order_date.strftime('%Y-%m-%d')), f"Rs. {order.total_price}", f"Rs. {order.coupon_discount_total}"])

    # Table styling: Add lines around the table
    table = Table(data, colWidths=[100, 150, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#009efb")),  # Blue background for header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # White text for header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),  # Light gray background for rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Lines around cells
    ]))
    
    elements.append(table)

    # Space before the copyright notice
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Add the copyright notice
    copyright_text = "<small>© Cycular. All rights reserved.</small>"
    copyright_notice = Paragraph(copyright_text, styles['Normal'])
    elements.append(copyright_notice)

    # Build the PDF with the elements
    pdf.build(elements)

    # Write the PDF data to the response
    pdf_data = buffer.getvalue()
    buffer.close()
    response.write(pdf_data)

    return response
