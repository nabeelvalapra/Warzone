from django.shortcuts import render,redirect
from django.http.response import HttpResponse
import httplib2
import apiclient
from gdrive.models import FlowModel, CredentialsModel, DriveFiles
from django.contrib.auth.models import User
import oauth2client
from apiclient.discovery import build
from gdrive.forms import FileForm
from django.contrib.auth.decorators import login_required

@login_required
def upload(request):
    if request.method == 'POST':
        form = FileForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            file = DriveFiles.objects.get(id=1)
            file_name = file.file_name
            file_path = file.file_name.path
            import pdb; pdb.set_trace()
            
            return HttpResponse('Your file is saved')
    return render(request,'gdrive/uploadfile.html')

@login_required
def gdrive_add_account(request):
    OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRETS = 'client_secrets.json'
    
    # Path to the file to upload.
    FILENAME = 'ex.txt'
    FILEPATH = ''
    
    # Metadata about the file.
    MIMETYPE = 'text/plain'
    TITLE = 'My Second Text Document'
    DESCRIPTION = 'A shiny new text document about hello world.'
    
    # Perform OAuth2.0 authorization flow.
    FLOW = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
    FLOW.redirect_uri = 'http://localhost:8000/gdrive/callback/'
    authorize_url = FLOW.step1_get_authorize_url()
    
    user_id = User.objects.get(id=request.user.id)
    FlowModel(user=user_id,flow=FLOW).save()
    
    request.session['FILENAME'] = FILENAME
    request.session['MIMETYPE'] = MIMETYPE
    request.session['TITLE'] = TITLE
    request.session['DESCRIPTION'] = DESCRIPTION
    
    request.session.save() 
    
    return redirect(authorize_url)
 

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
    
    
    
    
    
    
    
    
    
