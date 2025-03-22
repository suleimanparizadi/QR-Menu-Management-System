from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('register/verify/', views.UserPhoneVerfiy.as_view(), name='phone_verify'),
    path('login_password/', views.UserLoginPassword.as_view(), name='login_password'),
    path('logine_send_code/', views.UserLoginSendCode.as_view(), name='login_send_code'),
    path('login_receive_code/', views.UserLoginReceiveCode.as_view(), name='login_receive_code'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('update_account/<int:pk>/', views.UserUpdateProfile.as_view(), name='profile_update'),

    
]
