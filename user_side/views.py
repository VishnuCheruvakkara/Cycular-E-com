from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegisterForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.conf import settings
import random
from .utils.gmail import send_otp_email
from django.utils import timezone
from datetime import timedelta,datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Address
from django.views.decorators.cache import never_cache
from orders.models import Order,OrderItem
from django.http import FileResponse, Http404
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import os
from datetime import datetime, timedelta
import tempfile
User = get_user_model()
from .validation import validate_address_data


###########################  user sign-up  #####################################

import uuid

def generate_unique_session_key():
    return str(uuid.uuid4())

@never_cache
def register_view(request):
    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid(): #check the all validation condition for the submitted data
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')

            session_key=generate_unique_session_key() #custom function called for generate the session key : above

            otp = generate_otp()

            otp_created_at = timezone.now()
           
            request.session[session_key]={
                'otp':otp,
                'otp_created_at':otp_created_at.isoformat(),#for serialization
                'email':email,
                'username':username,
                'password':password,
            }

            send_otp_email(email,otp,username)
            request.session['user_registration_data']=session_key
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('user_side:otp')
        
    else : 
        form=UserRegisterForm()

    context={
        'form':form,
    }
   
    return render(request,"user_side/sign-up.html",context)

###########################  login section #############################################

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "Hello, you are already logged in.", extra_tags='user')
        return redirect("core:index")
    
    if request.method == "POST":
        email = request.POST.get("signin-email")
        password = request.POST.get("signin-password")

        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "You are logged in.", extra_tags='user')
                return redirect('core:index')
            else:
                messages.error(request, 
                               "Your account has been blocked. Please contact our support team for assistance. Thank you.", 
                               extra_tags='user')
                return redirect('user_side:sign-in')  # Fixed typo from 'idex' to 'index'
        else:
            messages.warning(request, "Invalid email or password Please try again.", extra_tags='user')
    
    return render(request, 'user_side/sign-in.html')

###########################  logout section  #########################################

def logout_view(request):
    logout(request)
    messages.info(request,"You logged out")
    return redirect("user_side:sign-in")

###########################  otp page section  #########################################

@never_cache
def otp_view(request):

    #cheker

    session_key=request.session.get('user_registration_data')
    session_data=request.session.get(session_key)


    if (not session_key) or (session_key not in request.session):
        messages.error(request, 'No data found. Please sign-up again.')
        return redirect('user_side:sign-up')

    if request.method=='POST':
        otp1=request.POST.get('otp1','0')
        otp2=request.POST.get('otp2','0')
        otp3=request.POST.get('otp3','0')
        otp4=request.POST.get('otp4','0')
        otp5=request.POST.get('otp5','0')
        otp6=request.POST.get('otp6','0')
        entered_otp=f"{otp1}{otp2}{otp3}{otp4}{otp5}{otp6}"
        
        session_data=request.session.get(session_key)
        if not session_data:
            messages.error(request,'No data found. Please sign-up again.')
            return redirect('user_side:sign-up')
        
        stored_otp=session_data.get('otp')
        otp_created_at=datetime.fromisoformat(session_data.get('otp_created_at'))

        if timezone.now() - otp_created_at > timedelta(seconds=OTP_EXPIRY_SECONDS):
            messages.error(request,'OTP has expired, Please checkout the resend OTP.')
            return redirect('user_side:otp')

        if entered_otp == stored_otp:
            email=session_data.get('email')
            username=session_data.get('username')
            password=request.POST.get('password1')

            # Attempt to retrieve the password from the session data
            password = session_data.get('password')
            
            user=User.objects.create_user(username=username,email=email,password=password)

            # Attempt to retrieve the password from the session data
            password = session_data.get('password')

            user.save()
            if user is not None:
                backend = 'django.contrib.auth.backends.ModelBackend'
                login(request,user,backend=backend)
                del request.session[session_key]
                del request.session['user_registration_data']
                messages.success(request,'OTP Registration was successful.  you are now logged in.')
                return redirect('core:index')
            else:
                messages.error(request,'User creation failed. Please try again.')
                return redirect('user_side:sign-in')
        else:
            messages.error(request,'Invalid OTP : Entered otp is not match, check-otp resend OTP.')

    return render(request,'user_side/otp.html')

