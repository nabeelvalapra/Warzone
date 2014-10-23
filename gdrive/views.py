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


@login_required
def upload(request):
    if request.method == 'POST':
        form = FileForm(request.POST,request.FILES)
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
                    REDIRECT_URI = 'http://localhost:8000/gdrive/callback/'
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
    else:
        form = FileForm()    
                
    return render(request,'gdrive/uploadfile.html',{'form':form,'user':request.user.id})


@login_required
def gdrive_callback(request):
    token = request.GET.get("code")
    
    user = User.objects.get(id=request.user.id)
    FLOW = FlowModel.objects.get(user_id=user.id).flow
    
    credentials = FLOW.step2_exchange(token)
    storage = Storage('gdrive/Storage/UserID_'+str(user.id)+'_FirstDriveToken')
    storage.put(credentials)
    
    return google_file_exce(credentials,request)


def google_file_exce(credentials,request):
    drivefile_id = request.session['drivefile_id']
    FileName = request.session['filename']
    MimeType = request.session['mimetype']
    FilePath = request.session['filepath']
    try:
        http = httplib2.Http()
        credentials.authorize(http) 
                 
        drive_service = build('drive', 'v2', http=http)
        def retrieve_all_files(service):
            result = []
            page_token = None
            while True:
                try:
                    param = {}
                    if page_token:
                        param['pageToken'] = page_token
                    files = service.files().list(**param).execute()
                     
                    result.extend(files['items'])
                    page_token = files.get('nextPageToken')
                    if not page_token:
                        break
                except errors.HttpError, error:
                    print 'An error occurred: %s' % error
                    
                    import pdb; pdb.set_trace()
                    break
            return result
        
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
        result = retrieve_all_files(drive_service)
        return HttpResponse('File added : ' + FileName + 'aa' + str(result))
    except Exception,e:
        import pdb; pdb.set_trace()
        os.remove(BASE_DIR+'/gdrive/Storage/UserID_'+str(request.user.id)+'_FirstDriveToken' )
        return redirect('/gdrive/')
        
    
    
    
    
    
    
    
    
    