from django.shortcuts import render,redirect
import apiclient
from gdrive.forms import FileForm, ChoicesForm
from django.contrib.auth.decorators import login_required
import os
from Warzone.settings import BASE_DIR 

from django.contrib.auth import logout
from GoogleDriveFunctions import *

@login_required(login_url='/registration02/')
def upload2(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        choices = ChoicesForm(request.POST)
        option = request.POST.get('choice')
        if form.is_valid():
            
            user = request.user
            savedfile = form.save()
            #request.session['file_id'] = str(savedfile.id)
            request.session['filename'] = str(request.FILES['file_name'])
            request.session['mimetype'] = str(request.FILES['file_name'].content_type)
            request.session['filepath'] = str(savedfile.file_name.path)
            file = request.FILES.get('file_name')
                                    
            try:
                #raise Exception('invalid_grand')
                if has_credential(request):   
                    credentials = has_credential(request)
                    return filehandler(request, credentials, option)
                else:
                    authorize_url = createflow(request)
                    request.session['option'] = option
                    return redirect(authorize_url)
                
            #except 'invalid_grant':
            #   return HttpResponse('Yeah!! Its an invalid grant.')
            except Exception,e:
                GoogleDriveCoreModel.objects.filter(user_id=request.user.id).delete()
                # FolderID need to be saved in another table.
                return HttpResponse('<br>Operation Failed!!! An Error has Occured:::Exception:::<br><br>'+str(e))
    else:
        form = FileForm() 
        choices = ChoicesForm()
    
                    
    return render(request,'gdrive/secondwar/uploadfile.html',{'form':form,'choices':choices,'user':request.user.id})

def gdrive_callback(request):
    token = request.GET.get('code')
    if token:
        option = request.session['option']
        Flow = retriveflow(request)
        credentials = Flow.step2_exchange(token)
        savecredential(request, credentials)
        return filehandler(request, credentials, option)

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
         
     
     
     
     
     
     
     
     
     