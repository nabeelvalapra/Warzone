from django.shortcuts import render,redirect, render_to_response
from django.http.response import HttpResponse, HttpResponseRedirect
import httplib2
import apiclient
from gdrive.models import FlowModel, CredentialsModel, DriveFiles
from django.contrib.auth.models import User
import oauth2client
from apiclient.discovery import build
from gdrive.forms import FileForm
from django.contrib.auth.decorators import login_required
import os
from Warzone.settings import BASE_DIR, DRIVE_FILES
from django.core import serializers
from apiclient import errors

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


@login_required
def upload2(request):
    def createflow():
        OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
        CLIENT_SECRETS = 'gdrive/client_secrets.json'
        REDIRECT_URI = 'http://localhost:8000/gdrive/secondwar/'
        
        FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
        FLOW.redirect_uri = REDIRECT_URI
        FlowModel(user=user,flow=FLOW).save() #Save the flow to DB.
        authorize_url = FLOW.step1_get_authorize_url()
        return authorize_url
    
    def retriveflow():
        user = User.objects.get(id=request.user.id)
        Flow = FlowModel.objects.get(user_id=user.id).flow
        return Flow
    
    def savecredential(credential, _type):
        CredentialsModel(user=request.user,credential=credential).save()
        return True
    
    def has_credential():
        if CredentialsModel.objects.filter(user_id=request.user.id).exists():
            return CredentialsModel.objects.get(user_id=request.user.id).credential
        else:
            return False
        
    def filehandler(credentials, action):
        
        gauth = GoogleAuth()
        gauth.credentials = credentials
        drive = GoogleDrive(gauth)
        if action == 'upload':
            FileName = request.session['filename']
            FilePath = request.session['filepath']
            
            file1 = drive.CreateFile({'title': FileName})
            file1.SetContentFile(FilePath)
            file1.Upload()
        else:
            file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
            filelist = '<br>'
            for file in file_list:
                filelist += file['title']
                filelist += '<br>'
            return HttpResponse(filelist)
        return HttpResponse('Attaboy, you got the filehander, the file seems uploaded!!!')
    
#============================================================================================================ 
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            
            savedfile = form.save()
            request.session['file_id'] = str(savedfile.id)
            request.session['filename'] = str(request.FILES['file_name'])
            request.session['filepath'] = str(savedfile.file_name.path)
                                    
            try:
                if has_credential():   
                    credentials = has_credential()
                    return filehandler(credentials, 'upload')
                else:
                    
                    authorize_url = createflow()
                    return redirect(authorize_url)
            except Exception,e:
                try:
                    CredentialsModel.objects.filter(user_id=request.user.id).delete()
                except:
                    pass
                finally:
                    return HttpResponse(str(e) + '<br> An Error has Occured:::Exception')
            
    elif request.method == 'GET':
        if request.GET.get('code'):
            token = request.GET.get('code')
            
            Flow = retriveflow()
            credentials = Flow.step2_exchange(token)
            savecredential(credentials,'DB')
            
            return filehandler(credentials, 'upload')
        else:
            form = FileForm() 
        
    return render(request,'gdrive/secondwar/uploadfile.html',{'form':form,'user':request.user.id})


    
    
 
#============================================================================================================
#============================================================================================================
#============================================================================================================
#============================================================================================================
#============================================================================================================
#============================================================================================================
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
                    FlowModel(user=user,flow=FLOW).save()
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
            FLOW = FlowModel.objects.get(user_id=user.id).flow
             
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
         
     
     
     
     
     
     
     
     
     