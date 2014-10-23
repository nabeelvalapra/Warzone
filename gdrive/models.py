from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import FlowField, CredentialsField
from Warzone.settings import DRIVE_FILES


class DriveFiles(models.Model):
    file_name = models.FileField(upload_to=DRIVE_FILES)
    
    class Meta:
        db_table = 'drivefile'
        

class FlowModel(models.Model):
    user = models.ForeignKey(User,primary_key=True)
    flow = FlowField()
    
    class Meta:
        db_table = 'flow_model'
        
        
class CredentialsModel(models.Model):
    user = models.ForeignKey(User)
    credential = CredentialsField()

    class Meta:
        db_table = 'credential_model'
        
