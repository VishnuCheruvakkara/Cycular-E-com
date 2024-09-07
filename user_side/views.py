from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegisterForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login,authenticate,logout

from django.contrib import messages
from django.conf import settings
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta,datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from .models import Address
from django.views.decorators.cache import never_cache


User = get_user_model()
# Create your views here.


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
            
            # #checker
            print(email,password,username)

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

            # # checker
            print("Session data after storing:", request.session[session_key])


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

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "Hello, you are already logged in.",extra_tags='user')
        return redirect("core:index")
    
    if request.method == "POST":
        email = request.POST.get("signin-email")
        password = request.POST.get("signin-password")

        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "You are logged in.",extra_tags='user')
                return redirect('core:index')
            else:
                messages.error(request,'Your account has been blocked please check the contact support section...',extra_tags='user')
                return redirect('core:idex')
        else:
            messages.warning(request, "Invalid email or password. Please try again.",extra_tags='user')
    
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

    # # Debugging print statements
    # print("Session data before retrieving password:", session_data)
    
    # # Attempt to retrieve the password from the session data
    # password = session_data.get('password')
    # print("Retrieved password:", password)


    # email=session_data.get('email')
    # username=session_data.get('username')
    # password=session_data.get('password')

    # print(email,username,password)

    # session_key=request.session.get('user_registration_data')

    #################################################

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

#############################################
            #checker
                    
            # Debugging print statements
            print("Session data before retrieving password:", session_data)
            
            # Attempt to retrieve the password from the session data
            password = session_data.get('password')
            print("Retrieved password:", password)

            print("Password before creating user:", password)
            ##############################################################

            user=User.objects.create_user(username=username,email=email,password=password)

            ##############################################################
            
            #checker``
            # Print the stored password (note: this will be a hashed value, not the raw password)
            print("Stored password (hashed):", user.password)
                     
            # Debugging print statements
            print("Session data before retrieving password:", session_data)
            
            # Attempt to retrieve the password from the session data
            password = session_data.get('password')
            print("Retrieved password:", password)

########################################################

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

OTP_EXPIRY_SECONDS=60

def generate_otp():
    return str(random.randint(100000,999999))

###########################   send otp to user email   ########################################

def send_otp_email(email,otp,username):
    subject = "Your OTP for Sign-Up"
    message=f"Dear {username},\n\nThank you for registering with Cycular! Your One-Time Password (OTP) to complete the sign-up process is {otp}. Please keep this code confidential and do not share it with anyone.\n\nIf you did not request this code, please disregard this message.\n\nBest regards,\nThe Cycular Team"
    email_form=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_form,recipient_list)

###########################   resend otp   ########################################

