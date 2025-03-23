from accounts.models import User
from django.test import TestCase



class TestUserModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='0123456789',
            password='1234'
        )

    def test_user_register(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.phone_number, '0123456789')

    def test_trring_user(self):
        self.assertEqual(str(self.user), 'testuser-0123456789-1')


