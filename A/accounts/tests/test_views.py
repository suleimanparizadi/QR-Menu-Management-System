from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from accounts.models import User, OTPcode
from rest_framework import status
from unittest.mock import patch



class TestUserRegistration(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:user_register')
        self.valid_data = {
            'username': 'spongebob',
            'phone_number':'0123456789',
            'password':'1234',
            'password2':'1234'
        }
        self.invaild_data = {
            'username':'',
            'phone_number':'InvaildPhonNumber',
            'password':'notmatch',
            'password2':'password'
        }

    def test_vaild_register(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'user will receive a code')
        self.assertTrue(OTPcode.objects.filter(phone_number='0123456789').exists())
        self.assertEqual(OTPcode.objects.count(), 1)

    def test_invalid_register(self):
        response = self.client.post(self.url, self.invaild_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('phone_number', response.data)


class TestUserPhoneVerify(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:phone_verify')
        self.user_session = {
            'username':'spongeboe',
            'phone_number':'0123456789',
            'password':'1234',
        }

        self.valid_otp = 1999
        self.invalid_otp = 2347

        OTPcode.objects.create(phone_number='0123456789', code=self.valid_otp)


    def test_successful_verification(self):

        session = self.client.session
        session['user_register_session'] = self.user_session
        session.save()

   
        response = self.client.post(self.url, data={'code':self.valid_otp}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'SignUp successfully')
        self.assertEqual(User.objects.count(), 1)
        self.assertIn('token', response.data)


    def test_fail_verification(self):
        
        session = self.client.session
        session['user_register_session'] = self.user_session
        session.save()

        response = self.client.post(self.url, data={'code':self.invalid_otp}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['detail'], 'the code is incorrect')


    def test_expired_session_verification(self):

        response = self.client.post(self.url, data={'code':self.valid_otp}, format='json')

        self.assertEqual(response.status_code, status.HTTP_308_PERMANENT_REDIRECT)
        self.assertIn(response.data['detail'], 'session is expired redirect to user_register')


class TestLoginPassword(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='spongebob',
                                 phone_number='0123456789',
                                 password='1234')
        
        self.url = reverse('accounts:login_password')
    
    
    def test_success_login_username(self):
        data = {
            'identifier':'spongebob',
            'password':'1234'
        }
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)        


    def test_success_login_phone_number(self):

        data = {
            'identifier':'0123456789',
            'password':'1234'
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)        


    def test_fail_login(self):
        data = {
            'identifier':'patric',
            'password':'2444'
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['detail'], 'username or password is incorrect')


class TestLoginSendCode(APITestCase):

    def setUp(self):
        User.objects.create_user(username='spongebob',
                                 phone_number='0123456789',
                                 password='1234')
        self.url = reverse('accounts:login_send_code')

    def test_success_send_code(self):
        data = {
            'phone_number':'0123456789'
        }

        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(OTPcode.objects.count(), 1)
        self.assertTrue(OTPcode.objects.filter(phone_number='0123456789').exists())    
        self.assertEqual(response.data['detail'], 'user will receive a code')



    def test_fail_send_code(self):

        data = {
            'phone_number':'0244466666'
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_308_PERMANENT_REDIRECT)
        self.assertIn(response.data['detail'], 'user not singup')
        self.assertEqual(response.data['redirect_url'], reverse('accounts:user_register'))


class TestLogiReceiveCode(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:login_receive_code')


        self.vaild_code = 1993
        self.invalid_code = 4567

        User.objects.create_user(username='spongebob',
                                 phone_number='0123456789',
                                 password='1234')
        OTPcode.objects.create(phone_number='0123456789', code=self.vaild_code)
    
    
    def test_success_verify(self):
        session = self.client.session
        session['user_phone_number'] = {'user_phone': '0123456789'}  
        session.save()

        response = self.client.post(self.url, data={'code': self.vaild_code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


class TestLogoutView(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:logout')
        self.user = User.objects.create(username='testuser',
                                        phone_number='0123456789',
                                        password='1234')
        
        

    def success_logout(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'user has been loged out')


    def fail_logout(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'user not loged in')





class TestUpdateProfile(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username = 'squidward',
            phone_number = '0123456789',
            password = '1234',
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('accounts:profile_update', kwargs={'pk':self.user.id})

    
    def test_update_profile(self):
        data = {
            'username':'Mr.Squidward',
            'phone_number':'0987654321'
        }

        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



