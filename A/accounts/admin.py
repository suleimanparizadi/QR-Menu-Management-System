from django.contrib import admin
from .models import User, OTPcode
from django.contrib.auth.models import Group



admin.site.unregister(Group)
admin.site.register(OTPcode)
admin.site.register(User)