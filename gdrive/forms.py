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
