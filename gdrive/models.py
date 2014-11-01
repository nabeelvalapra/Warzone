from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import FlowField, CredentialsField
from Warzone.settings import DRIVE_FILES


class DriveFiles(models.Model):
    file_name = models.FileField(upload_to=DRIVE_FILES)
    
    class Meta:
        db_table = 'temp_drive_file'


class GoogleDriveCoreModel(models.Model):
    user = models.OneToOneField(User)
    flow = FlowField()
    credential = CredentialsField()
    
    class Meta:
        db_table = 'google_drive_core_model'    


class MainFolderIDModel(models.Model):
    user = models.OneToOneField(User)
    mainfolderID = models.CharField(max_length=200)
    class Meta:
        db_table = 'main_folder_id_model'


class FileInfo(models.Model):
    id = models.AutoField(primary_key=True)
    fileinfo = models.CharField(max_length=150,unique=True)
    class Meta:
        db_table = 'file_info'
