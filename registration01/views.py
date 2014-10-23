from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)   # UserCreationForm is a Builtin form.
        if form.is_valid():
            #All the email validation can be done here.
            form.save()
            return HttpResponseRedirect('/registration01/registration_success/')
        
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()

    return render_to_response('registration01/register.html',args)


def registration_success(request):
    return render_to_response('registration01/registration_success.html')


def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('registration01/login.html',c)

    
def auth_login(request):
    # Here you can login through Username and EmailID...
    
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
            return HttpResponseRedirect('/registration01/loggedin/')
        else:
            return HttpResponseRedirect('/registration01/')

    
def loggedin(request):
    return render_to_response('registration01/loggedin.html')


