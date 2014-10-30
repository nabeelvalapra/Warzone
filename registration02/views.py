from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.context import RequestContext
from registration02.forms import UserForm, UserProfileForm

# Create your views here.
def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)    # set_password hashes the password into hash
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'address' in request.POST:
                profile.address = request.POST.get('address')

            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'registration02/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)


def registration_success(request):
    return render_to_response('registration02/registration_success.html')


def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('registration02/login.html',c)

    
def auth_login(request):
    def getUser(email):                         # finds the username and returns it.
        try:
            return User.objects.get(email=email.lower())
        except User.DoesNotExist:
                return None
            
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        
        if '@' in username:
            username = getUser(username)         # Passed to retrive the username from email.
            
        user = auth.authenticate(username=username,password=password)
        
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/registration02/loggedin/')
        else:
            return HttpResponseRedirect('/registration02/')
        
    
def loggedin(request):
    return render_to_response('registration02/loggedin.html')


