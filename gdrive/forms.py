from django import forms
from gdrive.models import DriveFiles

class FileForm(forms.ModelForm):
    class Meta:
        model = DriveFiles
        fields = ['file_name']
    

class ChoicesForm(forms.Form):
    CHOICES = (('1','Upload'),('2','List'),('3','Delete the folder'))
    choice = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES)