from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegisterForm
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.conf import settings
import random
from django.core.mail import send_mail
from datetime import datetime
# Create your views here.

User=settings.AUTH_USER_MODEL


############################  home page ###################################

def home_page(request):
    return render(request,'core/index.html')

###########################  user sign-up  #####################################

def register_view(request):
    if request.method=='POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid(): #check the all validation condition for the submitted data
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')

            existing_user=User.objects.filter(email=email).first()

            if existing_user:
                if existing_user.is_active:
                    form.add_error('email','This email is already registered and verified. Please log in.')
                else:
                    otp=generate_otp()
                    existing_user.otp=otp
                    existing_user.otp_created_at=datetime.now()
                    new_user.save()
                    send_otp_email(existing_user.email,otp)
                    request.session['user_id']=existing_user.id
                    return redirect('user_side:otp')
                
            else:
                new_user=form.save(commit=False)
                new_user.is_active=False
                otp=generate_otp()
                new_user.otp=otp
                new_user.otp_created_at=datetime.now()
                new_user.save()
                send_otp_email(new_user.email,otp)
                request.session['user_id']=new_user.id
                return redirect('user_side:otp')
            
    else : 
        form=UserRegisterForm()

    context={
        'form':form
    }
    return render(request,"user_side/sign-up.html",context)

###########################  login section #############################################

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

def otp_view(request,user_id):
    user=get_object_or_404(User,id=user_id)

    if request.method=='POST':
        otp1=request.POST.get('otp1','0')
        otp2=request.POST.get('otp2','0')
        otp3=request.POST.get('otp3','0')
        otp4=request.POST.get('otp4','0')
        otp5=request.POST.get('otp5','0')
        otp6=request.POST.get('otp6','0')

        entered_otp=f"{otp1}{otp2}{otp3}{otp4}{otp5}{otp6}"
        
        #check wheather the eneterd otp is iteger or not.
        try:
            entered_otp=int(entered_otp)
        except ValueError:
            messages.error(request,"Invalid OTP format. Please enter a numeric OTP.")
            return render(request,"user_side/otp.html",{'user_id':user_id})

        #validate the enterd otp based on the otp that generated in the backend ,
        #it is equal or not downbelow.
        if str(user.otp) != str(entered_otp):
            messages.error(request,'Invalid OTP. Please check and try again.')
            return render(request,"user_side/otp.html",{'user_id':user_id})

        #check the time is expired or not 
        if ((datetime.now()-user.otp_created_at).total_seconds() > OTP_EXPIRY_SECONDS):
            messages.error(request,"OTP expired. Please enter resend OTP.")
            return render(request,"user_side/otp.html",{"user_id" : user_id})
        #if both the above condition is true then.
        user.is_verified=True
        user.is_avtive=True
        user.save()
        messages.success(request,"OTP verified successfully. Your account is now activated.")
        return redirect('core:index')
    
    return render(request,'user_side/otp.html',{'user_id':user_id})

###########################   generating otp   ########################################

OTP_EXPIRY_SECONDS=60

def generate_otp():
    return str(random.randint(100000,999999))

###########################   send otp to user email   ########################################

def send_otp_email(email,otp):
    subject = "Your OTP for Sign-Up"
    message=f"Your OTP for signing up is {otp}. Please do not share this with anyone."
    email_form=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_form,recipient_list)