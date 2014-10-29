from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import FlowField, CredentialsField
from Warzone.settings import DRIVE_FILES


class DriveFiles(models.Model):
    file_name = models.FileField(upload_to=DRIVE_FILES)
    
    class Meta:
        db_table = 'drivefile'

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
        db_table = 'mainfolderidmodel'