###########################   generating otp   ########################################

OTP_EXPIRY_SECONDS=300

def generate_otp():
    return str(random.randint(100000,999999))

###########################   resend otp   ########################################

def resend_otp(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error'}, status=400)

    session_key = request.session.get('user_registration_data')
    if not session_key or session_key not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Session expired. Please sign up again.'
        }, status=400)

    session_data = request.session.get(session_key)

    email = session_data.get('email')
    username = session_data.get('username')

    new_otp = generate_otp()
    send_otp_email(email, new_otp, username)

    session_data['otp'] = new_otp
    session_data['otp_created_at'] = timezone.now().isoformat()
    request.session[session_key] = session_data
    request.session.modified = True

    return JsonResponse({
        'status': 'success',
        'message': f'OTP successfully resent to {email}'
    })


###############################  to handle the user status through admin page  ##########################

@require_POST
def toggle_user_status(request):
    user_id = request.POST.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'success': True, 'is_active': user.is_active})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})

############################### user accout-dashboard ##########################

@login_required(login_url='user_side:sign-in')
@never_cache
def user_dash_board(request):
    addresses=Address.objects.filter(user=request.user)
    orders=Order.objects.filter(user=request.user)

    context={
        'user':request.user,
        'addresses':addresses,
        'orders':orders,
    }
    return render(request,'user_side/user-dash-board.html',context)

############################### update or change username ##########################

@login_required(login_url='user_side:sign-in')
@never_cache
def change_username(request):
    errors = {}
    show_modal=False
    if request.method=='POST':
        new_username=request.POST.get('username')
        current_username=request.user.username
        if not new_username:
            errors['username']='Username cannot be empty.'
        elif not re.match(r'^[A-Za-z]+( [A-Za-z]+){0,5}$', new_username):
            errors['username'] = 'Username must contain only letters and at most one space between words.'
        elif len(new_username)<3 :
            errors['username']='Username contain atleast 3 letters.'
        elif User.objects.filter(username=new_username).exclude(username=current_username).exists():
            errors['username']='This username is already taken.'

        if not errors:
            user=request.user
            user.username=new_username
            user.save()
            messages.success(request,'Your username has been updated successfully!')
            return redirect('user_side:user-dash-board')
        else:
            show_modal=True
            #dont close modal when there is any validation error found

    context={
        'errors':errors,
        'user':request.user,
        'show_modal':show_modal
    }

    return render(request,'user_side/user-dash-board.html',context)

###################### update or change the email address of the current uesr by sending otp to the current email address ##########################

@login_required(login_url='user_side:sign-in')
@never_cache
def email_change_view(request):

    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        request.session['new_email'] = new_email

        try:
            validate_email(new_email)
        except ValidationError:
            messages.error(request, 'Invalid email address. Please enter a valid email.')
            return redirect('user_side:user-dash-board')

        if User.objects.filter(email=new_email).exists():
            messages.error(request, 'This email address is already in use. Please choose a different email.')
            return render(request, 'user_side/user-dash-board.html')

        otp = random.randint(100000, 999999)

        send_otp_email(
            to_email=new_email,
            otp=otp,
            username=request.user.username,
            purpose="Email Change"
        )

        request.session['email_change_otp'] = otp
        request.session['otp_generated_time'] = timezone.now().isoformat()

        messages.success(request, 'An OTP has been sent to your new email address.')
        return redirect('user_side:email-change-otp-view')

    return render(request, 'user_side/user-dash-board.html')


##########################  verify otp for the email change   #################################

