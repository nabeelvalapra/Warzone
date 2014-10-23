from django import forms
from fmzone.models import Persons
from django.core.exceptions import ValidationError


class PersonDetailForm(forms.ModelForm):
    class Meta:
        model = Persons
        
    def clean(self):
        cleaned_data = super(PersonDetailForm, self).clean()
        email = cleaned_data.get("email")
        
        if 'n' in email:
            raise ValidationError("You Got It!!!")

class PersonForm(forms.ModelForm):
    class Meta:
        model = Persons
        exclude = ['address']
        
    def clean(self):
        cleaned_data = super(PersonForm, self).clean()
        email = cleaned_data.get("email")
        
        if 'n' in email:
            raise ValidationError("You Got It!!!")
        

class PersonFormSet(PersonForm):
    def clean(self):
        cleaned_data = super(PersonForm, self).clean()
        email = cleaned_data.get("email")
        
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        #if email in Persons.objects.all():
        #    raise ValidationError("This email address already exixts in the Person database")
        
        
        