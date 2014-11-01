from django import forms
from gdrive.models import DriveFiles
from django.forms.widgets import HiddenInput


class FileForm(forms.ModelForm):
    file_name = forms.FileField()
    
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['file_name'].widget.attrs.update({'multiple': 'multiple'})
    
    class Meta:
        model = DriveFiles
        fields = ['file_name']
        
        
# class FileListForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         filelist = kwargs.pop('filelist')
#         super(FileListForm, self).__init__(*args, **kwargs)
#         counter = 1
#         for _file in filelist:
#             self.fields[_file['title']+str(counter)] = forms.CharField(label=_file['title'],
#                                                                         widget= forms.TextInput(attrs={'type':'hidden'}))
#             counter +=1
            
class FileListForm(forms.Form):
    fname = forms.CharField()           