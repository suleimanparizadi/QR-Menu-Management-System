from django.test import TestCase
from accounts.serializer import UserSerializer


class TestUserSerializer(TestCase):

    def setUp(self):
        self.valid_data = {
            'username':'testuser',
            'phone_number':'0123456789',
            'password':'1234',
            'password2':'1234',
        }
        self.invalid_data = {
            'username':None,
            'phone_number':'09999999999999',
            'password':'1234',
            'password2':'4321',
        }


    def test_success_serialize(self):
        serz_data = UserSerializer(data=self.valid_data)
        self.assertTrue(serz_data.is_valid())
        self.assertEqual(serz_data.validated_data['username'], 'testuser')
        self.assertEqual(serz_data.validated_data['phone_number'], '0123456789')
        self.assertNotIn('password2', serz_data.validated_data)


    def test_fail_serialize(self):
        serz_data = UserSerializer(data=self.invalid_data)
        self.assertFalse(serz_data.is_valid())
