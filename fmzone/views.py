from django.shortcuts import render, render_to_response
from fmzone.forms import PersonForm, PersonDetailForm, PersonFormSet
from django.http.response import HttpResponse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from fmzone.models import Persons

# Create your views here.
def details(request):
    form = PersonDetailForm()
    if request.method == "POST":
        form = PersonDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Cool You form is valid....') 
    return render(request,'fmzone/details.html',{'form':form})


def outforms(request):
    modelformset = modelformset_factory(Persons,PersonFormSet)
    formset = modelformset(queryset=Persons.objects.all())
    #formset = formset_factory(PersonForm)
    if request.method == "POST":
        formset = formset_factory(PersonFormSet)
        form = formset(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Cool You form is valid....') 
    return render(request,'fmzone/outdata.html',{'formset':formset})