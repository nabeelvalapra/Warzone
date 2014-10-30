from django.http.response import HttpResponse
from gdrive.models import MainFolderIDModel, GoogleDriveCoreModel
from apiclient import errors
from apiclient.http import MediaFileUpload
import httplib2
from apiclient.discovery import build
import oauth2client
from django.contrib.auth.models import User
from django.core.files.base import File


APP_NAME = 'MyFirstDrive'
def createflow(request):
    OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive.file'
    CLIENT_SECRETS = 'gdrive/client_secrets.json'
    REDIRECT_URI = 'http://localhost:8000/gdrive/secondwar/code/'
    
    FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
    FLOW.redirect_uri = REDIRECT_URI
    GoogleDriveCoreModel(user=request.user,flow=FLOW).save() #Save the flow to DB.
    authorize_url = FLOW.step1_get_authorize_url()
    return authorize_url

def retriveflow(request):
    user = User.objects.get(id=request.user.id)
    Flow = GoogleDriveCoreModel.objects.get(user_id=user.id).flow
    return Flow

def savecredential(request, credential):
    GoogleDriveCoreModel.objects.filter(user=request.user).update(credential=credential)
    return True

def has_credential(request):
    if GoogleDriveCoreModel.objects.filter(user_id=request.user.id).exists():
        return GoogleDriveCoreModel.objects.get(user_id=request.user.id).credential
    else:
        return False

def create_service(creds):
    http = httplib2.Http()
    creds.authorize(http)
    return build('drive', 'v2', http=http)  

def create_Folder(service, APP_NAME, parentID = None):
    body = {
      'title': APP_NAME,
      'mimeType': "application/vnd.google-apps.folder"
    }
    if parentID:
        body['parents'] = [{'id': parentID}]
    root_folder = service.files().insert(body = body).execute()
    return root_folder['id'] 
 
def main_folder_exists(service,mainfolderID):
    meta_list = retrieve_all_files(service)
    for _ in meta_list:
        if _['id'] == str(mainfolderID):
            return True
    return False
    
def create_main_folder_and_save_id(request, service):
    folder_id = create_Folder(service, APP_NAME)
    MainFolderIDModel(user_id=request.user.id,mainfolderID=folder_id).save()
    return folder_id

def insert_file(service, title, description, parent_id, mime_type, filename):
    media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
    body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
    }
    if parent_id:
        body['parents'] = [{'id': parent_id}]
    try:
        file = service.files().insert(
                                      body=body,
                                      media_body=media_body
                                      ).execute()
        return file
    except errors.HttpError, error:
        print 'An error occured: %s' % error
        return None
    
def retrieve_all_files(service,query=''):
    filelist = service.files().list(q=query).execute()
    return filelist['items']

def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def filehandler(request, credentials, action):
    service = create_service(credentials)
    
    if MainFolderIDModel.objects.filter(user_id=request.user.id).exists():
        mainfolderID = MainFolderIDModel.objects.get(user_id=request.user.id).mainfolderID
        if not main_folder_exists(service, mainfolderID):
            MainFolderIDModel.objects.filter(user_id=request.user.id).delete()
            mainfolderID = create_main_folder_and_save_id(request, service)
    else:
        mainfolderID = create_main_folder_and_save_id(request, service)
        
    if action == '1':
        FileName = request.session['filename']
        FilePath = request.session['filepath']
        MimeType = request.session['mimetype'] 
        #thefile = open(FilePath, 'w')
        #import pdb;pdb.set_trace()
        file = insert_file(service, FileName, 'description', mainfolderID, MimeType, FilePath) 
        if file:
            #All file details can be fetched from 'file' variable.
            return HttpResponse('Attaboy, you got the filehander, the file seems uploaded!!!')
        else:
            return HttpResponse('Sorry')
        
    elif action == '2':
        q = "'%s' in parents" % mainfolderID
        file_list = retrieve_all_files(service, query=q)
        outstring = '<br>'
        for file in file_list:
            
            outstring += '<a href="https://drive.google.com/uc?id=' + file['id'] + '">'+file['title']+'</a><br>'
            outstring += '<br>'
        return HttpResponse('Your files are:' + outstring)
    
    elif action == '3':
        mainfolderID = ''
        if MainFolderIDModel.objects.filter(user_id=request.user.id).exists():
            mainfolderID = MainFolderIDModel.objects.get(user_id=request.user.id).mainfolderID
            if not main_folder_exists(service, mainfolderID):
                return HttpResponse('File not exist.')
            else:
                delete_file(service, mainfolderID)
        return HttpResponse('File deleted')