def resend_otp(request):
    session_key = request.session.get('user_registration_data')
    if not session_key or session_key not in request.session:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect('user_side:sign-up')  # Redirect to signup if no session data
    
    session_data = request.session.get(session_key)
    if not session_data:
        messages.error(request, "Session data not found. Please sign up again.")
        return redirect('user_side:sign-up')  # Redirect to signup if session data is empty
    
    email = session_data.get('email')
    username = session_data.get('username')
    new_otp = generate_otp()
    send_otp_email(email, new_otp, username)
    
    session_data['otp'] = new_otp
    session_data['otp_created_at'] = timezone.now().isoformat()
    request.session[session_key] = session_data
    request.session.modified = True

    messages.success(request, f"OTP successfully resent to {email}. Please check your inbox.")
    # Redirect back to the OTP input page with a success message
    return redirect('user_side:otp')

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

    context={
        'user':request.user,
        'addresses':addresses,
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

context_data={}

@login_required(login_url='user_side:sign-in')
@never_cache
def email_change_view(request):
    """
    View to send OTP to the new email address entered by the user.
    """
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        context_data['new_email']=new_email

        try:
            validate_email(new_email)
        except ValidationError:
           messages.error(request,'Invalid email address. Please enter a valid email.')
           return redirect('user_side:user-dash-board')
       
        # Check if the email already exists
        if User.objects.filter(email=new_email).exists():
            messages.error(request, 'This email address is already in use. Please choose a different email.')
            context_data['email_error'] = 'This email address is already in use. Please choose a different email.'
            return render(request, 'user_side/user-dash-board.html', context_data)

        otp = random.randint(100000, 999999)  # Generate a random OTP

        # Send OTP to the new email address
        send_mail(
            'Your OTP Code',
            f'Dear User,\n\nTo complete your email change request, please use the following OTP code: {otp}. This code is valid for 2 minutes.\n\nThank you!\n\n Greetings from Cycular...',
            settings.EMAIL_HOST_USER,  # Replace with your actual sender email
            [new_email],
            fail_silently=False,
        )

        context_data['otp']=otp
        context_data['otp_generated_time']=timezone.now()

        messages.success(request,'An OTP has been sent to your new email address.')
        return redirect('user_side:email-change-otp-view')

    return render(request,'user_side/user-dash-board.html',context_data)

##########################  verify otp for the email change   #################################

@login_required(login_url='user_side:sign-in')
@never_cache
def email_change_otp_view(request):
    error_message = "" 
    if request.method=='POST':
        entered_otp=request.POST.get('otp')
        current_time=timezone.now()
        otp_generated_time=context_data.get('otp_generated_time')
        otp_pattern = re.compile(r'^\d{6}$')

        if not otp_pattern.match(entered_otp):
            error_message = "Please enter a valid 6-digit OTP."

        if  entered_otp == str(context_data.get('otp')) and otp_generated_time:
            #check for otp is expired or not (timer is set to be 2 seconds.)
            if (current_time-otp_generated_time).total_seconds() <= 120 :
                user=request.user
                user.email=context_data.get('new_email')
                user.save()
                #clear the data due to the user is successfully logged in 
                context_data.clear()

                messages.success(request,"Your Email has been successfully updated.")
                return redirect('user_side:user-dash-board')
            else:
                messages.error(request,"The OTP has been expired.Please check the resend otp for a new otp.")
        else:
            messages.error(request,"The OTP you entered is incorrect.")

    return render(request,'user_side/email-change-otp.html',{'error_message': error_message})

########################### resend otp for the change email for the user #######################

@login_required(login_url='user_side:sign-in')
@never_cache
def email_change_resend_otp_view(request):
  
        new_email=context_data.get('new_email')
        if not new_email:
            messages.error(request,'Email address is not available.')
            return redirect('user_side:user-dash-board')
        
        otp = random.randint(100000, 999999)

        send_mail(
            'Your OTP code',
            f'Dear User,\n\nTo complete your email change request, please use the following OTP code: {otp}. This code is valid for only 2 minutes.\n\nThank you!\n\nGreetings from Cycular...',
            settings.EMAIL_HOST_USER,  # Replace with your actual sender email
            [new_email],
            fail_silently=False,
        )
        context_data['otp'] = otp
        context_data['otp-generated-time'] = timezone.now()

        messages.success(request, 'New OTP has been sent to your email address.')
        return redirect('user_side:email-change-otp-view')  # Redirect to the OTP verification page
    
 

##########################  update the password of the logined user  ##################################

password_context={}


@login_required(login_url='user_side:sign-in')
@never_cache
def password_change_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('user_side:user-dash-board')
        
        if current_password == new_password:
            messages.error(request,'New password cannot be same as the old password. try again...')
            return redirect('user_side:user-dash-board')

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('user_side:user-dash-board')
        
    

        # Generate and send OTP to user's email
        otp = random.randint(100000, 999999)
        password_context['otp'] = otp
        password_context['otp_generated_time'] = timezone.now()
        password_context['new_password'] = new_password
        
        send_mail(
            'Your OTP Code',
            f'Dear User,\n\nTo complete your password change request, please use the following OTP code: {otp}. This code is valid for 2 minutes.\n\nThank you!\n\nGreetings from Cycular...',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        messages.info(request, 'An OTP has been sent to your email address.')
        return redirect('user_side:password-change-otp-view')

    return render(request, 'user_side/user-dash-board.html')

########################## varify otp for the password change  ############################



@login_required(login_url='user_side:sign-in')
@never_cache
def password_change_otp_view(request):
    error_message_password = "" 
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_password')
        current_time = timezone.now()
        otp_generated_time = password_context.get('otp_generated_time')
        new_password = password_context.get('new_password')
        
        otp_pattern = re.compile(r'^\d{6}$')

        if not otp_pattern.match(entered_otp):
            error_message_password = "Please enter a valid 6-digit OTP."
        elif entered_otp == str(password_context.get('otp')) and otp_generated_time:
            if (current_time - otp_generated_time).total_seconds() <= 120:
                user = request.user
                user.set_password(new_password)
                user.save()
                password_context.clear()
                messages.success(request, "Your password has been successfully updated,Please login with new password.")
                return redirect('user_side:user-dash-board')
            else:
                messages.error(request, "The OTP has expired. Please request a new OTP.")
        else:
            messages.error(request, "The OTP you entered is incorrect.")

    return render(request, 'user_side/password-change-otp.html', {'error_message_password': error_message_password})

###########################  paswword resend otp view   ##################################

@login_required(login_url='user_side:sign-in')
@never_cache
def password_change_resend_otp_view(request):
    user = request.user
    if not user.email:
        messages.error(request, 'Email address is not available.')
        return redirect('user_side:user-dash-board')
    
    # Generate a new OTP
    otp = random.randint(100000, 999999)

    # Send the OTP to the user's email
    send_mail(
        'Your OTP Code',
        f'Dear User,\n\nTo complete your password change request, please use the following OTP code: {otp}. This code is valid for only 2 minutes.\n\nThank you!\n\nGreetings from Cycular...',
        settings.EMAIL_HOST_USER,  # Replace with your actual sender email
        [user.email],  # Send OTP to the user's email
        fail_silently=False,
    )

    # Update the context with the new OTP and its generation time
    password_context['otp'] = otp
    password_context['otp_generated_time'] = timezone.now()

    # Notify the user that a new OTP has been sent
    messages.success(request, 'A new OTP has been sent to your email address.')
    return redirect('user_side:password-change-otp-view')  # Redirect to the OTP verification page



#Adress management section down below...

#########################  add address view  ####################

def add_address(request):

    errors = {}  # Dictionary to hold error messages

    # Fetch all addresses of the logged-in user
    addresses = Address.objects.filter(user=request.user)


    if request.method == 'POST':
        address_line = request.POST.get('address_line', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        is_default = request.POST.get('is_default') == 'on'

        # Validation for Address Line
        if not address_line:
            errors['address_line'] = 'Address line is required.'
        elif len(address_line) < 5 or len(address_line) > 100:
            errors['address_line'] = 'Address line must be between 5 and 100 characters.'
        elif re.search(r'[^a-zA-Z0-9\s,.-]', address_line):
            errors['address_line'] = 'Address line contains invalid characters.'

        # Validation for City
        if not city:
            errors['city'] = 'City is required.'
        elif len(city) > 50:
            errors['city'] = 'City name is too long (max 50 characters).'
        elif not re.match(r'^[a-zA-Z\s\-]+$', city):
            errors['city'] = 'City must only contain letters, spaces, or hyphens.'
        elif any(char.isdigit() for char in city):
            errors['city'] = 'City name cannot contain numbers.'

        # Validation for State
        if not state:
            errors['state'] = 'State is required.'
        elif len(state) > 50:
            errors['state'] = 'State name is too long (max 50 characters).'
        elif not re.match(r'^[a-zA-Z\s\-]+$', state):
            errors['state'] = 'State must only contain letters, spaces, or hyphens.'
        elif any(char.isdigit() for char in state):
            errors['state'] = 'State name cannot contain numbers.'

        # Validation for Country
        if not country:
            errors['country'] = 'Country is required.'
        elif len(country) > 50:
            errors['country'] = 'Country name is too long (max 50 characters).'
        elif not re.match(r'^[a-zA-Z\s\-]+$', country):
            errors['country'] = 'Country must only contain letters, spaces, or hyphens.'
        elif any(char.isdigit() for char in country):
            errors['country'] = 'Country name cannot contain numbers.'

        # Validation for Postal Code
        if not postal_code:
            errors['postal_code'] = 'Postal code is required.'
        elif not re.match(r'^\d{4,10}$', postal_code):
            errors['postal_code'] = 'Postal code must be between 4 and 10 digits and contain only numbers.'
        elif len(postal_code) > 10:
            errors['postal_code'] = 'Postal code is too long (max 10 digits).'

        # Validation for Phone Number with Mandatory Country Code
        if not phone_number:
            errors['phone_number'] = 'Phone number is required.'
        elif not re.match(r'^\+\d{1,4}\d{6,10}$', phone_number):
            errors['phone_number'] = (
                'Phone number must start with a "+" followed by 1-4 digits for the country code '
                'and then 6-10 digits for the phone number itself.'
            )
        elif phone_number[0] != '+':
            errors['phone_number'] = 'Phone number must start with a "+" followed by the country code.'

        # If no errors, create the address
        if not errors:
            Address.objects.create(
                user=request.user,
                address_line=address_line,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                phone_number=phone_number,
                is_default=is_default
            )
            messages.success(request, 'Address added successfully.')
            return redirect('user_side:user-dash-board')
        else:
           
            messages.error(request, 'Please correct the errors in Add address form.')

    context = {
        'errors': errors,
        'addresses':addresses,
       
    }

    return render(request, 'user_side/user-dash-board.html', context)
#######################  edit address  ##########################

def edit_address(request, address_id):
    # Fetch the address object based on the given ID and ensure it belongs to the current user
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        # Update address fields from the form
        address.address_line = request.POST.get('address_line')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.postal_code = request.POST.get('postal_code')
        address.phone_number = request.POST.get('phone_number')
        address.is_default = request.POST.get('is_default') == 'on'  # Checkbox handling for default address

        # Save the updated address
        address.save()
        messages.success(request, 'Address updated successfully.')
        
        
        return redirect('user_side:user-dash-board')  


    context = {
        'address': address,  # Pass the address object to pre-fill form fields
    }
    return render(request, 'user_side/user-dash-board.html', context)


#########################  delete user address  ######################3

@login_required(login_url='user_side:sign-in')  # Restrict to logged-in users
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

forget_context={}
def forget_password(request):
   
    if request.method == 'POST':
        current_email = request.POST.get('current_email')
        forget_context['current_email']=current_email


        try:
            validate_email(current_email)
        except ValidationError:
           messages.error(request,'Invalid email address. Please enter a valid email.')
           return redirect('user_side:user-dash-board')

        #chec if the email exist in the data base or not
        if not User.objects.filter(email=current_email).exists():
            messages.error(request,'The email address does not exist,try again...')
            return  redirect('user_side:forget-password')
        
        otp = random.randint(100000, 999999)  # Generate a random OTP

        # Send OTP to the new email address
        send_mail(
            'Your OTP Code',
            f'Dear User,\n\nIt seems like you requested a resend of your OTP code. Your new OTP is: {otp}. Please use this code to complete your request within 2 minutes.\n\nIf you did not request this OTP, please ignore this message.\n\nThank you for choosing Cycular!\n\nBest Regards,\nThe Cycular Team',
            settings.EMAIL_HOST_USER,  # Replace with your actual sender email
            [current_email],
            fail_silently=False,
        )

        forget_context['otp']=otp
        forget_context['otp_generated_time']=timezone.now()

        messages.success(request,'An OTP has been sent to the enterd email address.')
        return redirect('user_side:forget-password-otp')

    return render(request,'user_side/forget-password-1.html')

###################  forget password otp section  ###################

def forget_password_otp(request):
    error_message_forget = "" 
    if request.method=='POST':
        entered_otp=request.POST.get('forget-otp')
        current_time=timezone.now()
        otp_generated_time=forget_context.get('otp_generated_time')
        otp_pattern = re.compile(r'^\d{6}$')

        if not otp_pattern.match(entered_otp):
            error_message_forget = "Please enter a valid 6-digit OTP."

        if  entered_otp == str(forget_context.get('otp')) and otp_generated_time:
            #check for otp is expired or not (timer is set to be 2 seconds.)
            if (current_time-otp_generated_time).total_seconds() <= 120 :
    
                #clear the data due to the user is successfully logged in 
                forget_context.clear()

                messages.success(request,"Otp is verified.")
                return redirect('user_side:forget-password-set')
            else:
                messages.error(request,"The OTP has been expired.Please check the resend otp for a new otp.")
        else:
            messages.error(request,"The OTP you entered is incorrect.")

    return render(request,'user_side/forget-password-2.html',{'error_message_forget':error_message_forget})

##################### for get password new password entering section   ######################


def forget_password_set(request):
    if request.method == 'POST':
        pass1=request.POST.get('password')
        pass2=request.POST.get('confirm_password')

        if pass1 != pass2:
            messages.error(request, 'Eterd passwords do not match.')
            return redirect('user_side:forget-password-set')
        else:
            user = request.user
            user.set_password(pass1)
            user.save()
            messages.success(request, "Your password has been successfully updated,Please login with new password.")
            return redirect('user_side:sign-in')

    return render(request,'user_side/forget-password-3.html')