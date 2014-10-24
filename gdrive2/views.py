from django.shortcuts import render, render_to_response

# Create your views here.

def letitgo(request):
    return render_to_response('/gdrive2/index.html')