@login_required(login_url='user_side:sign-in')
@never_cache
def email_change_otp_view(request):
    error_message = ""

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        current_time = timezone.now()
        otp_generated_time = request.session.get('otp_generated_time')
        otp_pattern = re.compile(r'^\d{6}$')

        if not otp_pattern.match(entered_otp):
            error_message = "Please enter a valid 6-digit OTP."

        if entered_otp == str(request.session.get('email_change_otp')) and otp_generated_time:
            otp_generated_time = timezone.datetime.fromisoformat(otp_generated_time)

            if (current_time - otp_generated_time).total_seconds() <= OTP_EXPIRY_SECONDS:
                user = request.user
                user.email = request.session.get('new_email')
                user.save()

                request.session.pop('email_change_otp', None)
                request.session.pop('otp_generated_time', None)
                request.session.pop('new_email', None)

                messages.success(request, "Your Email has been successfully updated.")
                return redirect('user_side:user-dash-board')
            else:
                messages.error(request, "The OTP has been expired.Please check the resend otp for a new otp.")
        else:
            messages.error(request, "The OTP you entered is incorrect.")

    return render(request, 'user_side/email-change-otp.html', {'error_message': error_message})

########################### resend otp for the change email for the user #######################

@login_required(login_url='user_side:sign-in')
@never_cache
def email_change_resend_otp_view(request):

    new_email = request.session.get('new_email')
    if not new_email:
        messages.error(request, 'Email address is not available.')
        return redirect('user_side:user-dash-board')

    otp = random.randint(100000, 999999)

    send_otp_email(
        to_email=new_email,
        otp=otp,
        username=request.user.username,
        purpose="Email Change"
    )

    request.session['email_change_otp'] = otp
    request.session['otp_generated_time'] = timezone.now().isoformat()

    messages.success(request, 'New OTP has been sent to your email address.')
    return redirect('user_side:email-change-otp-view')

##########################  update the password of the logined user  ##################################

@login_required(login_url='user_side:sign-in')
@never_cache
def password_change_view(request):
    error_message_password_change = []

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('user_side:user-dash-board')

        if current_password == new_password:
            messages.error(request, 'New password cannot be same as the old password. try again...')
            return redirect('user_side:user-dash-board')

        if new_password != confirm_password:
            error_message_password_change.append('Entered passwords do not match.')

        if len(new_password) < 8:
            error_message_password_change.append('Password must be at least 8 characters long.')

        if not re.search(r'[A-Z]', new_password):
            error_message_password_change.append('Password must contain at least one uppercase letter.')

        if not re.search(r'[a-z]', new_password):
            error_message_password_change.append('Password must contain at least one lowercase letter.')

        if not re.search(r'[0-9]', new_password):
            error_message_password_change.append('Password must contain at least one digit.')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            error_message_password_change.append('Password must contain at least one special character.')

        if error_message_password_change:
            messages.error(request, 'Password validation error found!,Please try again...')
            return render(
                request,
                'user_side/user-dash-board.html',
                {'error_message_password_change': error_message_password_change}
            )

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('user_side:user-dash-board')

        otp = random.randint(100000, 999999)

        request.session['password_change_otp'] = otp
        request.session['password_change_otp_generated_time'] = timezone.now().isoformat()
        request.session['password_change_new_password'] = new_password

        send_otp_email(
            to_email=user.email,
            otp=otp,
            username=user.username,
            purpose="Password Change"
        )

        messages.info(request, 'An OTP has been sent to your email address.')
        return redirect('user_side:password-change-otp-view')

    return render(
        request,
        'user_side/user-dash-board.html',
        {'error_message_password_change': error_message_password_change}
    )

########################## varify otp for the password change  ############################

