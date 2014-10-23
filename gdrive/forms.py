from django import forms
from gdrive.models import DriveFiles

class FileForm(forms.ModelForm):
    class Meta:
        model = DriveFiles
        fields = ['file_name']
    