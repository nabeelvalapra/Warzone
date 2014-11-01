from django.http.response import HttpResponse
from gdrive.models import MainFolderIDModel, GoogleDriveCoreModel, FileInfo
from apiclient import errors
from apiclient.http import MediaFileUpload
import httplib2
from apiclient.discovery import build
import oauth2client
from django.contrib.auth.models import User
from django.shortcuts import redirect
import os
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


APP_NAME = 'MyFirstDrive'


def createflow(request):
    try:
        OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive.file'
        CLIENT_SECRETS = 'gdrive/client_secrets.json'
        REDIRECT_URI = 'http://localhost:8000/gdrive/secondwar/code/'
        
        FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
        FLOW.redirect_uri = REDIRECT_URI
        GoogleDriveCoreModel(user=request.user,flow=FLOW).save() #Save the flow to DB.
        authorize_url = FLOW.step1_get_authorize_url()
        return authorize_url
    except:
        raise Exception('Sorry we could not create a flow for you. Please try again.')


def retriveflow(request):
    try:
        user = User.objects.get(id=request.user.id)
        Flow = GoogleDriveCoreModel.objects.get(user_id=user.id).flow
        return Flow
    except:
        raise Exception("Sorry we could'nt retrive flow for you, Please try again")


def savecredential(request, credential):
    try:
        GoogleDriveCoreModel.objects.filter(user=request.user).update(credential=credential)
        return True
    except:
        raise Exception("Sorry we had an error in saving your credential.")


def has_credential(request):
    try:
        if GoogleDriveCoreModel.objects.filter(user_id=request.user.id).exists():
            return GoogleDriveCoreModel.objects.get(user_id=request.user.id).credential
        else:
            return False
    except:
        raise Exception("Sorry we had an error in retriving your Credential.")


def create_service(creds):
    try:
        http = httplib2.Http()
        creds.authorize(http)
        _build = build('drive', 'v2', http=http)
        return _build
    except Exception, e:
        raise Exception('Sorry could not connect to your google drive, There was an error in creating a service. <br>' + str(e))
      
        
def create_Folder(service, APP_NAME, parentID = None):
    try:
        body = {
          'title': APP_NAME,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [{'id': parentID}]
        root_folder = service.files().insert(body = body).execute()
        return root_folder['id'] 
    except:
        raise Exception("Sorry we have an error in creating a folder in your Google drive account.")
 
 
def main_folder_exists(service,mainfolderID):
    meta_list = retrieve_all_files(service)
    for _ in meta_list:
        if _['id'] == str(mainfolderID):
            return True
    return False
    
    
def create_main_folder_and_save_id(request, service):
    try:
        folder_id = create_Folder(service, APP_NAME)
        MainFolderIDModel(user_id=request.user.id,mainfolderID=folder_id).save()
        return folder_id
    except:
        raise Exception(" There is a error in creating main folder in your google drive account.")


def insert_file(service, FileName, FilePath, parent_id):
    try:
        media_body = MediaFileUpload(FilePath, resumable=False)
        body = {
                'title': FileName
        }
        if parent_id:
            body['parents'] = [{'id': parent_id}]
        
        _file = service.files().insert(
                                      body=body,
                                      media_body=media_body
                                      ).execute()
        return _file
    except:
        raise Exception('Your file seems corupted, you have an error in the insert function')
    
    
def retrieve_all_files(service,query=''):
        filelist = service.files().list(q=query).execute()
        return filelist['items']


def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
    except:
        raise Exception("There was an error in deleting files.")


def Upload_File_Handler(request, credentials, service, mainfolderID, FileName, FilePath):
    try:
        _file = insert_file(service, FileName, FilePath, parent_id=mainfolderID) 
        if _file:
            f = FileInfo(fileinfo=_file['id']).save()
            os.remove(FilePath)
            #f.id can be returned if necessary.
            return HttpResponse('Boy, you got the filehander, the file seems uploaded!!!')
    except Exception, e:
        raise Exception("Oops, there was an error in your filehandler function<br>" + str(e))
    

def auth_check(view_func): 
    def _wrapped_view_func(request, *args, **kwargs): 
        try:
            if has_credential(request):   
                credentials = has_credential(request)
                service = create_service(credentials)
                if MainFolderIDModel.objects.filter(user_id=request.user.id).exists():
                    mainfolderID = MainFolderIDModel.objects.get(user_id=request.user.id).mainfolderID
                    if not main_folder_exists(service, mainfolderID):
                        MainFolderIDModel.objects.filter(user_id=request.user.id).delete()
                        mainfolderID = create_main_folder_and_save_id(request, service)
                else:
                    mainfolderID = create_main_folder_and_save_id(request, service)
                    
                if mainfolderID:
                    
                    kwargs['credentials'] = credentials
                    kwargs['service'] = service
                    kwargs['mainfolderID'] = mainfolderID
                    
                    return view_func(request,  *args, **kwargs) 
                else:
                    return HttpResponse('You have a serious error!!!')
            else:
                authorize_url = createflow(request)
                return redirect(authorize_url)
        except Exception, e:
#             GoogleDriveCoreModel.objects.filter(user_id=request.user.id).delete()
#             authorize_url = createflow(request)
#             return redirect(authorize_url) 
            return HttpResponse("You had an exception in Auth_check.<br>" + str(e))
    return _wrapped_view_func


@login_required(login_url='/registration02/')
def gdrive_callback(request):
    token = request.GET.get('code')
    if token:
        Flow = retriveflow(request)
        credentials = Flow.step2_exchange(token)
        savecredential(request, credentials)
        service = create_service(credentials)

        return redirect(reverse('index2'))
    else:
        return HttpResponse('Oops, you cannot use this application without the permission of google drive. Sorry..')