@login_required(login_url='user_side:sign-in')
@never_cache
def password_change_otp_view(request):
    error_message_password = ""

    if request.method == 'POST':
        entered_otp = request.POST.get('otp_password')
        current_time = timezone.now()
        otp_generated_time = request.session.get('password_change_otp_generated_time')
        new_password = request.session.get('password_change_new_password')

        otp_pattern = re.compile(r'^\d{6}$')

        if not otp_pattern.match(entered_otp):
            error_message_password = "Please enter a valid 6-digit OTP."
        elif entered_otp == str(request.session.get('password_change_otp')) and otp_generated_time:
            otp_generated_time = timezone.datetime.fromisoformat(otp_generated_time)

            if (current_time - otp_generated_time).total_seconds() <= OTP_EXPIRY_SECONDS:
                user = request.user
                user.set_password(new_password)
                user.save()

                request.session.pop('password_change_otp', None)
                request.session.pop('password_change_otp_generated_time', None)
                request.session.pop('password_change_new_password', None)

                messages.success(
                    request,
                    "Your password has been successfully updated,Please login with new password."
                )
                return redirect('user_side:user-dash-board')
            else:
                messages.error(request, "The OTP has expired. Please request a new OTP.")
        else:
            messages.error(request, "The OTP you entered is incorrect.")

    return render(
        request,
        'user_side/password-change-otp.html',
        {'error_message_password': error_message_password}
    )


###########################  paswword resend otp view   ##################################

@login_required(login_url='user_side:sign-in')
@never_cache
def password_change_resend_otp_view(request):
    user = request.user

    if not user.email:
        messages.error(request, 'Email address is not available.')
        return redirect('user_side:user-dash-board')

    otp = random.randint(100000, 999999)

    send_otp_email(
        to_email=user.email,
        otp=otp,
        username=user.username,
        purpose="Password Change"
    )

    request.session['password_change_otp'] = otp
    request.session['password_change_otp_generated_time'] = timezone.now().isoformat()

    messages.success(request, 'A new OTP has been sent to your email address.')
    return redirect('user_side:password-change-otp-view')

#Adress management section down below...
#########################  add address view  ####################

@login_required(login_url='user_side:sign-in')
@never_cache
def add_address(request):

    errors = {}  # Dictionary to hold error messages
    form_data = {}

    # Fetch all addresses of the logged-in user
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        errors, data = validate_address_data(request.POST)
        form_data = request.POST
        # If no errors, create the address
        if not errors:
            Address.objects.create(user=request.user, **data)
            messages.success(request, 'Address added successfully.')
            return redirect('user_side:user-dash-board')
        else:
            messages.error(request, 'Please correct the errors in Add address form.')

    context = {
        'errors': errors,
        'form_data': form_data,
        'addresses':addresses,
        'open_add_address_modal': bool(errors)
    }

    return render(request, 'user_side/user-dash-board.html', context)

#######################  edit address  ##########################

@login_required(login_url='user_side:sign-in')
@never_cache
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    edit_errors = {}

    if request.method == 'POST':
        errors, data = validate_address_data(request.POST)

        if not errors:
            for field, value in data.items():
                setattr(address, field, value)
            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('user_side:user-dash-board')
        else:
            edit_errors = {address_id: errors}
            messages.error(request, 'Please correct the errors in Edit address form.')

    # Only pass edit_address_id if there are errors
    context = {
        'addresses': Address.objects.filter(user=request.user),
        'edit_errors': edit_errors,
        'edit_address_id': address_id if edit_errors else None,
    }
    return render(request, 'user_side/user-dash-board.html', context)

#########################  delete user address  ######################

@login_required(login_url='user_side:sign-in')
@never_cache
def delete_address(request, address_id):
    # Get the address object that belongs to the logged-in user or 404 if not found
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        # Delete the address
        address.delete()
        messages.success(request, 'Address has been deleted successfully.')
        return redirect('user_side:user-dash-board')  # Redirect to the desired page after deletion

    # If the method is not POST, show an error or handle appropriately
    messages.error(request, 'Invalid request method. Please use the delete button provided.')
    return redirect('user_side:user-dash-board')

################### forget password section  ######################

