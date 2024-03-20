import uuid
from django.db import models
from django.contrib.auth.models import  PermissionsMixin,AbstractUser
from .managers import *

# Create your models here.
class CustomUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Почта",max_length=100,null=True,unique=True)
    first_name = models.CharField(max_length=100,verbose_name="Имя")
    last_name = models.CharField(max_length=100,verbose_name="Фамилия")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(verbose_name="Когда зарегистрирован",auto_now_add=True)
    username = models.CharField(verbose_name = 'Логин',max_length=100,unique=True)
    USERNAME_FIELD = ('username')
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email','first_name','last_name']

    objects = CustomUserManager()


    def __str__(self):
        return self.email
    

