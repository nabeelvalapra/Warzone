from django.shortcuts import render,redirect, render_to_response
import apiclient
from gdrive.forms import FileForm, FileListForm
from django.contrib.auth.decorators import login_required
import os
from Warzone.settings import BASE_DIR 
from django.contrib.auth import logout
from GoogleDriveFunctions import *
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
    

@login_required(login_url='/registration02/')
@auth_check
def index2(request, *args, **kwargs):
    form = FileForm()
    return render(request,'gdrive/secondwar/uploadfile.html',{'form':form})


@login_required(login_url='/registration02/')
@auth_check
def upload2(request, *args, **kwargs):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            savedfile = form.save()
            
            File = request.FILES.get('file_name')
            FileName = File.name
            FilePath = str(savedfile.file_name.path)
            
            credentials = kwargs['credentials']
            service = kwargs['service']
            mainfolderID = kwargs['mainfolderID']
            
            return Upload_File_Handler(request, credentials, service, mainfolderID, FileName, FilePath)  
        else:
            return HttpResponse('Form is not valid.')                      
    else:
        form = FileForm() 
                    
    return render(request,'gdrive/secondwar/uploadfile.html',{'form':form,'user':request.user.id})


@login_required(login_url='/registration02/')
@auth_check
def listGfiles(request, *args, **kwargs):
    q = "'%s' in parents" % kwargs['mainfolderID']
    file_list = retrieve_all_files(kwargs['service'], query=q)
    formsetInitial = []
    d = {}
    for file in file_list:
        d = {'fname': file['title'],'fileid':file['id']}
        formsetInitial.append(d) 
        
    filelist_formset = formset_factory(FileListForm, can_delete=True)   
    formset = filelist_formset(initial=formsetInitial)
    if request.method == 'POST':
        formset = filelist_formset(request.POST)
        to_delete = [form.cleaned_data['fileid'] for form in formset.deleted_forms]
        
        for fileID in to_delete:
            delete_file(kwargs['service'], fileID)
        
    return render(request,'gdrive/secondwar/listGfiles.html',{'formset':formset,'user':request.user.id})

   
def logoutfromhere(request):
    logout(request)
    return HttpResponse('You sucessfully logged out.')
    
 
