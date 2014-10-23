from django import forms
from django.contrib.auth.models import User
from registration02.models import UserProfile


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        feilds = ('username','email','password')
        

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address','phone_num')