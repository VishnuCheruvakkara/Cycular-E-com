from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegisterForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.hashers import make_password
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
import uuid

def generate_unique_session_key():
    return str(uuid.uuid4())

@never_cache
def register_view(request):

    breadcrumbs_pages=[
        {'name':'Home','url':'core/index.html'},
        {'name':'Sign-up','url':'','active':True}
    ]

    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid(): #check the all validation condition for the submitted data
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            
            # #checker
            # print(email,password,username)

            session_key=generate_unique_session_key()

            otp = generate_otp()
            otp_created_at = timezone.now()
           
            request.session[session_key]={
                'otp':otp,
                'otp_created_at':otp_created_at.isoformat(),
                'email':email,
                'username':username,
                'password':password,
            }

            # # checker
            # print("Session data after storing:", request.session[session_key])


            send_otp_email(email,otp,username)
            request.session['user_registration_data']=session_key
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('user_side:otp')
        
    else : 
        form=UserRegisterForm()

    context={
        'form':form,
        'breadcrumb_pages': breadcrumbs_pages,
    }
   
    return render(request,"user_side/sign-up.html",context)

###########################  login section #############################################
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Hello, you are already logged in.")
        return redirect("core:index")
    
    if request.method == "POST":
        email = request.POST.get("signin-email")
        password = request.POST.get("signin-password")

        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("core:index")
        else:
            messages.warning(request, "Invalid email or password. Please try again.")
    
    return render(request, 'user_side/sign-in.html')


###########################  logout section  #########################################

def logout_view(request):
    logout(request)
    messages.success(request,"You logged out")
    return redirect("user_side:sign-in")

###########################  otp page section  #########################################

def otp_view(request):

    #cheker

    # session_key=request.session.get('user_registration_data')
    # session_data=request.session.get(session_key)

    # # Debugging print statements
    # print("Session data before retrieving password:", session_data)
    
    # # Attempt to retrieve the password from the session data
    # password = session_data.get('password')
    # print("Retrieved password:", password)


    # email=session_data.get('email')
    # username=session_data.get('username')
    # password=session_data.get('password')

    # print(email,username,password)

    session_key=request.session.get('user_registration_data')

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

            # #checker
                    
            # # Debugging print statements
            # print("Session data before retrieving password:", session_data)
            
            # # Attempt to retrieve the password from the session data
            # password = session_data.get('password')
            # print("Retrieved password:", password)

            # print("Password before creating user:", password)

            user=User.objects.create_user(username=username,email=email,password=password)
                        
            # # Print the stored password (note: this will be a hashed value, not the raw password)
            # print("Stored password (hashed):", user.password)
                     
            # # Debugging print statements
            # print("Session data before retrieving password:", session_data)
            
            # # Attempt to retrieve the password from the session data
            # password = session_data.get('password')
            # print("Retrieved password:", password)


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
            messages.error(request,'Invalid OTP : Entered otp is not match, check-otu resend OTP.')

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
        return redirect('user_side:sign-up')  # Redirect to signup if no session data
    
    session_data = request.session.get(session_key)
    if not session_data:
        return redirect('user_side:sign-up')  # Redirect to signup if session data is empty
    
    email = session_data.get('email')
    username = session_data.get('username')
    new_otp = generate_otp()
    send_otp_email(email, new_otp, username)
    
    session_data['otp'] = new_otp
    session_data['otp_created_at'] = timezone.now().isoformat()
    request.session[session_key] = session_data
    request.session.modified = True
    
    # Redirect back to the OTP input page with a success message
    return redirect('user_side:otp')

###############################  to handle the user status through admin page  ##########################


###################################
