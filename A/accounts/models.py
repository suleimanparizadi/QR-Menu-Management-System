from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManger



class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=125)
    phone_number = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS =[
        'username'
    ]

    objects = UserManger()

    def __str__(self):
        return f"{self.username}-{self.phone_number}-{self.id}"



    
    def has_perm(self, perm, obj = ...):
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        return super().has_module_perms(app_label)
 
    def is_staff(self):
        return self.is_admin
    
    
class OTPcode(models.Model):
    phone_number = models.CharField(max_length=11)
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def  __str__(self):
        return f"{self.phone_number}-{self.code}"
    
