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
from oauth2client.file import Storage
from django.core import serializers
from apiclient import errors

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


@login_required
def upload2(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            
            savedfile = form.save()
             
            request.session['file_id'] = str(savedfile.id)
            request.session['filename'] = str(request.FILES['file_name'])
            request.session['filepath'] = str(savedfile.file_name.path)
                                    
            storage = Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
            
            try:
                if not storage.get():  # 'not' is important for testing
                    OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
                    CLIENT_SECRETS = 'gdrive/client_secrets.json'
                    REDIRECT_URI = 'http://localhost:8000/gdrive/secondwar/'
                    FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
                    FLOW.redirect_uri = REDIRECT_URI
                    FlowModel(user=user,flow=FLOW).save()
                    authorize_url = FLOW.step1_get_authorize_url()
                    
                    return redirect(authorize_url)
                
                else:
                    credentials = storage.get()
                    return filehandler(request, credentials, 'upload')
            except:
                os.remove(BASE_DIR+'/gdrive/Storage/UserID_'+str(request.user.id)+'_FirstDriveToken')
                return redirect('/')

    elif request.method == 'GET':
        if request.GET.get('code'):
            token = request.GET.get('code')
            user = User.objects.get(id=request.user.id)
            FLOW = FlowModel.objects.get(user_id=user.id).flow
             
            credentials = FLOW.step2_exchange(token)
            storage = Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
            storage.put(credentials)
            
            return filehandler(request, credentials, 'upload')
        
        else:
            form = FileForm() 
        
    return render(request,'gdrive/secondwar/uploadfile.html',{'form':form,'user':request.user.id})


def filehandler(request, credentials, action):
    gauth = GoogleAuth()
    gauth.credentials = credentials
            
    FileName = request.session['filename']
    FilePath = request.session['filepath']
    
    drive = GoogleDrive(gauth)
    file1 = drive.CreateFile({'title': FileName})
    file1.SetContentFile(FilePath)
    file1.Upload()
    
    return HttpResponse('Attaboy, you got the filehander, the file seems uploaded!!!')
    
 
 
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
             
            storage = Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
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
            storage = Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
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
         
     
     
     
     
     
     
     
     
     