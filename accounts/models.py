from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from base.models import BaseModel


# Create your models here.

class Profile(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to="profile")
    phone_number = models.CharField(max_length=20, null=True, blank=True, default='')
    profile_image = models.ImageField(upload_to="profile", default="default_profile.jpg")



class Address(BaseModel):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    house_name =models.CharField(max_length=150)
    street = models.CharField(max_length=150)
    pincode = models.IntegerField()
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number = models.IntegerField()
    alternate_number = models.IntegerField()
    user = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="user_address")
    
    