@never_cache
def forget_password(request):
    """
    View for initiating the forget password process by entering the user's email.
    """
    if request.method == 'POST':
        current_email = request.POST.get('current_email')

        # Validate the entered email
        try:
            validate_email(current_email)
        except ValidationError:
            messages.error(request, 'Invalid email address. Please enter a valid email.')
            return redirect('user_side:forget-password')

        # Check if the email exists in the database
        if not User.objects.filter(email=current_email).exists():
            messages.error(request, 'The email address does not exist, try again...')
            return redirect('user_side:forget-password')

        # Generate and send OTP
        otp = random.randint(100000, 999999)
        send_otp_email(
            to_email=current_email,
            otp=otp,
            username="User",
            purpose="Forget Password"
        )

        # Store the OTP and generation time in the context
        request.session['forget_password'] = {
            'current_email': current_email,
            'otp': otp,
            'otp_generated_time': timezone.now().isoformat()
        }

        messages.success(request, 'An OTP has been sent to the entered email address.')
        return redirect('user_side:forget-password-otp')

    return render(request, 'user_side/forget-password-1.html')

############################   forget password otp send page   #########################

@never_cache
def forget_password_otp(request):
    """
    View for OTP verification during the forget password process.
    """
    error_message_forget = ""

    if request.method == 'POST':
        entered_otp = request.POST.get('forget-otp')
        current_time = timezone.now()

        # Get OTP data from session
        data = request.session.get('forget_password')

        if not data:
            messages.error(
                request,
                "Session expired or no email associated. Please restart the forget password process."
            )
            return redirect('user_side:forget-password')

        stored_otp = str(data.get('otp'))
        otp_generated_time = timezone.datetime.fromisoformat(
            data.get('otp_generated_time')
        )

        # Validate OTP format
        otp_pattern = re.compile(r'^\d{6}$')
        if not otp_pattern.match(entered_otp):
            error_message_forget = "Please enter a valid 6-digit OTP."
            return render(
                request,
                'user_side/forget-password-2.html',
                {'error_message_forget': error_message_forget}
            )

        # Check OTP correctness
        if entered_otp != stored_otp:
            messages.error(request, "The OTP you entered is incorrect.")
            return redirect('user_side:forget-password-otp')

        # Check OTP expiry
        if (current_time - otp_generated_time).total_seconds() > OTP_EXPIRY_SECONDS:
            messages.error(request, "The OTP has expired. Please request a new OTP.")
            return redirect('user_side:forget-password-otp')
        
        # OTP is valid
        request.session['forget_password']['otp_verified'] = True
        request.session.modified = True

        # OTP is valid
        messages.success(request, "OTP verified. Please set a new password.")
        return redirect('user_side:forget-password-set')

    return render(
        request,
        'user_side/forget-password-2.html',
        {'error_message_forget': error_message_forget}
    )

##########################  forget password resend otp #######################

@never_cache
def forget_password_resend_otp(request):
    # Get forget-password data from session
    data = request.session.get('forget_password')

    if not data:
        messages.error(
            request,
            'Session expired or no email associated. Please restart the forget password process.'
        )
        return redirect('user_side:forget-password')

    current_email = data.get('current_email')

    if not current_email:
        messages.error(
            request,
            'No email found. Please restart the forget password process.'
        )
        return redirect('user_side:forget-password')

    # Generate new OTP
    new_otp = random.randint(100000, 999999)

    # Send OTP email
    send_otp_email(
        to_email=current_email,
        otp=new_otp,
        username="User",
        purpose="Forget Password"
    )

    # Update session data
    request.session['forget_password'] = {
        'current_email': current_email,
        'otp': new_otp,
        'otp_generated_time': timezone.now().isoformat()
    }
    request.session.modified = True

    messages.success(request, 'A new OTP has been sent to your email address.')
    return redirect('user_side:forget-password-otp')

#############################  forget password new passwrord set  view ########################

