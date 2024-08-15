from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegisterForm,OTPVerificationForm
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


User = get_user_model()
# Create your views here.


############################  home page ###################################

def home_page(request):
    return render(request,'core/index.html')

###########################  user sign-up  #####################################

@never_cache
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')  # Use password1 to avoid confusion
            
            otp = generate_otp()
            send_otp_email(email, otp, username)

            # Pass the user data and OTP to the next form via hidden fields
            otp_form = OTPVerificationForm(initial={
                'email': email,
                'username': username,
                'password': password,
                'otp': otp,
                'otp_created_at': timezone.now().isoformat(),
            })

            # Store OTP and timestamp in hidden fields
            context = {
                'form': otp_form,
                'otp': otp,
                'otp_created_at': timezone.now(),
            }

            messages.success(request, 'OTP has been sent to your email.')
            return render(request, 'user_side/otp.html', context)
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
    }
    return render(request, "user_side/sign-up.html", context)


###########################  login section #############################################


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Hello, you are already logged in.")
        return redirect("core:index")
    
    if request.method == "POST":
        email = request.POST.get("signin-email")
        password = request.POST.get("signin-password")
        
        # Authenticate using email as the username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_verified:
                login(request, user)
                messages.success(request, "You are logged in.")
                return redirect("core:index")
            else:
                messages.warning(request, "Your account is not verified. Please check your email for verification instructions or [Resend OTP](url_to_resend_otp).")
        else:
            messages.warning(request, "Invalid email or password. Please try again.")
    
    # Always return a response, even for GET requests
    return render(request, 'user_side/sign-in.html')


###########################  logout section  #########################################

def logout_view(request):
    logout(request)
    messages.success(request,"You logged out")  
    return redirect("user_side:sign-in")

###########################  otp page section  #########################################
@never_cache
def otp_view(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        
        if form.is_valid():
            entered_otp = form.cleaned_data.get('otp')
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            stored_otp = request.POST.get('otp')  # This should be fetched from session or hidden field
            otp_created_at = request.POST.get('otp_created_at')

            # Validate OTP and timestamp
            if entered_otp == stored_otp:
                # Ensure the OTP hasn't expired
                otp_creation_time = datetime.fromisoformat(otp_created_at)
                current_time = timezone.now()

                if current_time - otp_creation_time <= timedelta(seconds=OTP_EXPIRY_SECONDS):
                    # OTP is valid and within expiry time
                    user = User.objects.create_user(email=email, username=username, password=password)
                    user.is_verified = True
                    user.save()

                    backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user, backend=backend)

                    messages.success(request, 'OTP verification successful. You are now logged in.')
                    return redirect('core:index')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'Form validation failed. Please check your inputs.')

    else:
        form = OTPVerificationForm()

    context = {
        'form': form,
    }
    return render(request, 'user_side/otp.html', context)

###########################   generating otp   ########################################

OTP_EXPIRY_SECONDS=300

def generate_otp():
    return str(random.randint(100000,999999))

###########################   send otp to user email   ########################################

def send_otp_email(email,otp,username):
    subject = "Your OTP for Sign-Up"
    message=f"Dear {username},\n\nThank you for registering with Cycular! Your One-Time Password (OTP) to complete the sign-up process is {otp}. Please keep this code confidential and do not share it with anyone.\n\nIf you did not request this code, please disregard this message.\n\nBest regards,\nThe Cycular Team"
    email_form=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_form,recipient_list)

###########################   resend E-mail   ########################################

@require_POST
def resend_otp(request):
    session_key = request.session.get('user_registration_data')
    if not session_key or session_key not in request.session:
        return JsonResponse({'status': 'error', 'message': 'No data found. Please sign-up again.'})
    
    session_data = request.session.get(session_key)
    if not session_data:
        return JsonResponse({'status': 'error', 'message': 'No data found. Please sign-up again.'})
    
    email = session_data.get('email')
    username=session_data.get('username')
    new_otp = generate_otp()
    send_otp_email(email, new_otp,username)
    
    session_data['otp'] = new_otp
    session_data['otp_created_at'] = timezone.now().isoformat()
    request.session[session_key] = session_data
    request.session.modified = True
    
    return JsonResponse({'status': 'success', 'message': 'New OTP sent successfully.'})

###############################  to handle the user status through admin page  ##########################

@login_required
def toggle_user_status(request,user_id):
    if request.method == 'GET':
        user=get_object_or_404(User,id=user_id)
        user.is_active=not user.is_active #toogle logic
        user.save()
        status='active' if user.is_active else 'blocked'
        return JsonResponse({'status':status})
    return JsonResponse({'error':'Invalid request'},status=400)


###################################
