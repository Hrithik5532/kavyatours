from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20,unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    
    address = models.TextField(null=True, blank=True)
    email = models.EmailField( null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    def __str__(self):
        return str(self.username)











class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name + ' - ' + 'Date  :  ' + str(self.created_at)