from .models import User


class PhoneNumberLogin:

    def authenticate(self, request, identifier=None, password=None):
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=identifier)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        
    def get_user(self, user_id):
        try:
           return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        

       