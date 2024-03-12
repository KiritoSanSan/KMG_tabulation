from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    
    def create_user(self,username,email,password,first_name,last_name,**kwargs):
        if not email:
            raise ValueError(_("The email must be set"))
        if email:
            email = self.normalize_email(email)
            if username is None:
                username = email.split('@',1)[0]
            
        
        user = self.model(username=username,email=email,password=password,first_name=first_name,last_name=last_name,**kwargs)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self,username,password,first_name,last_name,**kwargs):
        kwargs.setdefault('is_staff',True)
        kwargs.setdefault('is_superuser',True)
        kwargs.setdefault('is_active',True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('superuser must have is_staff=True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('superuser must have is_superuser=True')
        return self.create_user(username=username,password=password,first_name=first_name,last_name=last_name,**kwargs)
    
