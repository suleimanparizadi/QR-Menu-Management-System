from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import User, OTPcode


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = [
            'username', 'phone_number', 'password', 'password2'
        ]

    def validate(self, attrs):
        password = attrs.get('password')
        passwrod2 = attrs.get('password2')
        if password and passwrod2:
             if password != passwrod2:
                  raise serializers.ValidationError('passwords must match')
        attrs.pop('password2', None)
        return attrs
    


class OTPserializer(serializers.ModelSerializer):
        class Meta:
             model = OTPcode
             fields = [
                  'code'
             ]

class UserloginPasswordSerializer(serializers.Serializer):
     
     identifier = serializers.CharField(required=True)
     password = serializers.CharField(required=True)  


class UserLoginSendCodeSerializer(serializers.Serializer):
     
     phone_number = serializers.CharField(required=True)

class UserLoginReceiveCodeSerializer(serializers.Serializer):
     code = serializers.IntegerField(required=True)