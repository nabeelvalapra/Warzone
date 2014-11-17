from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.messages import constants as messagesconst
from django.contrib import messages
from django.contrib.messages import get_messages
import json


# Create your views here.
def index(request):
    totmessages = ''
    if request.method == 'POST':
        #Save
        for i in range(5):
            messages.add_message(request, messages.INFO, 'My notification'+str(i+1))
            
        totmessages = get_messages(request)
        return HttpResponse(str(totmessages))   
    return render(request,'makenotification/index.html',{'messages':totmessages})

def gonotify(request):
    data = {}
    data['message'] = "stru"
        
    return HttpResponse(json.dumps(data),mimetype='application/javascript')