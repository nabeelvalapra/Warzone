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
    
 
#==========================================================================================================================================================
#==========================================================================================================================================================
#==========================================================================================================================================================
#==========================================================================================================================================================
#==========================================================================================================================================================
#==========================================================================================================================================================
@login_required
def firstwar(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            savedfile = form.save()
             
            request.session['drivefile_id'] = str(savedfile.id)
            request.session['filename'] = str(request.FILES['file_name'])
            request.session['mimetype'] = str(request.FILES['file_name'].content_type)
            request.session['filepath'] = str(savedfile.file_name.path)
            user = request.user
             
            storage = oauth2client.file.Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
            try:
                if not storage.get():
                    OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
                    CLIENT_SECRETS = 'gdrive/client_secrets.json'
                    REDIRECT_URI = 'http://localhost:8000/gdrive/firstwar/'
                    FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
                    FLOW.redirect_uri = REDIRECT_URI
                    GoogleDriveCoreModel(user=user,flow=FLOW).save()
                    authorize_url = FLOW.step1_get_authorize_url()
                    return redirect(authorize_url)
                else:
                    credentials = storage.get()
                    return google_file_exce(credentials,request)
            except:
                os.remove(BASE_DIR+'/gdrive/Storage/UserID_'+str(request.user.id)+'_FirstDriveToken')
                return redirect('/')
            
    elif request.method == 'GET':
        if request.GET.get('code'):
            token = request.GET.get("code")
     
            user = User.objects.get(id=request.user.id)
            FLOW = GoogleDriveCoreModel.objects.get(user_id=user.id).flow
             
            credentials = FLOW.step2_exchange(token)
            storage = oauth2client.file.Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
            storage.put(credentials)
             
            return google_file_exce(credentials,request)
        else:
            form = FileForm() 
                 
    return render(request,'gdrive/firstwar/uploadfile.html',{'form':form,'user':request.user.id})
 
 
def google_file_exce(credentials,request):
    FileName = request.session['filename']
    MimeType = request.session['mimetype']
    FilePath = request.session['filepath']
    try:
        http = httplib2.Http()
        credentials.authorize(http) 
                  
        drive_service = build('drive', 'v2', http=http)
        
        media_body = apiclient.http.MediaFileUpload(
                                                    FilePath,
                                                    mimetype=MimeType,
                                                    resumable=True
                                                    )
        body = {
                'title': FileName,
                'description': 'A shiny new text document about hello world.',
                }
        drive_service.files().insert(body=body, media_body=media_body).execute()
        
#         def retrieve_all_files(service):
#             result = []
#             page_token = None
#             while True:
#                 try:
#                     param = {}
#                     if page_token:
#                         param['pageToken'] = page_token
#                     files = service.files().list(**param).execute()
#                       
#                     result.extend(files['items'])
#                     page_token = files.get('nextPageToken')
#                     if not page_token:
#                         break
#                 except errors.HttpError, error:
#                     print 'An error occurred: %s' % error
#                      
#                     import pdb; pdb.set_trace()
#                     break
#             return result
#         result = retrieve_all_files(drive_service)
         
         
        return HttpResponse('File added : ' + FileName )
    except :
        os.remove(BASE_DIR+'/gdrive/Storage/UserID_'+str(request.user.id)+'_FirstDriveToken' )
        return redirect('/gdrive/')
         
     
     
     
     
     
     
     
     
     