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
from gdrive.models import DriveFiles
    

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
            Files = request.FILES.getlist('file_name')
            
            service = kwargs['service']
            mainfolderID = kwargs['mainfolderID']

            try:
                for file in Files:
                    tempFile = DriveFiles.objects.create(file_name=file)
                    FileName = file.name
                    FilePath = str(tempFile.file_name.path)
                    _file = insert_file(service, FileName, FilePath, parent_id=mainfolderID) 
                    if _file:
                        f = FileInfo(fileinfo=_file['id']).save()
                        #f.id can be returned if necessary.
                        os.remove(FilePath)
                return HttpResponse('Cool, your file seem uploaded.')
            except Exception, e:
                raise Exception("Oops, there was an error in your filehandler function<br>" + str(e))
            
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
    
 