@never_cache
def forget_password_set(request):
    """
    View for setting a new password after successful OTP verification.
    """
    error_message_password_forget = []

    if request.method == 'POST':
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')

        # Password validations (UNCHANGED)
        if pass1 != pass2:
            error_message_password_forget.append('Entered passwords do not match.')

        if len(pass1) < 8:
            error_message_password_forget.append('Password must be at least 8 characters long.')

        if not re.search(r'[A-Z]', pass1):
            error_message_password_forget.append('Password must contain at least one uppercase letter.')

        if not re.search(r'[a-z]', pass1):
            error_message_password_forget.append('Password must contain at least one lowercase letter.')

        if not re.search(r'[0-9]', pass1):
            error_message_password_forget.append('Password must contain at least one digit.')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pass1):
            error_message_password_forget.append('Password must contain at least one special character.')

        if error_message_password_forget:
            return render(
                request,
                'user_side/forget-password-3.html',
                {'error_message_password_forget': error_message_password_forget}
            )

        # SESSION FIX
        data = request.session.get('forget_password')

        if not data or not data.get('current_email'):
            messages.error(
                request,
                'Session expired or no email associated. Please restart the forget password process.'
            )
            return redirect('user_side:forget-password')

        current_email = data.get('current_email')

        # Fetch user
        try:
            user = User.objects.get(email=current_email)
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
            return redirect('user_side:forget-password')

        # Set new password
        user.set_password(pass1)
        user.save()

        # Clear session data securely
        request.session.pop('forget_password', None)

        messages.success(
            request,
            "Your password has been successfully updated. Please log in with your new password."
        )
        return redirect('user_side:sign-in')

    return render(
        request,
        'user_side/forget-password-3.html',
        {'error_message_password_forget': error_message_password_forget}
    )


########################### to show the orderd product detail history page based on the orderitem ##########################

@login_required(login_url='user_side:sign-in')
@never_cache
def order_item_details(request):
    if request.user.is_authenticated:
        order_items = OrderItem.objects.filter(order__user=request.user).order_by('-order__order_date')
        # Fetch all orders for the logged-in user
        orders = Order.objects.filter(user=request.user)

        # Filter to only include orders where the order status is pending
        pending_orders = orders.filter(user=request.user,order_status__in=['Pending Payment','Payment Failed']).order_by('-order_date')

        for order in pending_orders:
            order.can_pay = True

            for item in order.items.all():
                if item.product_variant.stock < item.quantity:
                    order.can_pay = False
                    break

        context={
            'order_items':order_items,
            'orders': pending_orders,
        }
        return render(request,'user_side/order-item-history-user.html',context)
    else:
        # Handle the case where the user is not logged in (optional)
        messages.error(request, "You need to log in to view your order items.")
        return redirect('login')

############################  return product dynamically  ########################

def request_return(request, order_item_id):
    if request.method == 'POST':
        try:
            # Find the order item by ID
            order_item = get_object_or_404(OrderItem, id=order_item_id)
            
            # Only allow return request if the current status is 'Delivered'
            if order_item.order_item_status == 'Delivered':
                order_item.order_item_status = 'Return Requested'
                order_item.save()

                # Return success response
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid order status.'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

##########################  invoice pdf generator  #####################

