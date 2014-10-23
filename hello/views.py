from django.shortcuts import render, render_to_response

# Create your views here.
def startpage(request):
    return render_to_response('hello/startpage.html')