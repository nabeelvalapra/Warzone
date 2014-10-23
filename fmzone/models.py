from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Company(models.Model):
    name = models.CharField(
                            max_length=100,
                            help_text='Please enter your name of your great company')
    
    class Meta:
        db_table = 'company'
    
    def __str__(self):
        return self.name
    
    
class Persons(models.Model):
    full_name = models.CharField(
                                 max_length=100,
                                 help_text='Please enter your FullName Here.'
                                 )
    dob = models.DateField(
                           null=True,
                           help_text='The date you first came to this world.'
                           )
    ShirtSizes = (
            ('S','Small'),
            ('M','Medium'),
            ('L','Large')
    )
    shirt_size = models.CharField(
                                  null=True,
                                  max_length=1,
                                  choices=ShirtSizes,
                                  default='M'
    )
    email = models.EmailField(unique=True)
    phone_num = models.BigIntegerField(
                                       null=True,
                                       help_text='Please enter your unique phone number'
                                       )
    address = models.TextField(null=True)
    contact = models.ManyToManyField(Company)
    
    
    
#     def clean(self):
#         if self.email in Persons.objects.all():
#             raise ValidationError('Hello..Hellooo....')
        
    class Meta:
        db_table = 'persons'
        
    def __unicode__(self):
        return self.full_name

