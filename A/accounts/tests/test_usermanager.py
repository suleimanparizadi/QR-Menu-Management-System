from accounts.manager import UserManger
from django.test import TestCase
from accounts.models import User

class TestUserManager(TestCase):

    def setUp(self):
        
        self.data = {
            'username':'testuser',
            'phone_number':'0123456789',
            'password':'1234'
        }

    def test_user_creation(self):
        user = User.objects.create_user(
            username = self.data['username'],
            phone_number = self.data['phone_number'],
            password = self.data['password']
        )

        self.assertEqual(user.username, self.data['username'])
        self.assertEqual(user.phone_number, self.data['phone_number'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_admin)


    def test_missing_username(self):
        
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username = None,
                phone_number = self.data['username'],
                password = self.data['password']
            )
        self.assertEqual(str(context.exception), 'user name is required')


    def test_missing_phone_number(self):
            with self.assertRaises(ValueError) as context:
                 User.objects.create_user(
                      username = 'testuser',
                      phone_number = None,
                      password = '1234'
                 )
            self.assertEqual(str(context.exception), 'phone number is required')

    
    def test_create_superuser_success(self):
        super_user = User.objects.create_superuser(
            username = self.data['username'],
            phone_number = self.data['phone_number'],
            password = self.data['password']
        )

        self.assertEqual(super_user.username, self.data['username'])
        self.assertEqual(super_user.phone_number, self.data['phone_number'])
        self.assertTrue(super_user.check_password(self.data['password']))
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_admin)        


    def test_missing_username_speruser(self):
        
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                username = None,
                phone_number = self.data['username'],
                password = self.data['password']
            )
        self.assertEqual(str(context.exception), 'user name is required')


    def test_missing_phone_number_superuser(self):
            with self.assertRaises(ValueError) as context:
                 User.objects.create_superuser(
                      username = self.data['username'],
                      phone_number = None,
                      password = '1234'
                 )
            self.assertEqual(str(context.exception), 'phone number is required')

 