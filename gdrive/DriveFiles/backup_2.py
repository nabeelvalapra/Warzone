from django.shortcuts import render,redirect, render_to_response
from django.http.response import HttpResponse
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

@login_required
def upload(request):
#     def gdrive_add_account(user):        
#         OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
#         CLIENT_SECRETS = 'client_secrets.json'
#         REDIRECT_URI = 'http://localhost:8000/gdrive/callback/'
#         
#         FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
#         FLOW.redirect_uri = REDIRECT_URI
#         FlowModel(user=user,flow=FLOW).save()
#         authorize_url = FLOW.step1_get_authorize_url()
#         render(authorize_url)
#         return 0
#         request.session['FILENAME'] = FILENAME
#         request.session['MIMETYPE'] = MIMETYPE
#         request.session['TITLE'] = TITLE
#         request.session['DESCRIPTION'] = DESCRIPTION
#         
#         request.session.save() 
        
        
    if request.method == 'POST':
        form = FileForm(request.POST,request.FILES)
        if form.is_valid():
            user = request.user
            
            OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
            CLIENT_SECRETS = 'client_secrets.json'
            REDIRECT_URI = 'http://localhost:8000/gdrive/callback/'
            
            FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
            FLOW.redirect_uri = REDIRECT_URI
            authorize_url = FLOW.step1_get_authorize_url()
            
            return redirect(authorize_url)
            
        
#             a = gdrive_add_account(user)
#             return render_to_response(a)
#             form.save()
#             f = DriveFiles.objects.get(id=1)
#             fname = str(f.file_name)
#             fpath = str(BASE_DIR) + '/' + str(DRIVE_FILES) + '/'
            
            return HttpResponse('Your file is saved')
    return render(request,'gdrive/uploadfile.html')



    
 

@login_required
def gdrive_callback(request):
    code = request.GET.get("code")
    
    id = User.objects.get(id=request.user.id).id
    FLOW = FlowModel.objects.get(id=id).flow
    
    FILENAME = request.session.get('FILENAME')
    MIMETYPE = request.session.get('MIMETYPE')
    TITLE = request.session.get('TITLE')
    DESCRIPTION = request.session.get('DESCRIPTION')
    
    credentials = FLOW.step2_exchange(code)
    user_id = User.objects.get(id=request.user.id)
    CredentialsModel(user=user_id,credential=credentials).save()
    
    # Create an authorized Drive API client.
    http = httplib2.Http()
    credentials.authorize(http)
    drive_service = build('drive', 'v2', http=http)
     
    # Insert a file. Files are comprised of contents and metadata.
    # MediaFileUpload abstracts uploading file contents from a file on disk.
    media_body = apiclient.http.MediaFileUpload(
        '/home/nabeel/django/Warzone/GFILES/ex.txt',
        mimetype=MIMETYPE,
        resumable=True
    )
    # The body contains the metadata for the file.
    body = {
      'title': TITLE,
      'description': DESCRIPTION,
    }
     
    # Perform the request and print the result.
    new_file = drive_service.files().insert(body=body, media_body=media_body).execute()
    
    return HttpResponse('file added')
    
    
    
    
    
    
    
    
    
