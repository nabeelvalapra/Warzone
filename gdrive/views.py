from django.shortcuts import render,redirect, render_to_response
from django.http.response import HttpResponse, HttpResponseRedirect
import httplib2
import apiclient
from gdrive.models import DriveFiles, GoogleDriveCoreModel
from django.contrib.auth.models import User
import oauth2client
from apiclient.discovery import build
from gdrive.forms import FileForm, ChoicesForm
from django.contrib.auth.decorators import login_required
import os
from Warzone.settings import BASE_DIR, DRIVE_FILES
from django.core import serializers
from apiclient import errors

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json


@login_required
def upload2(request):
    APP_NAME = 'MyFirstDrive'
    MAIN_FOLDER_ID = ''
    def createflow():
        OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive.file'
        CLIENT_SECRETS = 'gdrive/client_secrets.json'
        REDIRECT_URI = 'http://localhost:8000/gdrive/secondwar/'
        
        FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
        FLOW.redirect_uri = REDIRECT_URI
        GoogleDriveCoreModel(user=user,flow=FLOW).save() #Save the flow to DB.
        authorize_url = FLOW.step1_get_authorize_url()
        return authorize_url
    
    def retriveflow():
        user = User.objects.get(id=request.user.id)
        Flow = GoogleDriveCoreModel.objects.get(user_id=user.id).flow
        return Flow
    
    def savecredential(credential):
        GoogleDriveCoreModel.objects.filter(user=request.user).update(credential=credential)
        return True
    
    def has_credential():
        if GoogleDriveCoreModel.objects.filter(user_id=request.user.id).exists():
            return GoogleDriveCoreModel.objects.get(user_id=request.user.id).credential
        else:
            return False
        
    def main_folder_exists(drive,mainfolderID):
        try:
            query = "'"+str(mainfolderID)+"' in parents and trashed=false"
            final_query = {'q':query}
            final = json.dumps(final_query)
            
            file_list = drive.ListFile(json.loads(final)).GetList()
            return file_list
        except:
            return False
        
    def create_main_folder_and_save_id(drive):
        if True:
            new_folder = drive.CreateFile({'title':'{}'.format(APP_NAME),
                                           'mimeType':'application/vnd.google-apps.folder'})
            new_folder.Upload()
            GoogleDriveCoreModel.objects.filter(user_id=request.user.id).update(mainfolderID=new_folder['id'])
            return new_folder['id']
        else:
            return False
        
    def filehandler(credentials, action):
        gauth = GoogleAuth()
        gauth.credentials = credentials
        drive = GoogleDrive(gauth)
        
        mainfolderID = GoogleDriveCoreModel.objects.get(user_id=request.user.id).mainfolderID  
        if mainfolderID == None:
            mainfolderID = 'mainfoldernotfound'     
        if not main_folder_exists(drive, mainfolderID):
            mainfolderID = create_main_folder_and_save_id(drive) 
            
        if action == '1':#Upload
            FileName = request.session['filename']
            FilePath = request.session['filepath']
            file1 = drive.CreateFile({'title': FileName,'parent': APP_NAME,'parents':[{u'id':str(mainfolderID) }]})
            file1.SetContentFile(FilePath)
            file1.Upload()
            return HttpResponse('Attaboy, you got the filehander, the file seems uploaded!!!')
        
        elif action == '2':#list
            query = "'"+str(mainfolderID)+"' in parents and trashed=false"
            final_query = {'q':query}
            final = json.dumps(final_query)
            file_list = drive.ListFile(json.loads(final)).GetList()
            filelist = '<br>'
            for file in file_list:
                #file_id = str(file['id'])
                #filelist += '<a href="https://drive.google.com/uc?id=' + file_id + '"/>' + '<br>'
                filelist += file['title']
                filelist += '<br>'
            return HttpResponse('Your files are:' + filelist)
        
        elif action == '3':
            if create_main_folder_and_save_id(drive):
                return HttpResponse('Creted new Folder!!!')
            else:
                return False
            
#========================================================================================================================================================== 
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        option = request.POST.get('choice')
        if form.is_valid():
            
            user = request.user
            
            savedfile = form.save()
            request.session['file_id'] = str(savedfile.id)
            request.session['filename'] = str(request.FILES['file_name'])
            request.session['filepath'] = str(savedfile.file_name.path)
                                    
            try:
                if has_credential():   
                    credentials = has_credential()
                    return filehandler(credentials, option)
                else:
                    authorize_url = createflow()
                    request.session['option'] = option
                    return redirect(authorize_url)
            except Exception,e:
                return HttpResponse('<br>Operation Failed!!! An Error has Occured:::Exception:::'+str(e))
            
    elif request.method == 'GET':
        if request.GET.get('code'):
            option = request.session['option']
            token = request.GET.get('code')
            
            Flow = retriveflow()
            credentials = Flow.step2_exchange(token)
            savecredential(credentials)
            
            return filehandler(credentials, option)
        else:
            form = FileForm() 
            choices = ChoicesForm()
    return render(request,'gdrive/secondwar/uploadfile.html',{'form':form,'choices':choices,'user':request.user.id})


    
    
 
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
#=============================================================================================================
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
         
     
     
     
     
     
     
     
     
     