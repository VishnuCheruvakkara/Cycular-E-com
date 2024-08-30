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
def user_dash_board(request):
    context={
        'user':request.user
    }
    return render(request,'user_side/user-dash-board.html',context)

############################### update or change username ##########################

@login_required(login_url='user_side:sign-in')
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

otp_storage={}

def change_email(request):
    errors={}
    user=request.user


    if request.method=='POST':
        new_email=request.POST.get('new_email')
        if not new_email:
            errors['new_email']='Email cannot be empty.'
        else:
            try:
                validate_email(new_email)
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    errors['new_email']='This email is already taken.'
                else:
                    #To generate otp...
                    otp=get_random_string(length=6,allowed_chars="")
                    otp_storage[user.id]=otp

                    #send otp to the user's current email address.

                    send_mail(
                        'OTP Verification',
                        f'Your OTP for email change is : {otp}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False
                    )
                    messages.success(request,'An OTP has been sent to your current email. Please enter it to confirm your email change.')
                    return JsonResponse({'status': 'otp_sent'})
            except ValidationError:
                errors['new_email']="Enter a valid email address."
    context={
        'current_email':user.email,
        'errors':errors,
    }


    return render(request,'uesr_side/user-dash-board.htmnl',context)

##########################  verify otp for the email change   #################################

@login_required(login_url='user_side:sign-in')
def verify_otp(request):
    errors = {}
    user = request.user
    current_time = timezone.now()

    if request.method == 'POST' and 'otp' in request.POST:
        entered_otp = request.POST.get('otp')
        stored_data = otp_storage.get(user.id)

        if not stored_data:
            errors['otp'] = 'OTP not found or has expired.'
        else:
            stored_otp = stored_data['otp']
            otp_time = stored_data['time']

            # Check if OTP is expired (2 minutes)
            if current_time - otp_time > timedelta(minutes=2):
                errors['otp'] = 'OTP has expired. Please request a new one.'
                otp_storage.pop(user.id, None)  # Remove expired OTP
            elif entered_otp == stored_otp:
                # Update user's email if OTP matches
                new_email = request.session.get('new_email')
                user.email = new_email
                user.save()

                # Remove OTP from storage after successful verification
                otp_storage.pop(user.id, None)
                request.session.pop('new_email', None)  # Remove new email from session

                # Success message with SweetAlert
                return JsonResponse({'status': 'success', 'message': 'Your email has been updated successfully!'})
            else:
                errors['otp'] = 'Invalid OTP. Please try again.'

    context = {
        'errors': errors,
    }
    return render(request, 'user_side/otp_verification_modal.html', context)