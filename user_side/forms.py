from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_side.models import User


class UserRegisterForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control"}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}),label="Password")
    password2=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}),label="Confirm Password")
    class Meta:
        model=User
        fields=['username','email']

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter OTP"}))
    email = forms.EmailField(widget=forms.HiddenInput())
    username = forms.CharField(widget=forms.HiddenInput())
    password = forms.CharField(widget=forms.HiddenInput())