def generate_invoice_pdf(order_item):
    # Set the file path with the current date and time as the filename
    temp_dir = tempfile.gettempdir()  # Get the temp directory
    filename = f"invoice_{order_item.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(temp_dir, filename)

    # Create the PDF
    pdf = canvas.Canvas(file_path, pagesize=letter)
    pdf.setTitle(f"Invoice - {order_item.id}")

    # Find the static file path for the logo
    logo_path = os.path.join(settings.STATIC_ROOT, "assets/images/cycular/cycular_black.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, "static", "assets/images/cycular/cycular_black.png")

    # Adjusted y position for the logo and heading
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 720, "Invoice")  # Heading

    # Add logo centered below the invoice heading
    if os.path.exists(logo_path):
        logo_width = 80  # Adjust the logo size as needed
        pdf.drawImage(logo_path, (letter[0] - logo_width) / 2, 690, width=logo_width, height=80, mask='auto')  # Centering logo
    else:
        pdf.drawString((letter[0] - 100) / 2, 690, "[Logo Not Found]")  # Centering for logo not found

    # Fetch data from related models
    order = order_item.order  # Get the order from order_item
    product_variant = order_item.product_variant
    product = product_variant.product
    order_address = order.order_address  # Fetching the associated order address

    # Customer information
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 660, f"Order ID: {order_item.id}")
    pdf.drawString(50, 640, f"Order Date: {order.order_date.strftime('%Y-%m-%d')}")

    # Order status
    status = order_item.order_item_status
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(colors.red)   # RED color
    pdf.drawString(50, 620, f"Product Status: {status}")

    # Reset color back to normal
    pdf.setFillColor(colors.black)

    # Draw the shipping address
    shipping_address = (
        f"Order Address: {order_address.address_line}, "
        f"{order_address.city}, {order_address.state}, "
        f"{order_address.country}, {order_address.postal_code}"
    )
    address_lines = shipping_address.split(", ")
    y_position = 605  # Adjusted starting y position for address

    for line in address_lines:
        pdf.drawString(50, y_position, line)
        y_position -= 15  # Move down for the next line

    pdf.drawString(50, y_position, f"Phone Number: {order_address.phone_number}")

    # Create table for product information
    data = [
        ['Product Name', 'Variant Size', 'Variant Color', 'Quantity', 'Unit Price (Rs)'],
        [product.name, product_variant.size, product_variant.color, order_item.quantity, f"{order_item.product_variant.price:.2f}"]
    ]

    # Create a table
    table = Table(data, colWidths=[3 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1cc0a0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw the table on the canvas
    table.wrapOn(pdf, 50, 480)  # Adjust the position of the table as necessary
    table.drawOn(pdf, 50, 460)

    # Right side for pricing and discount details
    y_position = 420  # Adjusted starting position for pricing details
    left_label_x = 300  # X-coordinate for bold labels
    normal_value_x = 460  # X-coordinate for normal values

    # Original Price: bold label, normal value
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_label_x, y_position, "Original Price: ")  # Bold label
    pdf.setFont("Helvetica", 12)
    pdf.drawString(normal_value_x, y_position, f"{order_item.product_variant.price:.2f} Rs")  # Normal value
    y_position -= 20  # Move down for the next line

    # Offer Discount: bold label, normal value
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_label_x, y_position, "Offer Discount: ")  # Bold label
    pdf.setFont("Helvetica", 12)
    pdf.drawString(normal_value_x, y_position, f"-{order_item.product_variant.get_savings_amount():.2f} Rs")  # Normal value
    y_position -= 20  # Move down for the next line

    # Coupon Discount: bold label, normal value
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_label_x, y_position, "Coupon Discount: ")  # Bold label
    pdf.setFont("Helvetica", 12)
    pdf.drawString(normal_value_x, y_position, f"-{order_item.coupon_discount_price:.2f} Rs")  # Normal value
    y_position -= 20  # Move down for the next line

    # Total Amount Paid: bold label, normal value
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_label_x, y_position, "Total Amount Paid: ")  # Bold label
    pdf.setFont("Helvetica", 12)
    pdf.drawString(normal_value_x, y_position, f"{order_item.effective_price():.2f} Rs")  # Normal value

    # Footer section with thank you and contact details
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 200, "Thank you for your purchase from Cycular.")
    pdf.drawString(50, 180, "For any issues, contact us at:")
    pdf.drawString(50, 160, "Phone: 123-456-7890")
    pdf.drawString(50, 140, "Address: 123 Cycle St, City Name, State, Zip Code")
    pdf.drawString(50, 120, f"© {datetime.now().year} Cycular. All rights reserved.")

    pdf.showPage()
    pdf.save()

    return file_path

###########################  invoice pdf download button logic   ##############################

@login_required(login_url='user_side:sign-in')
@never_cache
def download_invoice_item(request, order_item_id):
    try:
        # Fetch the specific order item by its ID
        order_item = OrderItem.objects.get(id=order_item_id)
        
        # Generate the invoice PDF for this order item
        file_path = generate_invoice_pdf(order_item)

        # Ensure the file exists before trying to return it
        if os.path.exists(file_path):
            # Return the PDF as a downloadable response
            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"invoice_{order_item.id}.pdf")
            return response
        else:
            raise Http404("Invoice file not found")
        
    except OrderItem.DoesNotExist:
        raise Http404("Order item not found")
    except Exception as e:
        raise Http404(f"Error generating PDF: {str(e)}")
