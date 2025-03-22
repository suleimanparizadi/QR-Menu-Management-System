from django.contrib.auth.models import BaseUserManager


class UserManger(BaseUserManager):

    def create_user(self, username, phone_number, password):
        
        if username is None:
            raise ValueError("user name is required")
        
        if phone_number is None:
            raise ValueError("phone number is required")
        
        user = self.model(phone_number=phone_number, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, phone_number, password ):
        user = self.create_user(username, phone_number, password)
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user
    
