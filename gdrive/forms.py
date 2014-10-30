from django import forms
from gdrive.models import DriveFiles

class FileForm(forms.ModelForm):
    file_name = forms.FileField()
    
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['file_name'].widget.attrs.update({'multiple': 'multiple'})
    
    class Meta:
        model = DriveFiles
        fields = ['file_name']
        
  

class ChoicesForm(forms.Form):
    CHOICES = (('1','Upload'),('2','List'),('3','Delete the folder'))
    choice = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES)