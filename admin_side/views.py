from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from user_side.models import User 
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

# Create your views here.

#############################   seller home    ########################################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def SellerHome(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    return render(request,'admin_side/admin_dashboard.html')

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

@login_required(login_url='admin_side:seller_login')
def UserManagement(request):
    if not request.user.is_superuser:
        return redirect('core:index')

    customers=User.objects.filter(is_superuser=False)
   
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
        
        #if the status is cancell at that time we need to resotore the product count of the cancelled products.
        if new_status == 'Cancelled' and order_item.order_item_status != 'Cancelled':
            #restore logic...
            order_item.product_variant.stock=F('stock')+order_item.quantity
            order_item.product_variant.save()

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


def sales_report(request):
    # Fetching orders
    orders = Order.objects.all()

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
   
    # Check if the user requested a PDF download
    if 'download_pdf' in request.GET:
        return generate_sales_report_pdf(orders, total_orders, total_sales, total_discounts, date_range, start_date, end_date)
  
    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_discounts': total_discounts,
        'orders': orders,
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
    logo_path = 'static/assets/images/cycular/cycular-logo.png'  # Update to your logo path
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
