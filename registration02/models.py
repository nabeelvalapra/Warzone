from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    
    address = models.TextField(null=True)
    phone_num = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'user_profile'
    
    def __unicode__(self):
        return self.user.username
    
